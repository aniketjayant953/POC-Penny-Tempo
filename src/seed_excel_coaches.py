"""Append dummy coaches/candidates to the Candidate-coach Excel workbook."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

XLSX = Path(__file__).resolve().parent.parent / "data" / "Candidate-coach sample data_v2.0.xlsx"
ORIGINAL_CANDIDATE = "E7C1787E-7EF8-4CCA-3EC9-08DED5E6B6F5"
ORIGINAL_NOTE_CANDIDATE = "A7C1787A-7EF8-4CCA-3EC9-08DED5E6B6F5"

COACHES = [
    ("Daniel Okafor", "daniel.okafor@right.com"),
    ("Priya Nair", "priya.nair@right.com"),
    ("Marcus Webb", "marcus.webb@right.com"),
    ("Elena Rossi", "elena.rossi@right.com"),
    ("James Carter", "james.carter@right.com"),
    ("Sofia Lindqvist", "sofia.lindqvist@right.com"),
    ("Rahul Mehta", "rahul.mehta@right.com"),
    ("Hannah Cole", "hannah.cole@right.com"),
    ("Tomasz Kowalski", "tomasz.kowalski@right.com"),
    ("Aisha Rahman", "aisha.rahman@right.com"),
    ("Noah Bennett", "noah.bennett@right.com"),
    ("Chiara Bianchi", "chiara.bianchi@right.com"),
    ("Liam Walsh", "liam.walsh@right.com"),
    ("Mei Chen", "mei.chen@right.com"),
    ("Olivia Brooks", "olivia.brooks@right.com"),
    ("Mateo Alvarez", "mateo.alvarez@right.com"),
    ("Sara Holm", "sara.holm@right.com"),
    ("Jordan Blake", "jordan.blake@right.com"),
    ("Fatima Khan", "fatima.khan@right.com"),
]

ORIGINAL_COACH_ID = "9888B675-F92A-4AC0-A015-95F3ACD4B738"
ORIGINAL_COACH_EMAIL = "abc@right.com"

CANDIDATES = [
    [("Grace Adeyemi", "grace.adeyemi@gmail.com"), ("Stuart Hale", "stuart.hale@gmail.com"), ("Helen Park", "helen.park@gmail.com")],
    [("Anjali Deshmukh", "anjali.deshmukh@gmail.com"), ("Rohan Kapoor", "rohan.kapoor@gmail.com"), ("Neha Joshi", "neha.joshi@gmail.com")],
    [("David Nguyen", "david.nguyen@gmail.com"), ("Jessica Alvarez", "jessica.alvarez@gmail.com"), ("Brian Oconnell", "brian.oconnell@gmail.com")],
    [("Chiara Conti", "chiara.conti@gmail.com"), ("Giulia Romano", "giulia.romano@gmail.com"), ("Luca Greco", "luca.greco@gmail.com")],
    [("Dana Mitchell", "dana.mitchell@gmail.com"), ("Chris Patel", "chris.patel@gmail.com"), ("Ava Brooks", "ava.brooks@gmail.com")],
    [("Erik Berg", "erik.berg@gmail.com"), ("Ingrid Holm", "ingrid.holm@gmail.com"), ("Maja Ek", "maja.ek@gmail.com")],
    [("Kavya Sharma", "kavya.sharma@gmail.com"), ("Arjun Reddy", "arjun.reddy@gmail.com"), ("Dev Malhotra", "dev.malhotra@gmail.com")],
    [("Olivia Grant", "olivia.grant@gmail.com"), ("Ben Walker", "ben.walker@gmail.com"), ("Chloe Reid", "chloe.reid@gmail.com")],
    [("Jakub Nowak", "jakub.nowak@gmail.com"), ("Katarzyna Lewandowska", "katarzyna.lewandowska@gmail.com"), ("Piotr Zielinski", "piotr.zielinski@gmail.com")],
    [("Nadia Hussain", "nadia.hussain@gmail.com"), ("Imran Qureshi", "imran.qureshi@gmail.com"), ("Sara Malik", "sara.malik@gmail.com")],
    [("Laura Fitzgerald", "laura.fitzgerald@gmail.com"), ("Peter Abbott", "peter.abbott@gmail.com"), ("Nora Quinn", "nora.quinn@gmail.com")],
    [("Marco Esposito", "marco.esposito@gmail.com"), ("Francesca Ricci", "francesca.ricci@gmail.com"), ("Elena Costa", "elena.costa@gmail.com")],
    [("Callum Murray", "callum.murray@gmail.com"), ("Rachel Thornton", "rachel.thornton@gmail.com"), ("Harry Patel", "harry.patel@gmail.com")],
    [("Wei Zhang", "wei.zhang@gmail.com"), ("Hana Suzuki", "hana.suzuki@gmail.com"), ("Kenji Mori", "kenji.mori@gmail.com")],
    [("Thomas Whitfield", "thomas.whitfield@gmail.com"), ("Megan Clarke", "megan.clarke@gmail.com"), ("Isla Bennett", "isla.bennett@gmail.com")],
    [("Lucia Torres", "lucia.torres@gmail.com"), ("Diego Vargas", "diego.vargas@gmail.com"), ("Camila Ruiz", "camila.ruiz@gmail.com")],
    [("Freja Nielsen", "freja.nielsen@gmail.com"), ("Oskar Lind", "oskar.lind@gmail.com"), ("Linnea Berg", "linnea.berg@gmail.com")],
    [("Sam Taylor", "sam.taylor@gmail.com"), ("Alex Morgan", "alex.morgan@gmail.com"), ("Riley Chen", "riley.chen@gmail.com")],
    [("Yasmin Ali", "yasmin.ali@gmail.com"), ("Omar Farouk", "omar.farouk@gmail.com"), ("Layla Hassan", "layla.hassan@gmail.com")],
]

TITLES = [
    "meetingtype.careeroptionsandplanning",
    "meetingtype.interviewpreparation",
    "meetingtype.linkedinprofile",
    "meetingtype.cvandapplications",
]

EVENTS = [
    ("Virtual", "Core Series: Job Search Strategies"),
    ("Virtual", "Core Series: Writing Your CV"),
    ("Virtual", "Core Series: (1) How to Build a LinkedIn Profile that Stands Out"),
    ("Virtual", "Core Series: Interview Essentials"),
    ("Virtual", "Enrichment Series: Demystifying Networking"),
    ("Virtual", "Enrichment Series: Job Search Burnout"),
    ("onDemand", "CVs - Writing your CV"),
    ("onDemand", "LinkedIn - How to Build a LinkedIn Profile that stands out"),
]

ROLES = [
    "Marketing Manager",
    "Engineering Manager",
    "Finance Director",
    "Product Lead",
    "Operations Manager",
    "HR Business Partner",
]


def uid(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tempo-poc.{label}")).upper()


def stamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S.0000000 +00:00")


def note_text(first: str, role: str, n: int) -> str:
    variants = [
        f"Caught up with {first}, who is targeting {role} roles. Discussed CV structure and treating it as a master CV. {first} is sending it over for a review.",
        f"Caught up with {first} again. Confidence and interview technique came up. We discussed STAR/CAR stories and a matrix to capture examples.",
        f"{first} is struggling somewhat with momentum on applications. We discussed LinkedIn refresh and a short outreach approach for warm introductions.",
        f"At the last catch-up with {first}, we focused on wellbeing and next steps. I suggested networking webinars and asked {first} to keep me updated.",
    ]
    return variants[n % len(variants)]


DEMO_DAYS = [
    datetime(2026, 10, 13),
    datetime(2026, 10, 14),
    datetime(2026, 10, 15),
    datetime(2026, 10, 16),
    datetime(2026, 10, 20),
    datetime(2026, 10, 21),
    datetime(2026, 10, 22),
    datetime(2026, 10, 23),
]
DAY_HOURS = [9, 11, 14]
HISTORIC_DAYS = [datetime(2026, 9, 8), datetime(2026, 9, 15), datetime(2026, 9, 22), datetime(2026, 9, 29)]


def add_meeting(
    meetings: list[dict],
    *,
    coach_id: str,
    coach_email: str,
    cand_id: str,
    cand_email: str,
    start: datetime,
    title: str,
    duration: int,
    key: str,
    status: str = "Accepted",
) -> None:
    end = start + timedelta(minutes=duration)
    meetings.append(
        {
            "Id": uid(f"meetingrow.{key}"),
            "MeetingId": uid(f"meeting.{key}"),
            "Title": title,
            "MeetingEventType": "MeetingEvent",
            "Status": status,
            "ScheduledBy": "Candidate",
            "ScheduledTimeStamp": stamp(start - timedelta(days=7)),
            "StartTimeStamp": stamp(start),
            "EndTimeStamp": stamp(end),
            "Duration": duration,
            "CoachEmailAddress": coach_email,
            "CandidateEmailAddress": cand_email,
            "PreferredEmailAddress": None,
            "CandidateId": cand_id,
            "CoachId": coach_id,
            "CoachBufferTime": 15,
            "CreatedTimeStamp": stamp(start - timedelta(days=8)),
            "CreatedBy": cand_id.lower(),
            "UpdatedTimeStamp": None,
            "UpdatedBy": None,
        }
    )


def add_caseload(
    meetings: list[dict],
    notes: list[dict],
    courses: list[dict],
    *,
    coach_id: str,
    coach_email: str,
    candidates: list[tuple[str, str, str]],
    hour_shift: int = 0,
) -> None:
    """candidates: (name, email, candidate_id)"""
    for j, (cand_name, cand_email, cand_id) in enumerate(candidates):
        cand_first = cand_name.split()[0]
        role = ROLES[j % len(ROLES)]
        title = TITLES[j % len(TITLES)]
        for n in range(4):
            when = datetime(2026, 8, 18) + timedelta(days=7 * n + j)
            notes.append(
                {
                    "Id": uid(f"note.{cand_email}.{n}"),
                    "CandidateId": cand_id,
                    "ProgramId": uid("program.career"),
                    "ActivityType": "B2BD33B4-8528-4920-9553-9AB4F1B947FE",
                    "ModalityType": "Modality.Virtual",
                    "ActualDurationInMinutes": "Minutes.30Minutes",
                    "Notes": note_text(cand_first, role, n),
                    "ActivityDate": stamp(when),
                    "TimelineType": 1,
                }
            )
        for e, (event_type, event_name) in enumerate(EVENTS):
            day = datetime(2026, 9, 8) + timedelta(days=(j + e * 3) % 40)
            attended = 1 if e < 5 else 0
            registered = 1 if e < 7 else 0
            start = day.replace(hour=10, minute=30) if event_type == "Virtual" else None
            end = day.replace(hour=12, minute=0) if event_type == "Virtual" else None
            courses.append(
                {
                    "CandidateId": cand_id,
                    "CourseId": uid(f"course.{cand_email}.{event_name}.{e}"),
                    "ResourceType": "External",
                    "EventType": event_type,
                    "EventName": event_name,
                    "EventDate": stamp(day) if event_type == "Virtual" else "0001-01-01 00:00:00.0000000 +00:00",
                    "StartTime": stamp(start) if start else None,
                    "EndTime": stamp(end) if end else None,
                    "IsAttended": attended,
                    "IsRegistered": registered,
                    "IsSaved": 1 if e % 2 == 0 else 0,
                    "Status": "subscribed" if registered else None,
                    "RegisteredTimeStamp": stamp(day - timedelta(days=3)),
                    "IsClientSpecific": 0,
                }
            )

        for d_idx, day in enumerate(HISTORIC_DAYS):
            hour = DAY_HOURS[(d_idx + j + hour_shift) % len(DAY_HOURS)]
            start = day.replace(hour=hour, minute=0)
            if start.weekday() >= 5:
                start += timedelta(days=7 - start.weekday())
            add_meeting(
                meetings,
                coach_id=coach_id,
                coach_email=coach_email,
                cand_id=cand_id,
                cand_email=cand_email,
                start=start,
                title=title,
                duration=60,
                key=f"{cand_email}.hist.{d_idx}",
            )

    slot = 0
    for day in DEMO_DAYS:
        for s, hour in enumerate(DAY_HOURS):
            cand_name, cand_email, cand_id = candidates[(slot + hour_shift) % len(candidates)]
            title = TITLES[slot % len(TITLES)]
            duration = 60 if s < 2 else 45
            start = day.replace(hour=hour, minute=0)
            add_meeting(
                meetings,
                coach_id=coach_id,
                coach_email=coach_email,
                cand_id=cand_id,
                cand_email=cand_email,
                start=start,
                title=title,
                duration=duration,
                key=f"{coach_email}.{day.date()}.{hour}",
            )
            slot += 1


def build_dummy() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    meetings: list[dict] = []
    notes: list[dict] = []
    courses: list[dict] = []

    original_candidates = [
        ("Emma", "xys@gmail.com", ORIGINAL_CANDIDATE),
        ("Noah Grant", "noah.grant@gmail.com", uid("candidate.noah.grant@gmail.com")),
        ("Priya Shah", "priya.shah@gmail.com", uid("candidate.priya.shah@gmail.com")),
    ]
    add_caseload(
        meetings,
        notes,
        courses,
        coach_id=ORIGINAL_COACH_ID,
        coach_email=ORIGINAL_COACH_EMAIL,
        candidates=original_candidates,
        hour_shift=0,
    )

    for i, (_coach_name, coach_email) in enumerate(COACHES):
        coach_id = uid(f"coach.{coach_email}")
        people = [(name, email, uid(f"candidate.{email}")) for name, email in CANDIDATES[i]]
        add_caseload(
            meetings,
            notes,
            courses,
            coach_id=coach_id,
            coach_email=coach_email,
            candidates=people,
            hour_shift=i % 3,
        )

    return pd.DataFrame(notes), pd.DataFrame(courses), pd.DataFrame(meetings)


def main() -> None:
    notes = pd.read_excel(XLSX, sheet_name="Coach Notes")
    courses = pd.read_excel(XLSX, sheet_name="Courses and events")
    meetings = pd.read_excel(XLSX, sheet_name="Coach Meeting")
    metadata = pd.read_excel(XLSX, sheet_name="Metadata")

    orig_cands = {ORIGINAL_CANDIDATE, ORIGINAL_NOTE_CANDIDATE}
    notes = notes[notes["CandidateId"].astype(str).str.upper().isin(orig_cands)]
    courses = courses[courses["CandidateId"].astype(str).str.upper() == ORIGINAL_CANDIDATE]
    meetings = meetings[meetings["CandidateId"].astype(str).str.upper() == ORIGINAL_CANDIDATE]

    d_notes, d_courses, d_meetings = build_dummy()
    notes = pd.concat([notes, d_notes], ignore_index=True)
    courses = pd.concat([courses, d_courses], ignore_index=True)
    meetings = pd.concat([meetings, d_meetings], ignore_index=True)

    with pd.ExcelWriter(XLSX, engine="openpyxl") as writer:
        notes.to_excel(writer, sheet_name="Coach Notes", index=False)
        courses.to_excel(writer, sheet_name="Courses and events", index=False)
        meetings.to_excel(writer, sheet_name="Coach Meeting", index=False)
        metadata.to_excel(writer, sheet_name="Metadata", index=False)

    print(f"Wrote {XLSX}")
    print(f"meetings={len(meetings)} notes={len(notes)} courses={len(courses)}")
    print(f"coaches={meetings['CoachId'].nunique()} candidates={meetings['CandidateId'].nunique()}")


if __name__ == "__main__":
    main()
