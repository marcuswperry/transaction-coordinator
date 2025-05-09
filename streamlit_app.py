import streamlit as st
import os
import tempfile
import json

# from gpt_tools import analyze_contract_with_gpt
from calendar_tools import add_event_to_calendar
from main import extract_text_from_pdf, extract_json_from_gpt_response, try_add_event

st.set_page_config(page_title="AI Transaction Coordinator", layout="centered")

st.title("📄 AI Transaction Coordinator")
st.markdown("Upload a real estate contract (PDF), extract key dates, and sync to Google Calendar.")

parsed = None
use_sample_json = st.checkbox("💾 Load sample JSON instead of using GPT")

if use_sample_json:
    uploaded_json = st.file_uploader("Upload a sample contract JSON", type="json", key="json")
    if uploaded_json:
        parsed = json.load(uploaded_json)
        st.success("✅ Loaded sample JSON!")
        st.subheader("📋 Extracted Fields")
        st.json(parsed)

if not use_sample_json:
    uploaded_file = st.file_uploader("Choose a contract PDF", type="pdf")

    if uploaded_file:
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

            st.download_button("📥 Download JSON", data=json.dumps(parsed, indent=2), file_name="contract_output.json")
        except Exception as e:
            st.error(f"❌ Failed to process contract: {e}")

if parsed and st.button("🗓️ Add Dates to Google Calendar"):
    print("📌 Add to Calendar button clicked")
    print(f"📤 Adding: Closing Date → {parsed.get('Closing Date')}")
    try_add_event("Closing Date", parsed.get("Closing Date"))
    print(f"📤 Adding: Inspection Deadline → {parsed.get('Inspection Deadline')}")
    try_add_event("Inspection Deadline", parsed.get("Inspection Deadline"))
    print(f"📤 Adding: Financing Deadline → {parsed.get('Financing Deadline')}")
    try_add_event("Financing Deadline", parsed.get("Financing Deadline"))

    other_dates = parsed.get("Other Important Dates", {})
    if isinstance(other_dates, dict):
        for label, date in other_dates.items():
            print(f"📤 Adding: {label} → {date}")
            try_add_event(label, date)
    st.success("✅ Events sent to your Google Calendar.")