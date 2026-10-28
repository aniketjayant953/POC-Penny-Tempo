import { CalendarCheck, CalendarClock, Sparkles, UserRound } from 'lucide-react'
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

export default function CoachPage() {
  const [coachId, setCoachId] = useState<string>('')
  const [selected, setSelected] = useState<Booking | null>(null)
  const closeModal = useCallback(() => setSelected(null), [])

  const coaches = useAsync(() => api.coaches({ has_sessions: true }), 'coaches')
  const bookings = useAsync(() => api.upcomingBookings(coachId || undefined), `bookings:${coachId}`)

  useEffect(() => {
    setSelected(null)
  }, [coachId])

  // Optional deep link for demos: /coach?coach=<id>&booking=<id>
  const [params] = useSearchParams()
  const deepCoach = params.get('coach')
  const deepBooking = params.get('booking')
  useEffect(() => {
    if (deepCoach) setCoachId(deepCoach)
  }, [deepCoach])
  useEffect(() => {
    if (deepCoach || !coaches.data?.length) return
    if (!coachId || !coaches.data.some((c) => c.coach_id === coachId)) {
      setCoachId(coaches.data[0].coach_id)
    }
  }, [coaches.data, deepCoach, coachId])
  useEffect(() => {
    const match = bookings.data?.events.find((e) => e.booking_id === deepBooking)
    if (match) setSelected(match)
  }, [bookings.data, deepBooking])

  const kpis = bookings.data?.kpis

  const coachSelect = (
    <label className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-500 shadow-sm">
      <UserRound size={15} className="text-indigo-500" />
      Coach
      <select
        value={coachId}
        onChange={(e) => setCoachId(e.target.value)}
        className="tempo-select min-w-[180px] border-0 bg-transparent py-1 text-sm font-semibold text-slate-800 outline-none"
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
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 p-5 md:p-8">
        {coaches.error || bookings.error ? (
          <Card>
            <ErrorState
              title={
                (coaches.error ?? bookings.error)?.unreachable
                  ? 'Tempo backend is unavailable.'
                  : "We couldn't load upcoming sessions."
              }
              description="Check that the Tempo API is running, then try again."
              onRetry={() => {
                coaches.reload()
                bookings.reload()
              }}
            />
          </Card>
        ) : (
          <>
            <section className="grid gap-4 md:grid-cols-3">
              <KpiCard
                label="Booked Sessions"
                icon={CalendarClock}
                value={kpis?.upcoming_sessions}
                hint="Booked 1:1 sessions on this coach calendar"
                loading={bookings.loading || coaches.loading}
                tone="indigo"
              />
              <KpiCard
                label="Today's Sessions"
                icon={CalendarCheck}
                value={kpis?.todays_sessions}
                hint="Scheduled for today"
                loading={bookings.loading || coaches.loading}
                tone="sky"
              />
              <KpiCard
                label="Preparation Ready"
                icon={Sparkles}
                value={kpis?.preparation_ready}
                hint="Sessions Tempo can prepare from notes and activities"
                loading={bookings.loading || coaches.loading}
                tone="violet"
              />
            </section>

            <CalendarView
              bookings={bookings.data?.events ?? null}
              loading={bookings.loading || coaches.loading}
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
