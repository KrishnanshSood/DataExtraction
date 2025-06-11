import re

# Define regex patterns for Indian address components
ADDRESS_PATTERNS = {
    "house_number": r"\b(?:Flat\s+No|House\s+No|H\.?No|Bungalow|Plot\s+No|House)\s*\w+",
    "building": r"[A-Z][a-zA-Z0-9\s]*\s+(?:Towers|Residency|Apartments|Court|Heights|Block|Building)",
    "landmark": r"(?:Near|Opp\.?|Opposite|Behind|Beside)\s+[A-Z][\w\s&.-]+",
    "street": r"[A-Z][\w\s]*\s+(?:Road|Street|Lane|Marg|Main Road)",
    "locality": r"(Bandra|Ballygunge|Shivajinagar|Koramangala|Civil Lines|F\.?C\.? Road|Rajbhavan Road|Elgin Street|Shanumangala|Bidadi|Hobli)",
    "city": r"(Mumbai|Kolkata|Ajmer|Hyderabad|Pune|Chennai|Delhi|Bangalore|BENGALURU|Ahmedabad|Jaipur|Ramanagara)",
    "district": r"(Mumbai Suburban|Kolkata|Ajmer|Hyderabad|Pune|South Delhi|North Delhi|Ramanagara|BENGALURU URBAN)",
    "state": r"(Maharashtra|West Bengal|Rajasthan|Telangana|Delhi|Tamil Nadu|Karnataka|Gujarat)",
    "pincode": r"\b\d{6}\b",
    "country": r"India"
}

def extract_address_components(address: str):
    """Extracts structured fields from a block of address text."""
    return {
        key: (re.search(pattern, address, re.IGNORECASE).group(0)
              if re.search(pattern, address, re.IGNORECASE)
              else '-')
        for key, pattern in ADDRESS_PATTERNS.items()
    }

def extract_all_addresses(text: str):
    """
    Finds possible address blocks using heuristic:
    Lines with commas and pin codes.
    """
    candidate_lines = text.splitlines()
    address_blocks = []

    for line in candidate_lines:
        if ',' in line and re.search(r"\b\d{6}\b", line):
            address_blocks.append(line.strip())

    return [extract_address_components(block) for block in address_blocks]

# Optional: Demo
if __name__ == "__main__":
    with open("legal_records.txt", "r", encoding="utf-8") as f:
        content = f.read()

    structured_addresses = extract_all_addresses(content)

    for i, addr in enumerate(structured_addresses, 1):
        print(f"\n📍 Address Block {i}")
        for k, v in addr.items():
            print(f"  {k}: {v}")
