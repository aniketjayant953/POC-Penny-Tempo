import { History, MessageSquareOff } from 'lucide-react'
import { formatDate } from '../lib/format'
import type { MeetingNote } from '../types'
import { EmptyState, SectionCard } from './ui'

export function PreviousMeetingCard({ meeting }: { meeting: MeetingNote | null }) {
  return (
    <SectionCard title="Previous Meeting" subtitle="Most recent session notes" icon={History} className="h-full">
      {meeting ? (
        <div>
          <p className="mb-3 inline-flex rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            {formatDate(meeting.meeting_date)}
          </p>
          <p className="text-sm leading-relaxed text-slate-700">{meeting.notes}</p>
        </div>
      ) : (
        <EmptyState compact icon={MessageSquareOff} title="No previous meeting available." />
      )}
    </SectionCard>
  )
}
