import { UserCheck } from 'lucide-react'
import { formatDate } from '../lib/format'
import type { CandidateSnapshotData } from '../types'
import { StatusBadge } from './StatusBadge'
import { SectionCard } from './ui'

export function CandidateSnapshot({ snapshot }: { snapshot: CandidateSnapshotData }) {
  const rows: [string, React.ReactNode][] = [
    ['Programme', snapshot.programme],
    ['Status', <StatusBadge status={snapshot.status} />],
    ['Assigned Coach', snapshot.assigned_coach ?? '—'],
    ['Previous Meeting', snapshot.previous_meeting_date ? formatDate(snapshot.previous_meeting_date) : 'None on record'],
    ['Next Meeting', formatDate(snapshot.next_meeting_date)],
    ['Activities', snapshot.total_activities],
    ['Completed Activities', `${snapshot.attended_activities} of ${snapshot.total_activities}`],
  ]
  return (
    <SectionCard title="Candidate Snapshot" subtitle="Calculated from activity records" icon={UserCheck}>
      <dl className="divide-y divide-slate-100">
        {rows.map(([k, v]) => (
          <div key={k} className="flex items-center justify-between gap-4 py-2.5 text-sm">
            <dt className="text-slate-500">{k}</dt>
            <dd className="text-right font-medium text-slate-800">{v}</dd>
          </div>
        ))}
      </dl>
    </SectionCard>
  )
}
