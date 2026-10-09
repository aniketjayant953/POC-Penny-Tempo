import type { ReactNode } from 'react'

interface TopHeaderProps {
  title: string
  subtitle: string
  actions?: ReactNode
}

export function TopHeader({ title, subtitle, actions }: TopHeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white/85 px-8 py-5 backdrop-blur">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-slate-900">{title}</h1>
        <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>
      </div>
      <div className="flex items-center gap-3">
        {actions}
        <span className="hidden rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-[11px] font-medium text-amber-700 lg:inline-block">
          POC • Historical / Dummy Data
        </span>
      </div>
    </header>
  )
}
