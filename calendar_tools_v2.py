import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_google_credentials():
    if 'credentials' in st.session_state:
        creds = st.session_state['credentials']
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state['credentials'] = creds
        else:
            if 'code' in st.experimental_get_query_params():
                code = st.experimental_get_query_params()['code'][0]
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='https://transaction-coordinator.streamlit.app')
                flow.fetch_token(code=code)
                creds = flow.credentials
                st.session_state['credentials'] = creds
                st.experimental_set_query_params()  # Clear query params
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='https://transaction-coordinator.streamlit.app')
                auth_url, _ = flow.authorization_url(prompt='consent')
                st.markdown(f"Please [authorize]({auth_url}) to continue.")
                st.stop()
    return creds

def create_event(summary, date_str):
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'start': {
            'date': date_str,
        },
        'end': {
            'date': date_str,
        },
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')

def list_calendars():
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)
    calendar_list = service.calendarList().list().execute()
    for calendar_entry in calendar_list.get('items', []):
        print(f"Calendar: {calendar_entry['summary']} (ID: {calendar_entry['id']})")
