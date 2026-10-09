import { Table2 } from 'lucide-react'
import type { CoachUtilizationRow } from '../types'
import { StatusBadge } from './StatusBadge'
import { EmptyState, SectionCard } from './ui'

interface Props {
  rows: CoachUtilizationRow[]
  thresholds: { high: number; moderate: number } | null
}

const th = 'px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wide text-slate-500'
const thR = `${th} text-right`

export function CoachUtilizationTable({ rows, thresholds }: Props) {
  return (
    <SectionCard
      title="Coach Breakdown"
      subtitle={
        thresholds
          ? `POC thresholds: High ≥ ${thresholds.high}% · Moderate ≥ ${thresholds.moderate}% · Low < ${thresholds.moderate}%`
          : undefined
      }
      icon={Table2}
    >
      {rows.length === 0 ? (
        <EmptyState compact icon={Table2} title="No coaches to display" />
      ) : (
        <div className="-mx-2 overflow-x-auto">
          <table className="w-full min-w-[820px] text-sm">
            <thead className="border-b border-slate-200 bg-slate-50/70">
              <tr>
                <th className={th}>Coach</th>
                <th className={thR}>Working Hrs / Wk</th>
                <th className={thR}>Booked / Eligible Hrs</th>
                <th className={th}>Utilization</th>
                <th className={thR}>Completed</th>
                <th className={thR}>Booked</th>
                <th className={thR}>Cancelled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((r) => (
                <tr key={r.coach_id} className="hover:bg-slate-50/60">
                  <td className="whitespace-nowrap px-4 py-3">
                    <p className="font-medium text-slate-900">{r.coach_name}</p>
                    <p className="text-xs text-slate-400">{r.coach_id}</p>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">{r.working_hours_per_week}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">
                    {r.eligible_hours.toFixed(2)}{' '}
                    <span className="text-slate-400">/ {r.capacity_hours.toFixed(0)}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="w-12 font-semibold tabular-nums text-slate-900">{r.utilization_pct.toFixed(1)}%</span>
                      <StatusBadge status={r.level} />
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">{r.completed_sessions}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">{r.booked_sessions}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">{r.cancelled_sessions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </SectionCard>
  )
}
