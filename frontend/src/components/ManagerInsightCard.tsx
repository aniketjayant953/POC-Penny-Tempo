import { AlertCircle, Lightbulb, Info, TrendingUp } from 'lucide-react'
import type { ManagerInsight } from '../types'
import { EmptyState, SectionCard } from './ui'

const KIND = {
  positive: { icon: TrendingUp, cls: 'bg-emerald-50 text-emerald-600' },
  attention: { icon: AlertCircle, cls: 'bg-amber-50 text-amber-600' },
  neutral: { icon: Info, cls: 'bg-slate-100 text-slate-500' },
} as const

export function ManagerInsightCard({ insights }: { insights: ManagerInsight[] }) {
  return (
    <SectionCard title="Manager Insights" subtitle="Calculated directly from the data" icon={Lightbulb} className="h-full">
      {insights.length === 0 ? (
        <EmptyState compact icon={Lightbulb} title="No insights available" />
      ) : (
        <ul className="grid gap-x-8 gap-y-4 md:grid-cols-2 xl:grid-cols-3">
          {insights.map((i) => {
            const { icon: Icon, cls } = KIND[i.kind]
            return (
              <li key={i.title} className="flex items-start gap-3">
                <span className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${cls}`}>
                  <Icon size={14} />
                </span>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">{i.title}</p>
                  <p className="text-sm leading-snug text-slate-700">{i.text}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </SectionCard>
  )
}
