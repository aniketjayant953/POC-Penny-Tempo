import { formatTimeRange } from '../lib/format'
import type { Booking } from '../types'

export const PROGRAMME_STYLES: Record<string, { bg: string; border: string; text: string; sub: string }> = {
  'Executive Outplacement': { bg: '#eef2ff', border: '#6366f1', text: '#312e81', sub: '#4f46e5' },
  'Professional Outplacement': { bg: '#ecfdf5', border: '#10b981', text: '#064e3b', sub: '#047857' },
  'Career Transition Essentials': { bg: '#fff7ed', border: '#f59e0b', text: '#7c2d12', sub: '#b45309' },
  'Career Options and Planning': { bg: '#eef2ff', border: '#6366f1', text: '#312e81', sub: '#4f46e5' },
  'Interview Preparation': { bg: '#ecfdf5', border: '#10b981', text: '#064e3b', sub: '#047857' },
  'LinkedIn Profile': { bg: '#fff7ed', border: '#f59e0b', text: '#7c2d12', sub: '#b45309' },
  'CV and Applications': { bg: '#f5f3ff', border: '#8b5cf6', text: '#4c1d95', sub: '#6d28d9' },
}

const FALLBACK = { bg: '#f1f5f9', border: '#94a3b8', text: '#1e293b', sub: '#475569' }

export function programmeStyle(programme: string) {
  return PROGRAMME_STYLES[programme] ?? FALLBACK
}

interface CalendarEventProps {
  booking: Booking
  selected: boolean
}

export function CalendarEvent({ booking, selected }: CalendarEventProps) {
  const s = programmeStyle(booking.programme)
  const compact = booking.duration_minutes <= 30
  return (
    <div
      className="h-full w-full overflow-hidden rounded-md px-2 py-1 transition-shadow"
      style={{
        background: selected ? s.border : s.bg,
        borderLeft: `3px solid ${s.border}`,
        color: selected ? '#fff' : s.text,
        opacity: booking.is_past && !selected ? 0.65 : 1,
        boxShadow: selected ? '0 4px 12px rgba(79,70,229,0.35)' : 'none',
      }}
    >
      {compact ? (
        <div className="flex items-center gap-1.5 truncate text-[11px] leading-tight">
          <span className="truncate font-semibold">{booking.candidate_name}</span>
          <span className="shrink-0 opacity-75">{formatTimeRange(booking.start_time, booking.end_time).split(' – ')[0]}</span>
        </div>
      ) : (
        <>
          <p className="truncate text-[12px] font-semibold leading-tight">{booking.candidate_name}</p>
          <p className="truncate text-[11px] leading-tight" style={{ color: selected ? 'rgba(255,255,255,0.85)' : s.sub }}>
            {formatTimeRange(booking.start_time, booking.end_time)}
          </p>
          {booking.duration_minutes >= 45 && (
            <p className="mt-0.5 truncate text-[11px] leading-tight" style={{ opacity: 0.8 }}>
              {booking.programme}
            </p>
          )}
        </>
      )}
    </div>
  )
}
