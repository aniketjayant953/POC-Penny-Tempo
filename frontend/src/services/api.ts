import type {
  CandidateBrief,
  CandidatePreparation,
  Candidate,
  Coach,
  UpcomingBookings,
  UtilizationFilters,
  UtilizationMeta,
  UtilizationResponse,
  UtilizationSummary,
} from '../types'

const BASE_URL: string = import.meta.env.VITE_API_URL ?? ''

export class ApiError extends Error {
  status: number
  /** True when the server could not be reached at all. */
  unreachable: boolean
  constructor(message: string, status: number, unreachable = false) {
    super(message)
    this.status = status
    this.unreachable = unreachable
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}`, init)
  } catch {
    throw new ApiError('Tempo backend is unavailable.', 0, true)
  }
  if (!res.ok) {
    let detail = 'Something went wrong while loading this data.'
    try {
      const body = await res.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(detail, res.status)
  }
  return res.json() as Promise<T>
}

function qs(params: Record<string, string | undefined | boolean>): string {
  const sp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '') sp.set(k, String(v))
  })
  const s = sp.toString()
  return s ? `?${s}` : ''
}

// Cache + in-flight de-duplication so the same data/LLM brief is never requested twice.
const preparationCache = new Map<string, Promise<CandidatePreparation>>()
const briefCache = new Map<string, Promise<CandidateBrief>>()

export const api = {
  health: () => request<{ status: string; today: string }>('/api/health'),
  coaches: (opts?: { region?: string; has_sessions?: boolean }) =>
    request<Coach[]>(`/api/coaches${qs({ region: opts?.region, has_sessions: opts?.has_sessions || undefined })}`),
  candidates: (coachId?: string) => request<Candidate[]>(`/api/candidates${qs({ coach_id: coachId })}`),
  candidate: (id: string) => request<Candidate>(`/api/candidates/${id}`),
  upcomingBookings: (coachId?: string) =>
    request<UpcomingBookings>(`/api/bookings/upcoming${qs({ coach_id: coachId })}`),

  preparation(candidateId: string, bookingId: string): Promise<CandidatePreparation> {
    const key = `${candidateId}:${bookingId}`
    let p = preparationCache.get(key)
    if (!p) {
      p = request<CandidatePreparation>(
        `/api/candidates/${candidateId}/preparation${qs({ booking_id: bookingId })}`,
      )
      p.catch(() => preparationCache.delete(key))
      preparationCache.set(key, p)
    }
    return p
  },

  brief(candidateId: string, bookingId: string, refresh = false): Promise<CandidateBrief> {
    const key = `${candidateId}:${bookingId}`
    if (!refresh) {
      const cached = briefCache.get(key)
      if (cached) return cached
    }
    const p = request<CandidateBrief>(
      `/api/candidates/${candidateId}/brief${qs({ booking_id: bookingId, refresh: refresh || undefined })}`,
      { method: 'POST' },
    )
    p.catch(() => briefCache.delete(key))
    briefCache.set(key, p)
    return p
  },

  utilization: (f: UtilizationFilters) => request<UtilizationResponse>(`/api/utilization${qs({ ...f })}`),
  utilizationSummary: (f: UtilizationFilters) =>
    request<UtilizationSummary>(`/api/utilization/summary${qs({ ...f })}`),
  utilizationMeta: () => request<UtilizationMeta>('/api/utilization/meta'),
}
