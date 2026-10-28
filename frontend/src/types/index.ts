export interface Coach {
  coach_id: string
  coach_name: string
  region?: string
  working_hours_per_week: number
  working_days: string
  timezone: string
}

export interface Candidate {
  candidate_id: string
  candidate_name: string
  programme: string
  status: string
  assigned_coach_id: string
  assigned_coach_name?: string | null
}

export interface Booking {
  booking_id: string
  candidate_id: string
  candidate_name: string
  coach_id: string
  coach_name: string | null
  session_date: string
  start_time: string
  end_time: string
  duration_minutes: number
  programme: string
  candidate_status: string
  status: string
  is_today: boolean
  is_past: boolean
}

export interface UpcomingBookings {
  today: string
  events: Booking[]
  kpis: {
    upcoming_sessions: number
    todays_sessions: number
    preparation_ready: number
  }
}

export type ActivityStatus = 'attended' | 'booked' | 'not_attended' | 'cancelled' | string

export interface CandidateActivity {
  activity_id: string
  candidate_id: string
  activity_name: string
  activity_type: string
  scheduled_date: string
  completion_date: string | null
  status: ActivityStatus
  duration_minutes: number
}

export interface MeetingNote {
  meeting_date: string
  notes: string
  agreed_actions: string[]
}

export type ActionEvidence = 'attended' | 'booked' | 'not_attended' | 'cancelled' | 'not_found' | 'unknown'

export interface ActionResult {
  action: string
  status: 'activity_found' | 'not_found'
  activity: string | null
  evidence: ActionEvidence
  matched_activities: { activity_id: string; activity_name: string; status: string; scheduled_date: string | null }[]
}

export interface MeetingInfo {
  booking_id: string
  coach_id: string
  coach_name: string | null
  session_date: string
  start_time: string
  end_time: string
  duration_minutes: number
  status: string
}

export interface CandidateSnapshotData {
  programme: string
  status: string
  assigned_coach: string | null
  previous_meeting_date: string | null
  next_meeting_date: string
  total_activities: number
  attended_activities: number
  window_activities: number
}

export interface CandidatePreparation {
  candidate: Candidate
  meeting: MeetingInfo
  previous_meeting_found: boolean
  previous_meeting: MeetingNote | null
  action_results: ActionResult[]
  activities: CandidateActivity[]
  all_activities: CandidateActivity[]
  insights: string[]
  snapshot: CandidateSnapshotData
}

export interface CandidateBrief {
  candidate_id: string
  booking_id: string
  bullets: string[]
  generated_at: string
  cached: boolean
}

export type UtilizationLevel = 'high' | 'moderate' | 'low'

export interface CoachUtilizationRow {
  coach_id: string
  coach_name: string
  region?: string
  working_hours_per_week: number
  weeks: number
  capacity_hours: number
  eligible_hours: number
  utilization_pct: number
  level: UtilizationLevel
  completed_sessions: number
  booked_sessions: number
  cancelled_sessions: number
}

export interface UtilizationTrendPoint {
  week_start: string
  avg_utilization_pct: number
  booked_hours: number
  phase: 'historical' | 'current' | 'forward'
}

export interface UtilizationRecord {
  coach_id: string
  week_start: string
  working_hours: number
  booked_hours: number
  utilization_pct: number
}

export interface UtilizationResponse {
  weeks: string[]
  thresholds: { high: number; moderate: number }
  coaches: CoachUtilizationRow[]
  trend: UtilizationTrendPoint[]
  weekly: UtilizationRecord[]
}

export interface ManagerInsight {
  kind: 'positive' | 'attention' | 'neutral'
  title: string
  text: string
}

export interface UtilizationSummary {
  has_data: boolean
  kpis: {
    total_coaches: number
    average_utilization_pct: number
    total_coaching_hours: number
    cancelled_sessions: number
    highest: { coach_name: string; utilization_pct: number }
    lowest: { coach_name: string; utilization_pct: number }
  } | null
  insights: ManagerInsight[]
}

export interface UtilizationFilters {
  coach_id?: string
  start?: string
  end?: string
  region?: string
}

export interface UtilizationMeta {
  weeks: string[]
  regions: string[]
  default_start: string
  default_end: string
  default_region: string
  thresholds: { high: number; moderate: number }
  source: string
}
