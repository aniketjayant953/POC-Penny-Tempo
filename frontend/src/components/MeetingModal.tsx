import { CalendarClock, Clock, Hourglass, Video, X } from 'lucide-react'
import { useEffect } from 'react'
import { formatLongDate, formatTimeRange, initials, titleCase } from '../lib/format'
import type { Booking } from '../types'
import { CandidateWorkspace } from './CandidateWorkspace'
import { StatusBadge } from './StatusBadge'
import { programmeStyle } from './CalendarEvent'

interface MeetingModalProps {
  booking: Booking
  onClose: () => void
}

/** Outlook-style meeting popup rendered over the calendar. */
export function MeetingModal({ booking, onClose }: MeetingModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const accent = programmeStyle(booking.programme).border

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-[2px] md:p-8"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={`Meeting with ${booking.candidate_name}`}
        className="fade-up flex max-h-full w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-slate-50 shadow-2xl ring-1 ring-slate-900/10"
      >
        {/* Meeting metadata (always visible) */}
        <div className="shrink-0 border-b border-slate-200 bg-white" style={{ borderTop: `4px solid ${accent}` }}>
          <div className="flex items-start justify-between gap-4 px-6 pt-5">
            <div className="flex min-w-0 items-center gap-4">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-slate-700 to-slate-900 text-base font-semibold text-white">
                {initials(booking.candidate_name)}
              </span>
              <div className="min-w-0">
                <h2 className="truncate text-xl font-semibold tracking-tight text-slate-900">
                  {booking.candidate_name}
                </h2>
                <p className="truncate text-sm text-slate-500">
                  {booking.candidate_id} · {booking.programme}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close"
              className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            >
              <X size={18} />
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 px-6 pb-5 pt-4">
            <Meta icon={<CalendarClock size={15} />}>{formatLongDate(booking.session_date)}</Meta>
            <Meta icon={<Clock size={15} />}>{formatTimeRange(booking.start_time, booking.end_time)}</Meta>
            <Meta icon={<Hourglass size={15} />}>{booking.duration_minutes} minutes</Meta>
            <span className="flex items-center gap-2 text-sm text-slate-600">
              Meeting
              <StatusBadge status={booking.status} label={titleCase(booking.status)} />
            </span>
            <span className="flex items-center gap-2 text-sm text-slate-600">
              Candidate
              <StatusBadge status={booking.candidate_status} />
            </span>
            <button
              type="button"
              className="ml-auto inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
            >
              <Video size={16} /> Join Meeting
            </button>
          </div>
        </div>

        {/* Candidate insights (only this area scrolls) */}
        <div className="min-h-0 flex-1 overflow-y-auto p-6">
          <CandidateWorkspace booking={booking} />
        </div>
      </div>
    </div>
  )
}

function Meta({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
      <span className="text-slate-400">{icon}</span>
      {children}
    </span>
  )
}
