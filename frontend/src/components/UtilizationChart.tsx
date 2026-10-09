import { BarChart3 } from 'lucide-react'
import { Bar, BarChart, Cell, LabelList, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { CoachUtilizationRow, UtilizationLevel } from '../types'
import { EmptyState, SectionCard } from './ui'

const COLORS: Record<UtilizationLevel, string> = {
  high: '#4f46e5',
  moderate: '#818cf8',
  low: '#c7d2fe',
}

interface Props {
  rows: CoachUtilizationRow[]
  average: number | null
}

export function UtilizationChart({ rows, average }: Props) {
  const data = [...rows].sort((a, b) => b.utilization_pct - a.utilization_pct)
  const max = Math.max(...data.map((d) => d.utilization_pct), average ?? 0, 1)

  return (
    <SectionCard title="Coach Utilization" subtitle="Eligible session hours ÷ working hours" icon={BarChart3}>
      {data.length === 0 ? (
        <EmptyState compact icon={BarChart3} title="No utilization data" />
      ) : (
        <div style={{ height: data.length * 42 + 30 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 4, right: 48, left: 8, bottom: 0 }} barCategoryGap={10}>
              <XAxis type="number" domain={[0, Math.ceil(max * 1.15)]} hide />
              <YAxis
                type="category"
                dataKey="coach_name"
                width={140}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#475569' }}
              />
              <Tooltip
                cursor={{ fill: '#f6f7f9' }}
                formatter={(v) => [`${Number(v).toFixed(1)}%`, 'Utilization']}
                contentStyle={{ borderRadius: 10, border: '1px solid #e2e8f0', fontSize: 12, boxShadow: 'none' }}
              />
              {average !== null && data.length > 1 && (
                <ReferenceLine
                  x={average}
                  stroke="#94a3b8"
                  strokeDasharray="4 4"
                  label={{ value: `Avg ${average.toFixed(1)}%`, position: 'top', fontSize: 10, fill: '#64748b' }}
                />
              )}
              <Bar dataKey="utilization_pct" radius={[0, 6, 6, 0]} barSize={20} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell key={d.coach_id} fill={COLORS[d.level]} />
                ))}
                <LabelList
                  dataKey="utilization_pct"
                  position="right"
                  formatter={(v) => `${Number(v).toFixed(1)}%`}
                  style={{ fontSize: 12, fontWeight: 600, fill: '#0f172a' }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </SectionCard>
  )
}
