import { BarChart3, Clock, Gauge, Users, XCircle } from 'lucide-react'
import { useState } from 'react'
import { CoachUtilizationTable } from '../components/CoachUtilizationTable'
import { KpiCard } from '../components/KpiCard'
import { ManagerInsightCard } from '../components/ManagerInsightCard'
import { TopHeader } from '../components/TopHeader'
import { UtilizationChart } from '../components/UtilizationChart'
import { UtilizationTrend } from '../components/UtilizationTrend'
import { Card, EmptyState, ErrorState, Skeleton } from '../components/ui'
import { formatShortDate } from '../lib/format'
import { useAsync } from '../lib/useAsync'
import { api } from '../services/api'
import type { UtilizationFilters } from '../types'

const selectCls =
  'rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 shadow-sm outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100'

export default function ManagerPage() {
  const [coachId, setCoachId] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')

  const filters: UtilizationFilters = {
    coach_id: coachId || undefined,
    start: start || undefined,
    end: end || undefined,
  }
  const key = JSON.stringify(filters)

  const coaches = useAsync(() => api.coaches(), 'coaches')
  const util = useAsync(() => api.utilization(filters), `util:${key}`)
  const summary = useAsync(() => api.utilizationSummary(filters), `summary:${key}`)
  // Unfiltered list of weeks for the date-range selectors.
  const allWeeks = useAsync(() => api.utilization({}), 'weeks')

  const weeks = allWeeks.data?.weeks ?? []
  const error = util.error ?? summary.error
  const loading = util.loading || summary.loading
  const kpis = summary.data?.kpis
  const hasData = summary.data?.has_data ?? false

  const filtersUi = (
    <div className="flex flex-wrap items-center gap-2">
      <select className={selectCls} value={coachId} onChange={(e) => setCoachId(e.target.value)} aria-label="Coach">
        <option value="">All coaches</option>
        {(coaches.data ?? []).map((c) => (
          <option key={c.coach_id} value={c.coach_id}>
            {c.coach_name}
          </option>
        ))}
      </select>
      <select
        className={selectCls}
        value={start}
        aria-label="From week"
        onChange={(e) => {
          setStart(e.target.value)
          if (end && e.target.value && e.target.value > end) setEnd(e.target.value)
        }}
      >
        <option value="">From: first week</option>
        {weeks.map((w) => (
          <option key={w} value={w}>
            From: {formatShortDate(w)}
          </option>
        ))}
      </select>
      <select
        className={selectCls}
        value={end}
        aria-label="To week"
        onChange={(e) => {
          setEnd(e.target.value)
          if (start && e.target.value && e.target.value < start) setStart(e.target.value)
        }}
      >
        <option value="">To: last week</option>
        {weeks.map((w) => (
          <option key={w} value={w}>
            To: {formatShortDate(w)}
          </option>
        ))}
      </select>
      {(coachId || start || end) && (
        <button
          onClick={() => {
            setCoachId('')
            setStart('')
            setEnd('')
          }}
          className="px-2 text-xs font-medium text-indigo-600 hover:text-indigo-800"
        >
          Reset
        </button>
      )}
    </div>
  )

  return (
    <>
      <TopHeader title="Manager Intelligence" subtitle="Coach utilization and capacity overview" actions={filtersUi} />
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 p-8">
        {error ? (
          <Card>
            <ErrorState
              title={error.unreachable ? 'Tempo backend is unavailable.' : "We couldn't load utilization data."}
              description="Check that the Tempo API is running, then try again."
              onRetry={() => {
                util.reload()
                summary.reload()
              }}
            />
          </Card>
        ) : !loading && !hasData ? (
          <Card>
            <EmptyState
              icon={BarChart3}
              title="No utilization data"
              description="There is no booking data for the selected filters. Try widening the date range."
            />
          </Card>
        ) : (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <KpiCard label="Total Coaches" icon={Users} value={kpis?.total_coaches} hint="In current selection" loading={loading} />
              <KpiCard
                label="Average Utilization"
                icon={Gauge}
                value={kpis ? `${kpis.average_utilization_pct.toFixed(1)}%` : undefined}
                hint={kpis && kpis.total_coaches > 1 ? `High ${kpis.highest.utilization_pct}% · Low ${kpis.lowest.utilization_pct}%` : 'Eligible hours ÷ working hours'}
                loading={loading}
              />
              <KpiCard
                label="Total Coaching Hours"
                icon={Clock}
                value={kpis ? kpis.total_coaching_hours.toLocaleString() : undefined}
                hint="Completed + booked sessions"
                loading={loading}
              />
              <KpiCard
                label="Cancelled Sessions"
                icon={XCircle}
                value={kpis?.cancelled_sessions}
                hint="Excluded from utilization"
                loading={loading}
              />
            </section>

            {loading && !util.data ? (
              <div className="grid gap-6 xl:grid-cols-2">
                <Skeleton className="h-96" />
                <Skeleton className="h-96" />
              </div>
            ) : (
              <>
                <div className="grid gap-6 xl:grid-cols-2">
                  <UtilizationChart rows={util.data?.coaches ?? []} average={kpis?.average_utilization_pct ?? null} />
                  <UtilizationTrend points={util.data?.trend ?? []} />
                </div>
                <ManagerInsightCard insights={summary.data?.insights ?? []} />
                <CoachUtilizationTable rows={util.data?.coaches ?? []} thresholds={util.data?.thresholds ?? null} />
              </>
            )}
          </>
        )}
      </div>
    </>
  )
}
