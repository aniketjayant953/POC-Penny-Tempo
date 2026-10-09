import pandas as pd

from data_loader import load_data

def calculate_weekly_utilization(coaches, bookings):
    """Calculate weekly utilization.
    Cancelled sessions are excluded. Only completed and booked sessions are considered eligible."""

    coaches = coaches.copy()
    bookings = bookings.copy()

    # Convert dates
    bookings["session_date"] = pd.to_datetime(bookings["session_date"])

    # Convert duration to hours
    bookings["duration_hours"] = bookings["duration_minutes"] / 60 
    
    # Exclude cancelled sessions)
    eligible_bookings = bookings[bookings["status"].str.lower().isin(["completed", "booked"])].copy()

    # Get week starting Monday
    eligible_bookings["week_start"] = (eligible_bookings["session_date"] - pd.to_timedelta(eligible_bookings["session_date"].dt.weekday, unit="D"))

    # Aggregate coaching hours by coach and week
    weekly_booked = (eligible_bookings.groupby(["coach_id", "week_start"], as_index=False)["duration_hours"].sum().rename(columns={"duration_hours": "booked_coaching_hours"}))

    # Create coach/week combination 
    weeks = weekly_booked["week_start"].unique()

    coach_week = pd.MultiIndex.from_product([coaches["coach_id"],weeks], names=["coach_id", "week_start"]).to_frame(index=False)

    # Add working hours
    result = coach_week.merge(coaches[["coach_id", "working_hours_per_week"]], on="coach_id", how="left") 

    # Add booked hours
    result = result.merge(weekly_booked, on=["coach_id", "week_start"], how="left")

    result["booked_coaching_hours"] = (result["booked_coaching_hours"].fillna(0)) 

    # Calculate utilization
    result["utilization_percentage"] = result["booked_coaching_hours"]/ result["working_hours_per_week"] * 100

    return result.sort_values(["week_start", "coach_id"])

if __name__ == "__main__":
    data = load_data()

    result = calculate_weekly_utilization(data["coaches"],data["bookings"])

    print("\nWeekly Coach Utilitzation")
    print("--------------------------")
    
    print(result.to_string(index=False))