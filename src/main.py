from data_loader import load_data
from candidate_prep import (get_upcoming_sessions, prepare_candidate)
from utilization import calculate_weekly_utilization
from llm_summary import generate_candidate_brief

def main():

    # Load all datasets
    data = load_data()

    # ----------------------------
    # 1. Candidate Preparation
    # ----------------------------

    upcoming_sessions = get_upcoming_sessions(data["bookings"])

    print("\n" + "="*60)
    print("Tempo - Candidate Preparation")
    print("=" * 60)

    if upcoming_sessions.empty:
        print("No upcoming sessions found.")

    else:

        # Demonstrate preparation for the upcoming session
        session = upcoming_sessions.iloc[0]

        candidate_result = prepare_candidate(candidate_id=session["candidate_id"], coach_id=session["coach_id"], meeting_date=session["session_date"], data=data)
    
        print(f"\nCandidate: {session['candidate_id']}")
        print(f"Coach: {session['coach_id']}") 
        print(f"Meeting: {session['session_date']}")
        print("\nKey Insights:")

        for insight in candidate_result["insights"]:
            print(f"-{insight}")
        
        print("\nClaude Coach Brief")
        print("=" * 60)
        brief = generate_candidate_brief(candidate_result)
        print(brief)

    # ----------------------------
    # 2. Coach Utilization
    # ----------------------------

    utilization = calculate_weekly_utilization(data["coaches"], data["bookings"])

    print("\n" + "="*60)
    print("Tempo - Coach Utilization")
    print("=" * 60)

    print(utilization.to_string(index=False))


if __name__ == "__main__":
    main()

