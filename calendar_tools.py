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
            "redirect_uris": ["https://transaction-coordinator.streamlit.app"]
        }
    }

    flow = Flow.from_client_config(
        client_config, SCOPES
    )
    flow.redirect_uri = "https://transaction-coordinator.streamlit.app"

    query_params = st.query_params
    if "code" not in query_params:
        print("🔁 DEBUG: redirect_uri being sent to Google:", flow.redirect_uri)
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Click here to authorize Google Calendar access]({auth_url})")
        st.stop()

    code = query_params["code"][0]
    flow.fetch_token(code=code)
    creds = flow.credentials
    from google.oauth2 import id_token
    from google.auth.transport import requests
    info = id_token.verify_oauth2_token(
        creds.id_token, requests.Request(), st.secrets["GOOGLE_CLIENT_ID"]
    )
    print("📧 Google account authorized:", info["email"])

    service = build("calendar", "v3", credentials=creds)

    # DEBUG: List available calendars
    calendar_list = service.calendarList().list().execute()
    for cal in calendar_list["items"]:
        print(f"📅 Calendar: {cal['summary']} → ID: {cal['id']}")

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
    st.write("✅ Event created:")
    st.markdown(f"[🔗 Open in Google Calendar]({created_event.get('htmlLink')})")