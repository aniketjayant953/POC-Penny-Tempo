import type { LucideIcon } from 'lucide-react'
import { Card, Skeleton } from './ui'

interface KpiCardProps {
  label: string
  value?: string | number
  hint?: string
  icon: LucideIcon
  loading?: boolean
}

export function KpiCard({ label, value, hint, icon: Icon, loading }: KpiCardProps) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
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
          <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{value ?? '—'}</p>
          {hint && <p className="mt-1 truncate text-xs text-slate-500">{hint}</p>}
        </>
      )}
    </Card>
  )
}
