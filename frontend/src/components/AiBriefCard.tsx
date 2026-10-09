import { AlertCircle, RotateCw, Sparkles } from 'lucide-react'
import type { CandidateBrief } from '../types'
interface AiBriefCardProps {
  brief: CandidateBrief | null
  loading: boolean
  error: string | null
  onRetry: () => void
}

export function AiBriefCard({ brief, loading, error, onRetry }: AiBriefCardProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 p-7 text-white shadow-[0_10px_30px_-12px_rgba(49,46,129,0.6)]">
      <div className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-indigo-500/20 blur-3xl" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-200 ring-1 ring-inset ring-indigo-400/30">
            <Sparkles size={18} />
          </span>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-indigo-300">Tempo AI Brief</p>
            <h3 className="text-lg font-semibold">Preparation for your upcoming conversation</h3>
          </div>
        </div>
        {brief && !loading && (
          <button
            onClick={onRetry}
            title="Regenerate brief"
            className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 ring-1 ring-inset ring-white/10 hover:bg-white/5"
          >
            <RotateCw size={12} /> Regenerate
          </button>
        )}
      </div>

      <div className="relative mt-6">
        {loading ? (
          <div>
            <p className="mb-4 flex items-center gap-2 text-sm text-indigo-200">
              <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
              Tempo is preparing your candidate brief...
            </p>
            <div className="flex flex-col gap-3">
              {[92, 78, 85, 64, 88].map((w, i) => (
                <div key={i} className="skeleton-dark h-4" style={{ width: `${w}%` }} />
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="flex items-start gap-3 rounded-xl bg-white/5 p-4 ring-1 ring-inset ring-white/10">
            <AlertCircle size={18} className="mt-0.5 shrink-0 text-amber-300" />
            <div className="flex-1">
              <p className="text-sm font-medium">{error}</p>
              <p className="mt-1 text-xs text-slate-400">
                The candidate context below is still available for your preparation.
              </p>
            </div>
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium hover:bg-white/15"
            >
              <RotateCw size={12} /> Retry
            </button>
          </div>
        ) : brief ? (
          <div className="fade-up">
            <p className="mb-4 text-sm italic text-slate-300">“Here are the key points to consider for this conversation.”</p>
            <ol className="flex flex-col gap-3.5">
              {brief.bullets.map((b, i) => (
                <li key={i} className="flex gap-3.5">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-500/25 text-xs font-semibold text-indigo-200 ring-1 ring-inset ring-indigo-400/30">
                    {i + 1}
                  </span>
                  <p className="text-[14.5px] leading-relaxed text-slate-100">{b}</p>
                </li>
              ))}
            </ol>
            <p className="mt-6 border-t border-white/10 pt-3 text-[11px] text-slate-400">
              Generated from previous meeting notes, agreed actions and candidate activity. Review before use.
            </p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
