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
    <Card className="tempo-cal overflow-hidden p-4">
      <div className="mb-3 flex flex-wrap items-center gap-x-5 gap-y-1 px-1 text-[11px] text-slate-500">
        {Object.entries(PROGRAMME_STYLES).map(([name, s]) => (
          <span key={name} className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: s.border }} />
            {name}
          </span>
        ))}
      </div>
      <FullCalendar
        plugins={[timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        initialDate={today ?? undefined}
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
