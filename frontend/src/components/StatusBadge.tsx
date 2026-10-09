import { cn } from './ui'
import { titleCase } from '../lib/format'

type Tone = 'green' | 'blue' | 'amber' | 'slate' | 'red' | 'indigo'

const TONES: Record<Tone, string> = {
  green: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  blue: 'bg-sky-50 text-sky-700 ring-sky-600/15',
  amber: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  slate: 'bg-slate-100 text-slate-600 ring-slate-500/15',
  red: 'bg-rose-50 text-rose-700 ring-rose-600/15',
  indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-600/15',
}

const DOTS: Record<Tone, string> = {
  green: 'bg-emerald-500',
  blue: 'bg-sky-500',
  amber: 'bg-amber-500',
  slate: 'bg-slate-400',
  red: 'bg-rose-500',
  indigo: 'bg-indigo-500',
}

const STATUS_MAP: Record<string, { tone: Tone; label?: string }> = {
  // activities
  attended: { tone: 'green', label: 'Attended' },
  booked: { tone: 'blue', label: 'Booked' },
  not_attended: { tone: 'amber', label: 'Not Attended' },
  cancelled: { tone: 'slate', label: 'Cancelled' },
  completed: { tone: 'green', label: 'Completed' },
  // candidate
  active: { tone: 'green', label: 'Active' },
  'on hold': { tone: 'amber', label: 'On Hold' },
  onboarding: { tone: 'indigo', label: 'Onboarding' },
  withdrawn: { tone: 'red', label: 'Withdrawn' },
  // utilization
  high: { tone: 'green', label: 'High' },
  moderate: { tone: 'amber', label: 'Moderate' },
  low: { tone: 'red', label: 'Low' },
}

export function StatusBadge({ status, label, className }: { status: string; label?: string; className?: string }) {
  const entry = STATUS_MAP[status.toLowerCase()] ?? { tone: 'slate' as Tone }
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ring-inset',
        TONES[entry.tone],
        className,
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', DOTS[entry.tone])} />
      {label ?? entry.label ?? titleCase(status)}
    </span>
  )
}
