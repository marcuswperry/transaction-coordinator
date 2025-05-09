import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scope for full calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def add_event_to_calendar(summary, date_str):
    """Add an all-day event to Google Calendar using ISO date format (YYYY-MM-DD)."""

    import streamlit as st

    client_config = {
        "installed": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["https://marcuswperry-transaction-coordinator.streamlit.app"]
        }
    }

    flow = Flow.from_client_config(
        client_config, SCOPES
    )
    flow.redirect_uri = client_config["installed"]["redirect_uris"][0]

    query_params = st.query_params
    if "code" not in query_params:
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Click here to authorize Google Calendar access]({auth_url})")
        st.stop()

    code = query_params["code"][0]
    flow.fetch_token(code=code)
    creds = flow.credentials

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