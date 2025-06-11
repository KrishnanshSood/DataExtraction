import requests
import json
import re
import ast

LLAMA_API_URL = "http://localhost:11434/api/generate"
LLAMA_MODEL = "llama3"

# Desired Indian address structure
ADDRESS_FIELDS = [
    "flat_or_house_number",
    "building_or_post_office",
    "street",
    "area",
    "town_or_city",
    "district",
    "state",
    "country",
    "pincode"
]

def call_llama_address_parser(text: str) -> dict:
    """Call local LLaMA model to parse address into structured Indian format."""
    prompt = f"""
You are an expert in Indian address extraction.

From the following unstructured text, extract an Indian address and return it as a JSON object with these fields:
- flat_or_house_number
- building_or_post_office
- street
- area
- town_or_city
- district
- state
- country
- pincode

If a field is not found, return it as "-". Respond ONLY with valid compact JSON. No explanations.

Text:
\"\"\"{text}\"\"\"
"""

    response = requests.post(LLAMA_API_URL, json={
        "model": LLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return {key: "-" for key in ADDRESS_FIELDS}

    raw_response = response.json().get("response", "").strip()

    # Attempt strict JSON parsing
    try:
        parsed = json.loads(raw_response)
        if isinstance(parsed, dict):
            return {k: parsed.get(k, "-") for k in ADDRESS_FIELDS}
    except Exception:
        pass

    # Fallback: try Python dict literal (less strict)
    try:
        parsed = ast.literal_eval(raw_response)
        if isinstance(parsed, dict):
            return {k: parsed.get(k, "-") for k in ADDRESS_FIELDS}
    except Exception:
        pass

    print("⚠️ Could not parse model response:")
    print(raw_response)
    return {key: "-" for key in ADDRESS_FIELDS}


def get_address_blocks(text: str) -> list:
    """Heuristically identify address-like chunks from raw text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks = []
    buffer = []

    for line in lines:
        buffer.append(line)
        joined = " ".join(buffer)

        if re.search(r"\b\d{6}\b", joined) or re.search(r"\b(distt|district|state|pin|po|ps|city|village)\b", joined, re.IGNORECASE):
            blocks.append(joined)
            buffer.clear()
        elif len(buffer) > 3:
            buffer.clear()

    return blocks


def extract_all_addresses(text: str) -> list:
    """Main function to extract structured addresses using LLaMA."""
    raw_blocks = get_address_blocks(text)
    results = []

    for block in raw_blocks:
        parsed = call_llama_address_parser(block)
        results.append({
            "raw_block": block,
            "components": parsed
        })

    return results


# 🧪 Optional CLI test
if __name__ == "__main__":
    with open("legal_records.txt", "r", encoding="utf-8") as f:
        content = f.read()

    addresses = extract_all_addresses(content)

    for i, addr in enumerate(addresses, 1):
        print(f"\n🏷️ Address Block {i}")
        print(f"Raw: {addr['raw_block']}")
        print("📍 Address Components Found:")
        for key in ADDRESS_FIELDS:
            print(f"- {key}: {addr['components'].get(key, '-')}")
