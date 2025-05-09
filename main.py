import os
import re
import json
import pdfplumber
from dotenv import load_dotenv
# from gpt_tools import analyze_contract_with_gpt
from calendar_tools import add_event_to_calendar

CONTRACTS_FOLDER = "contracts"

# Load API key from .env
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# === PDF Text Extraction ===
def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# === GPT Output Parsing ===
def extract_json_from_gpt_response(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    else:
        raise ValueError("Could not extract JSON from GPT output.")

# === Calendar Event Wrapper ===
def try_add_event(label, date_value):
    if date_value and "20" in date_value:  # crude check for full dates like 'May 25, 2025'
        add_event_to_calendar(label, date_value)
    else:
        print(f"⚠️ Skipping {label}: not a valid calendar date →", date_value)

# === Main Execution ===
def main():
    for filename in os.listdir(CONTRACTS_FOLDER):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(CONTRACTS_FOLDER, filename)
            print(f"\n📄 Processing: {filepath}")

            contract_text = extract_text_from_pdf(filepath)
            print("🤖 Sending to OpenAI...")
            gpt_output = analyze_contract_with_gpt(contract_text)
            print("\n=== Raw GPT Output ===\n")
            print(gpt_output)

            try:
                parsed = extract_json_from_gpt_response(gpt_output)
                print("\n✅ Parsed Contract Fields:")
                print(json.dumps(parsed, indent=2))

                # Add calendar events
                try_add_event("Closing Date", parsed.get("Closing Date"))
                try_add_event("Inspection Deadline", parsed.get("Inspection Deadline"))
                try_add_event("Financing Deadline", parsed.get("Financing Deadline"))

                # Handle any extra dates
                other_dates = parsed.get("Other Important Dates", {})
                if isinstance(other_dates, dict):
                    for label, date in other_dates.items():
                        try_add_event(label, date)

                output_path = os.path.join("output", filename + ".json")
                with open(output_path, "w") as f:
                    json.dump(parsed, f, indent=2)
                print(f"📝 Saved extracted data to {output_path}")

                # Move file to /processed/ folder
                processed_path = os.path.join("processed", filename)
                os.rename(filepath, processed_path)
                print(f"📦 Moved {filename} to /processed/")

            except Exception as e:
                print(f"❌ Error parsing {filename}:", e)

if __name__ == "__main__":
    main()