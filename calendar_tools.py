import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scope for full calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def add_event_to_calendar(summary, date_str):
    """Add an all-day event to Google Calendar using ISO date format (YYYY-MM-DD)."""

    # Authenticate
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    # Assume date_str is already ISO-formatted
    iso_date = date_str

    # Build all-day event
    event = {
        "summary": summary,
        "start": {"date": iso_date},
        "end": {"date": iso_date},
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ Event created: '{summary}' on {iso_date}")
    print("🔗", created_event.get("htmlLink"))