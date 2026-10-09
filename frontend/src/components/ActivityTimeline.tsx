import { Activity, ActivitySquare } from 'lucide-react'
import { useState } from 'react'
import { formatShortDate, titleCase } from '../lib/format'
import type { CandidateActivity } from '../types'
import { StatusBadge } from './StatusBadge'
import { cn, EmptyState, SectionCard } from './ui'

interface ActivityTimelineProps {
  sinceMeeting: CandidateActivity[]
  all: CandidateActivity[]
  hasPreviousMeeting: boolean
}

export function ActivityTimeline({ sinceMeeting, all, hasPreviousMeeting }: ActivityTimelineProps) {
  const [mode, setMode] = useState<'since' | 'all'>(hasPreviousMeeting ? 'since' : 'all')
  const items = mode === 'since' ? sinceMeeting : all

  const toggle = hasPreviousMeeting && (
    <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs font-medium">
      {(
        [
          ['since', 'Since last meeting'],
          ['all', 'All activity'],
        ] as const
      ).map(([key, label]) => (
        <button
          key={key}
          onClick={() => setMode(key)}
          className={cn(
            'rounded-md px-3 py-1.5 transition-colors',
            mode === key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700',
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )

  return (
    <SectionCard title="Candidate Activity" subtitle="Learning and programme activity" icon={Activity} action={toggle}>
      {items.length === 0 ? (
        <EmptyState
          compact
          icon={ActivitySquare}
          title="No candidate activity found."
          description={mode === 'since' ? 'Nothing recorded since the previous meeting.' : undefined}
        />
      ) : (
        <ol className="relative ml-2 border-l border-slate-200">
          {items.map((a) => (
            <li key={a.activity_id} className="relative mb-4 flex items-center justify-between gap-4 pl-6 last:mb-0">
              <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-slate-300 ring-1 ring-slate-200" />
              <div className="flex items-baseline gap-4">
                <span className="w-14 shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  {formatShortDate(a.scheduled_date)}
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-800">{a.activity_name}</p>
                  <p className="text-xs text-slate-500">
                    {titleCase(a.activity_type)} · {a.duration_minutes} min
                  </p>
                </div>
              </div>
              <StatusBadge status={a.status} />
            </li>
          ))}
        </ol>
      )}
    </SectionCard>
  )
}
