import { useCallback, useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAsync } from '../lib/useAsync'
import type { Booking, CandidateBrief } from '../types'
import { ActivityTimeline } from './ActivityTimeline'
import { AgreedActions } from './AgreedActions'
import { AiBriefCard } from './AiBriefCard'
import { CandidateSnapshot } from './CandidateSnapshot'
import { PreviousMeetingCard } from './PreviousMeetingCard'
import { Card, ErrorState, Skeleton } from './ui'

function WorkspaceSkeleton() {
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="flex flex-col gap-6">
        <Card className="p-6">
          <p className="mb-4 text-sm text-slate-500">Preparing candidate context...</p>
          <Skeleton className="h-14 w-full" />
        </Card>
        <Skeleton className="h-64 w-full" />
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
      <div className="flex flex-col gap-6">
        <Skeleton className="h-60" />
        <Skeleton className="h-72" />
      </div>
    </div>
  )
}

/** Keyed by booking in the parent, so all state resets when a new meeting is selected. */
export function CandidateWorkspace({ booking }: { booking: Booking }) {
  const prep = useAsync(
    () => api.preparation(booking.candidate_id, booking.booking_id),
    `${booking.candidate_id}:${booking.booking_id}`,
  )

  const [brief, setBrief] = useState<CandidateBrief | null>(null)
  const [briefLoading, setBriefLoading] = useState(false)
  const [briefError, setBriefError] = useState<string | null>(null)

  const loadBrief = useCallback(
    (refresh: boolean) => {
      setBriefLoading(true)
      setBriefError(null)
      api
        .brief(booking.candidate_id, booking.booking_id, refresh)
        .then((b) => setBrief(b))
        .catch((e: unknown) => {
          setBrief(null)
          setBriefError(
            e instanceof ApiError && e.unreachable
              ? 'Tempo backend is unavailable.'
              : 'AI preparation is temporarily unavailable.',
          )
        })
        .finally(() => setBriefLoading(false))
    },
    [booking.candidate_id, booking.booking_id],
  )

  // 1) candidate context first, 2) AI brief once context is ready (de-duplicated in api.brief)
  const prepReady = prep.data !== null
  useEffect(() => {
    if (prepReady) loadBrief(false)
  }, [prepReady, loadBrief])

  if (prep.loading) return <WorkspaceSkeleton />

  if (prep.error || !prep.data) {
    return (
      <Card>
        <ErrorState
          title={prep.error?.unreachable ? 'Tempo backend is unavailable.' : "We couldn't prepare this candidate right now."}
          description="Please try again in a moment."
          onRetry={prep.reload}
        />
      </Card>
    )
  }

  const p = prep.data
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="flex min-w-0 flex-col gap-6">
        <AiBriefCard
          brief={brief}
          loading={briefLoading || (!brief && !briefError)}
          error={briefError}
          onRetry={() => loadBrief(true)}
        />
        <div className="grid gap-6 lg:grid-cols-2">
          <PreviousMeetingCard meeting={p.previous_meeting} />
          <AgreedActions
            actions={p.action_results}
            hasPreviousMeeting={p.previous_meeting_found}
            windowActivityCount={p.activities.length}
          />
        </div>
        <ActivityTimeline
          sinceMeeting={p.activities}
          all={p.all_activities}
          hasPreviousMeeting={p.previous_meeting_found}
        />
      </div>
      <div className="flex flex-col gap-6">
        <CandidateSnapshot snapshot={p.snapshot} />
      </div>
    </div>
  )
}
