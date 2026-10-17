import type { ReactNode } from 'react'

interface TopHeaderProps {
  title: string
  subtitle: string
  actions?: ReactNode
}

export function TopHeader({ title, subtitle, actions }: TopHeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200/80 bg-white/80 px-5 py-4 backdrop-blur-md md:px-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-slate-900">{title}</h1>
        <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        {actions}
        <span className="hidden rounded-full bg-slate-900 px-3 py-1 text-[11px] font-medium text-white/90 lg:inline-block">
          Demo data
        </span>
      </div>
    </header>
  )
}
