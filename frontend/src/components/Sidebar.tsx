import { BarChart3, CalendarDays, Database } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { cn } from './ui'

const NAV = [
  { to: '/coach', label: 'Calendar / Coach View', icon: CalendarDays },
  { to: '/manager', label: 'Manager View', icon: BarChart3 },
]

export function TempoMark({ size = 36 }: { size?: number }) {
  return (
    <span
      style={{ width: size, height: size }}
      className="flex items-center justify-center rounded-[10px] bg-gradient-to-br from-indigo-500 to-indigo-700 shadow-sm"
    >
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 32 32" fill="none">
        <path d="M5 17h5l3.5-9 5 15 3.5-7h5" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  )
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
      <div className="flex items-center gap-3 px-6 py-6">
        <TempoMark />
        <div className="leading-tight">
          <p className="text-[15px] font-bold tracking-[0.18em] text-slate-900">TEMPO</p>
          <p className="text-[11px] text-slate-500">AI Coaching Intelligence</p>
        </div>
      </div>

      <nav className="mt-2 flex flex-col gap-1 px-3">
        <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-400">Workspace</p>
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto p-4">
        <div className="flex items-center gap-2 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-2.5 text-[11px] text-slate-500">
          <Database size={13} className="shrink-0" />
          POC • Historical Data
        </div>
      </div>
    </aside>
  )
}
