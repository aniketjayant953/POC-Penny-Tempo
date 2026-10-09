import { CheckCircle2, Circle, CircleDashed, ClipboardList, Clock3, XCircle } from 'lucide-react'
import type { ReactNode } from 'react'
import type { ActionEvidence, ActionResult } from '../types'
import { EmptyState, SectionCard } from './ui'

interface Display {
  icon: ReactNode
  label: string
  tone: string
}

function describe(evidence: ActionEvidence, hasActivities: boolean): Display {
  switch (evidence) {
    case 'attended':
      return { icon: <CheckCircle2 size={18} className="text-emerald-500" />, label: 'Completed — matching activity attended', tone: 'text-emerald-700' }
    case 'booked':
      return { icon: <Clock3 size={18} className="text-sky-500" />, label: 'Matching activity booked, not yet attended', tone: 'text-sky-700' }
    case 'not_attended':
      return { icon: <XCircle size={18} className="text-amber-500" />, label: 'Matching activity not attended', tone: 'text-amber-700' }
    case 'cancelled':
      return { icon: <XCircle size={18} className="text-slate-400" />, label: 'Matching activity cancelled', tone: 'text-slate-600' }
    default:
      return hasActivities
        ? { icon: <Circle size={18} className="text-slate-300" />, label: 'Not found in activity data', tone: 'text-slate-500' }
        : { icon: <CircleDashed size={18} className="text-slate-300" />, label: 'Insufficient activity data', tone: 'text-slate-500' }
  }
}

interface AgreedActionsProps {
  actions: ActionResult[]
  hasPreviousMeeting: boolean
  windowActivityCount: number
}

export function AgreedActions({ actions, hasPreviousMeeting, windowActivityCount }: AgreedActionsProps) {
  return (
    <SectionCard title="Agreed Actions" subtitle="Checked against activity data" icon={ClipboardList} className="h-full">
      {!hasPreviousMeeting ? (
        <EmptyState compact icon={ClipboardList} title="No agreed actions available." description="There is no previous meeting to review." />
      ) : actions.length === 0 ? (
        <EmptyState compact icon={ClipboardList} title="No actions were agreed at the previous meeting." />
      ) : (
        <ul className="flex flex-col gap-2.5">
          {actions.map((a) => {
            const d = describe(a.evidence, windowActivityCount > 0)
            return (
              <li key={a.action} className="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50/60 px-4 py-3">
                <span className="mt-0.5">{d.icon}</span>
                <div>
                  <p className="text-sm font-medium text-slate-800">{a.action}</p>
                  <p className={`text-xs ${d.tone}`}>{d.label}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </SectionCard>
  )
}
