import { BarChart3, CalendarDays, Database } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { cn } from './ui'

const NAV = [
  { to: '/coach', label: 'Coach calendar', icon: CalendarDays },
  { to: '/manager', label: 'Manager view', icon: BarChart3 },
]

export function TempoMark({ size = 36 }: { size?: number }) {
  return (
    <span
      style={{ width: size, height: size }}
      className="flex items-center justify-center rounded-[11px] bg-gradient-to-br from-indigo-400 via-indigo-600 to-violet-700 shadow-[0_8px_18px_rgba(79,70,229,0.35)]"
    >
      <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 32 32" fill="none">
        <path d="M5 17h5l3.5-9 5 15 3.5-7h5" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  )
}

export function Sidebar() {
  return (
    <>
      <aside className="hidden w-[248px] shrink-0 flex-col border-r border-white/10 bg-[#0f172a] text-slate-300 md:flex">
        <div className="flex items-center gap-3 px-5 py-6">
          <TempoMark />
          <div className="leading-tight">
            <p className="text-[15px] font-bold tracking-[0.2em] text-white">TEMPO</p>
            <p className="text-[11px] text-slate-400">AI Coaching Intelligence</p>
          </div>
        </div>

        <nav className="mt-2 flex flex-col gap-1 px-3">
          <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">Workspace</p>
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:bg-white/5 hover:text-white',
                )
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto p-4">
          <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-[11px] text-slate-400">
            <Database size={13} className="shrink-0 text-indigo-300" />
            Live demo · sample data
          </div>
        </div>
      </aside>

      <div className="sticky top-0 z-30 flex items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:hidden">
        <TempoMark size={28} />
        <p className="text-sm font-bold tracking-[0.16em] text-slate-900">TEMPO</p>
        <nav className="ml-auto flex gap-1">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium',
                  isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-500',
                )
              }
            >
              <Icon size={14} />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </>
  )
}
