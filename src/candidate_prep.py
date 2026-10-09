import pandas as pd

from data_loader import load_data

def get_upcoming_sessions(bookings):
    """Return upcoming booked 1:1 sessions"""

    bookings = bookings.copy()

    bookings["session_date"] = pd.to_datetime(bookings["session_date"])

    upcoming = bookings[bookings["status"].str.lower() == "booked"].sort_values("session_date")

    return upcoming

def get_previous_meeting(meeting_notes, coach_id, candidate_id, before_date):
    """ Get the most recent completed meeting before the upcoming session."""

    notes = meeting_notes.copy()

    notes["meeting_date"] = pd.to_datetime(notes["meeting_date"])

    previous = notes[(notes["coach_id"] == coach_id) & (notes["candidate_id"] == candidate_id) & (notes["meeting_date"] < before_date)].sort_values("meeting_date", ascending=False)

    if previous.empty:
        return None

    return previous.iloc[0]

def get_candidate_activities(activities, candidate_id, start_date, end_date):
    """ Get candidate activities between two dates."""
    activities = activities.copy()

    activities["scheduled_date"] = pd.to_datetime(activities["scheduled_date"]) 

    result = activities[(activities["candidate_id"] == candidate_id) & (activities["scheduled_date"] > start_date) & (activities["scheduled_date"] <= end_date)].sort_values("scheduled_date")

    return result

def check_agreed_actions(agreed_actions, activities):
    """ Compare agreed actions from the previous meeting against candidate activities."""

    if pd.isna(agreed_actions) or not str(agreed_actions).strip():
        return []
    
    actions = [action.strip() for action in str(agreed_actions).split(";") if action.strip()]

    insight = []

    activity_names = (activities["activity_name"].dropna().astype(str).str.lower().tolist())

    for action in actions:
        action_lower = action.lower()

        matching_activity = [name for name in activity_names if action_lower in name or name in action_lower]

        if matching_activity:
            insight.append({
                "action": action,
                "status": "activity_found",
                "activity": matching_activity[0]
            })

        else:
            insight.append({
                "action": action,
                "status": "not_found",
                "activity": None
            }) 

    return insight

def prepare_candidate(candidate_id, coach_id, meeting_date, data):

    """Generate structured preparation for one candidate's upcoming 1:1"""

    meeting_date = pd.to_datetime(meeting_date)

    meeting_notes = data["meeting_notes"]   
    activities = data["activities"]

    previous_meeting = get_previous_meeting(meeting_notes, coach_id, candidate_id, meeting_date)

    if previous_meeting is None:
        return {
            "candidate_id": candidate_id,
            "coach_id": coach_id,
            "previous_meeting_found": False,
            "insights": ["No previous meeting found."]
        }

    previous_date = previous_meeting["meeting_date"]

    candidate_activities = get_candidate_activities(activities, candidate_id, previous_date, meeting_date)

    action_results = check_agreed_actions(previous_meeting["agreed_actions"], candidate_activities)

    insights = []

    for result in action_results:

        if result["status"] == "not_found":
            insights.append(f"Candidate may not have completed the agreed action:" f"{result['action']}")

        else:
            insights.append(f"Candidate completed the activity related to :" f"{result['action']}")

    if candidate_activities.empty:
        insights.append("No candidate activity found since the previous meeting.")
    
    return {
        "candidate_id": candidate_id,
        "coach_id": coach_id,
        "previous_meeting_found": True,
        "previous_meeting_date": previous_date,
        "previous_notes": previous_meeting["notes"],
        "agreed_actions": previous_meeting["agreed_actions"],
        "activities": candidate_activities.to_dict("records"),
        "action_results": action_results,
        "insights": insights 
    }

if __name__ == "__main__":
    data = load_data()

    upcoming = get_upcoming_sessions(data["bookings"])

    print(f"Upcoming session found: {len(upcoming)}")

    if not upcoming.empty:

        session = upcoming.iloc[0]

        result = prepare_candidate(
            candidate_id=session["candidate_id"],
            coach_id=session["coach_id"],
            meeting_date=session["session_date"],
            data=data
        )

        print(f"\nCandidate Preparation")
        print("--------------------------")
        for key, value in result.items():
            print(f"\n{key}")
            print(value)