import type { LucideIcon } from 'lucide-react'
import { Card, Skeleton, cn } from './ui'

interface KpiCardProps {
  label: string
  value?: string | number
  hint?: string
  icon: LucideIcon
  loading?: boolean
  tone?: 'indigo' | 'sky' | 'violet' | 'emerald'
}

const TONE = {
  indigo: { wrap: 'from-indigo-50 to-white', icon: 'bg-indigo-600 text-white', bar: 'bg-indigo-500' },
  sky: { wrap: 'from-sky-50 to-white', icon: 'bg-sky-600 text-white', bar: 'bg-sky-500' },
  violet: { wrap: 'from-violet-50 to-white', icon: 'bg-violet-600 text-white', bar: 'bg-violet-500' },
  emerald: { wrap: 'from-emerald-50 to-white', icon: 'bg-emerald-600 text-white', bar: 'bg-emerald-500' },
}

export function KpiCard({ label, value, hint, icon: Icon, loading, tone = 'indigo' }: KpiCardProps) {
  const t = TONE[tone]
  return (
    <Card className={cn('relative overflow-hidden bg-gradient-to-br p-5', t.wrap)}>
      <span className={cn('absolute inset-y-0 left-0 w-1', t.bar)} />
      <div className="flex items-start justify-between pl-1">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">{label}</p>
        <span className={cn('flex h-9 w-9 items-center justify-center rounded-xl shadow-sm', t.icon)}>
          <Icon size={16} />
        </span>
      </div>
      {loading ? (
        <>
          <Skeleton className="mt-3 h-8 w-20" />
          <Skeleton className="mt-2 h-3 w-32" />
        </>
      ) : (
        <>
          <p className="mt-2 pl-1 text-3xl font-semibold tracking-tight text-slate-900">{value ?? '—'}</p>
          {hint && <p className="mt-1 truncate pl-1 text-xs text-slate-500">{hint}</p>}
        </>
      )}
    </Card>
  )
}
