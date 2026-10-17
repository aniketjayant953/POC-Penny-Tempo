import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { EventInput } from '@fullcalendar/core'
import { CalendarX2 } from 'lucide-react'
import { useMemo } from 'react'
import type { Booking } from '../types'
import { CalendarEvent, PROGRAMME_STYLES } from './CalendarEvent'
import { Card, EmptyState, Skeleton } from './ui'

interface CalendarViewProps {
  bookings: Booking[] | null
  loading: boolean
  today: string | null
  selectedId: string | null
  onSelect: (booking: Booking) => void
}

export function CalendarView({ bookings, loading, today, selectedId, onSelect }: CalendarViewProps) {
  const byId = useMemo(() => new Map((bookings ?? []).map((b) => [b.booking_id, b])), [bookings])

  const events: EventInput[] = useMemo(
    () =>
      (bookings ?? []).map((b) => ({
        id: b.booking_id,
        title: b.candidate_name,
        start: `${b.session_date}T${b.start_time}:00`,
        end: `${b.session_date}T${b.end_time}:00`,
        backgroundColor: 'transparent',
        borderColor: 'transparent',
      })),
    [bookings],
  )

  const focusDate = useMemo(() => {
    const upcoming = (bookings ?? []).filter((b) => !b.is_past).sort((a, b) => a.session_date.localeCompare(b.session_date))
    if (upcoming[0]) return upcoming[0].session_date
    const latest = [...(bookings ?? [])].sort((a, b) => b.session_date.localeCompare(a.session_date))[0]
    return latest?.session_date ?? today ?? undefined
  }, [bookings, today])

  if (loading && !bookings) {
    return (
      <Card className="p-6">
        <p className="mb-4 text-sm text-slate-500">Loading upcoming sessions...</p>
        <div className="grid grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-72" />
          ))}
        </div>
      </Card>
    )
  }

  if (bookings && bookings.length === 0) {
    return (
      <Card>
        <EmptyState
          icon={CalendarX2}
          title="No upcoming meetings"
          description="This coach has no booked candidate sessions. Choose another coach to preview their calendar."
        />
      </Card>
    )
  }

  return (
    <Card className="tempo-cal overflow-hidden p-4 md:p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 px-1">
        <div>
          <p className="text-sm font-semibold text-slate-900">Week calendar</p>
          <p className="text-xs text-slate-500">Click a session to open AI candidate preparation</p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          {Object.entries(PROGRAMME_STYLES).map(([name, s]) => (
            <span
              key={name}
              className="inline-flex items-center gap-1.5 rounded-full bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200/80"
            >
              <span className="h-2 w-2 rounded-full" style={{ background: s.border }} />
              {name}
            </span>
          ))}
        </div>
      </div>
      <FullCalendar
        plugins={[timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        initialDate={focusDate}
        headerToolbar={{ left: 'title', right: 'today prev,next' }}
        weekends={false}
        allDaySlot={false}
        nowIndicator
        slotMinTime="09:00:00"
        slotMaxTime="17:30:00"
        slotDuration="00:30:00"
        slotLabelInterval="01:00:00"
        slotLabelFormat={{ hour: 'numeric', minute: '2-digit', hour12: true }}
        height="auto"
        eventOverlap={false}
        slotEventOverlap={false}
        events={events}
        dayHeaderContent={(arg) => (
          <div className="tempo-day-head">
            <span className="tempo-day-name">{arg.date.toLocaleDateString('en-GB', { weekday: 'long' })}</span>
            <span className="tempo-day-num">{arg.date.getDate()}</span>
          </div>
        )}
        eventContent={(arg) => {
          const booking = byId.get(arg.event.id)
          if (!booking) return null
          return <CalendarEvent booking={booking} selected={booking.booking_id === selectedId} />
        }}
        eventClick={(info) => {
          const booking = byId.get(info.event.id)
          if (booking) onSelect(booking)
        }}
      />
    </Card>
  )
}
