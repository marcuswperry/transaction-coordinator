import os
from openai import OpenAI
import streamlit as st
openai_key = st.secrets["OPENAI_API_KEY"]
print(f"🔐 Loaded OpenAI key prefix: {openai_key[:5]}")

client = OpenAI(api_key=openai_key)

def analyze_contract_with_gpt(contract_text):
    prompt = f"""
You are a real estate assistant. Given the contract text below:

1. Provide a brief summary of the agreement (3–4 sentences).
2. Extract the following fields in JSON format (use real calendar dates in the format YYYY-MM-DD, e.g., "2025-05-30"):
   - Buyer
   - Seller
   - Property Address
   - Purchase Price
   - Closing Date
   - Inspection Deadline (as MM/DD/YYYY, not "10 days after...")
   - Financing Deadline
   - Any other important dates (with actual dates)

Return the summary first, then the JSON in a markdown ```json block.

Contract text:
\"\"\"
{contract_text}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content

    # Optional: log token usage
    usage = response.usage
    print(f"\n🧮 Token usage: {usage.total_tokens} total (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")

    return content