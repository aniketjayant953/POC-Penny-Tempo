import { CalendarCheck, CalendarClock, Sparkles } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CalendarView } from '../components/CalendarView'
import { KpiCard } from '../components/KpiCard'
import { MeetingModal } from '../components/MeetingModal'
import { TopHeader } from '../components/TopHeader'
import { Card, ErrorState } from '../components/ui'
import { useAsync } from '../lib/useAsync'
import { api } from '../services/api'
import type { Booking } from '../types'

const DEFAULT_COACH = 'CH001'

export default function CoachPage() {
  const [coachId, setCoachId] = useState<string>(DEFAULT_COACH)
  const [selected, setSelected] = useState<Booking | null>(null)
  const closeModal = useCallback(() => setSelected(null), [])

  const coaches = useAsync(() => api.coaches(), 'coaches')
  const bookings = useAsync(() => api.upcomingBookings(coachId), `bookings:${coachId}`)

  useEffect(() => {
    setSelected(null)
  }, [coachId])

  // Optional deep link for demos: /coach?coach=CH001&booking=BK0153
  const [params] = useSearchParams()
  const deepCoach = params.get('coach')
  const deepBooking = params.get('booking')
  useEffect(() => {
    if (deepCoach) setCoachId(deepCoach)
  }, [deepCoach])
  useEffect(() => {
    const match = bookings.data?.events.find((e) => e.booking_id === deepBooking)
    if (match) setSelected(match)
  }, [bookings.data, deepBooking])

  const kpis = bookings.data?.kpis

  const coachSelect = (
    <label className="flex items-center gap-2 text-xs text-slate-500">
      Coach
      <select
        value={coachId}
        onChange={(e) => setCoachId(e.target.value)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 shadow-sm outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100"
      >
        {(coaches.data ?? []).map((c) => (
          <option key={c.coach_id} value={c.coach_id}>
            {c.coach_name}
          </option>
        ))}
        {!coaches.data && <option value={coachId}>Loading…</option>}
      </select>
    </label>
  )

  return (
    <>
      <TopHeader
        title="Coach View"
        subtitle="Your upcoming sessions and AI-powered candidate preparation."
        actions={coachSelect}
      />
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 p-8">
        {bookings.error ? (
          <Card>
            <ErrorState
              title={bookings.error.unreachable ? 'Tempo backend is unavailable.' : "We couldn't load upcoming sessions."}
              description="Check that the Tempo API is running, then try again."
              onRetry={bookings.reload}
            />
          </Card>
        ) : (
          <>
            <section className="grid gap-4 md:grid-cols-3">
              <KpiCard
                label="Upcoming Sessions"
                icon={CalendarClock}
                value={kpis?.upcoming_sessions}
                hint="Booked sessions from today onwards"
                loading={bookings.loading}
              />
              <KpiCard
                label="Today's Sessions"
                icon={CalendarCheck}
                value={kpis?.todays_sessions}
                hint="Scheduled for today"
                loading={bookings.loading}
              />
              <KpiCard
                label="Preparation Ready"
                icon={Sparkles}
                value={kpis?.preparation_ready}
                hint="Sessions Tempo can prepare you for"
                loading={bookings.loading}
              />
            </section>

            <CalendarView
              bookings={bookings.data?.events ?? null}
              loading={bookings.loading}
              today={bookings.data?.today ?? null}
              selectedId={selected?.booking_id ?? null}
              onSelect={setSelected}
            />
          </>
        )}

      </div>

      {selected && <MeetingModal key={selected.booking_id} booking={selected} onClose={closeModal} />}
    </>
  )
}
