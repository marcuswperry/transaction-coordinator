

import streamlit as st
import os
import tempfile
import json

from gpt_tools import analyze_contract_with_gpt
from calendar_tools import add_event_to_calendar
from main import extract_text_from_pdf, extract_json_from_gpt_response, try_add_event

st.set_page_config(page_title="AI Transaction Coordinator", layout="centered")

st.title("📄 AI Transaction Coordinator")
st.markdown("Upload a real estate contract (PDF), extract key dates, and sync to Google Calendar.")

# File upload
uploaded_file = st.file_uploader("Choose a contract PDF", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    st.success("✅ File uploaded. Extracting text...")
    text = extract_text_from_pdf(temp_path)

    with st.spinner("🧠 Sending to OpenAI..."):
        gpt_output = analyze_contract_with_gpt(text)

    try:
        parsed = extract_json_from_gpt_response(gpt_output)
        st.success("✅ Contract analyzed successfully!")
        st.subheader("📋 Extracted Fields")
        st.json(parsed)

        # Option to download JSON
        st.download_button("📥 Download JSON", data=json.dumps(parsed, indent=2), file_name="contract_output.json")

        # Option to add to Google Calendar
        if st.button("🗓️ Add Dates to Google Calendar"):
            try_add_event("Closing Date", parsed.get("Closing Date"))
            try_add_event("Inspection Deadline", parsed.get("Inspection Deadline"))
            try_add_event("Financing Deadline", parsed.get("Financing Deadline"))

            other_dates = parsed.get("Other Important Dates", {})
            if isinstance(other_dates, dict):
                for label, date in other_dates.items():
                    try_add_event(label, date)
            st.success("✅ Events sent to your Google Calendar.")
    except Exception as e:
        st.error(f"❌ Failed to process contract: {e}")