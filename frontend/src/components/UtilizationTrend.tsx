import { TrendingUp } from 'lucide-react'
import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatShortDate } from '../lib/format'
import type { UtilizationTrendPoint } from '../types'
import { EmptyState, SectionCard } from './ui'

export function UtilizationTrend({ points }: { points: UtilizationTrendPoint[] }) {
  const data = points.map((p) => ({ ...p, label: formatShortDate(p.week_start) }))
  const forward = data.filter((d) => d.phase === 'forward')
  const max = Math.max(...data.map((d) => d.avg_utilization_pct), 1)

  return (
    <SectionCard
      title="Weekly Utilization Trend"
      subtitle="Average utilization % by week (week starting Monday)"
      icon={TrendingUp}
    >
      {data.length === 0 ? (
        <EmptyState compact icon={TrendingUp} title="No weekly data available" />
      ) : (
        <>
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 12, right: 16, left: -8, bottom: 0 }}>
                <CartesianGrid stroke="#eef0f4" vertical={false} />
                {forward.length > 0 && (
                  <ReferenceArea
                    x1={forward[0].label}
                    x2={forward[forward.length - 1].label}
                    fill="#eef2ff"
                    fillOpacity={0.7}
                    label={{ value: 'Forward bookings', position: 'insideTop', fontSize: 10, fill: '#6366f1' }}
                  />
                )}
                <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(v) => `${v}%`}
                  domain={[0, Math.ceil(max * 1.3)]}
                />
                <Tooltip
                  formatter={(v) => [`${Number(v).toFixed(1)}%`, 'Avg utilization']}
                  labelFormatter={(l) => `Week of ${l}`}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e2e8f0', fontSize: 12, boxShadow: 'none' }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_utilization_pct"
                  stroke="#4f46e5"
                  strokeWidth={2.5}
                  isAnimationActive={false}
                  dot={{ r: 4, fill: '#fff', stroke: '#4f46e5', strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {data.length === 1 && (
            <p className="mt-2 text-xs text-slate-500">Only one week of data is available for the current selection.</p>
          )}
        </>
      )}
    </SectionCard>
  )
}
