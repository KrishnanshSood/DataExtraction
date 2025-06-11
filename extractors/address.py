import re

# More robust regex patterns for Indian address components
ADDRESS_PATTERNS = {
    "house_number": r"\b(?:Flat\s*No\.?|House\s*No\.?|H\.?No\.?|Plot\s*No\.?|Bungalow|Door\s*No\.?)\s*\w+",
    "building": r"[A-Z][a-zA-Z0-9\s]*\s+(?:Towers|Residency|Apartments|Court|Heights|Block|Building|Complex)",
    "landmark": r"(?:Near|Opp\.?|Opposite|Behind|Beside)\s+[A-Z][\w\s&().,-]+",
    "street": r"\b[\w\s]*\s+(?:Road|Street|Lane|Marg|Main Road)\b",
    "locality": r"\b(?:Bandra|Ballygunge|Shivajinagar|Koramangala|Civil Lines|Rajbhavan Road|Elgin Street|F\.?C\.? Road|Shanumangala|Bidadi|Hobli)\b",
    "city": r"\b(?:Mumbai|Kolkata|Ajmer|Hyderabad|Pune|Chennai|Delhi|Bangalore|BENGALURU|Ahmedabad|Jaipur|Ramanagara)\b",
    "district": r"\b(?:Mumbai Suburban|Kolkata|Ajmer|Hyderabad|Pune|South Delhi|North Delhi|Ramanagara|BENGALURU URBAN)\b",
    "state": r"\b(?:Maharashtra|West Bengal|Rajasthan|Telangana|Delhi|Tamil Nadu|Karnataka|Gujarat)\b",
    "pincode": r"\b\d{6}\b",
    "country": r"\bIndia\b"
}

def extract_address_components(address: str) -> dict:
    """Extracts structured components from a single address string."""
    return {
        key: (
            re.search(pattern, address, re.IGNORECASE).group(0)
            if re.search(pattern, address, re.IGNORECASE)
            else "-"
        )
        for key, pattern in ADDRESS_PATTERNS.items()
    }

def extract_all_addresses(text: str):
    """
    Extracts possible address blocks using lines that:
    - contain a comma (common in addresses)
    - contain a valid 6-digit pincode
    """
    candidate_lines = text.splitlines()
    address_blocks = []

    for line in candidate_lines:
        if ',' in line and re.search(ADDRESS_PATTERNS["pincode"], line):
            address_blocks.append(line.strip())

    return [extract_address_components(block) for block in address_blocks]

# Optional standalone test
if __name__ == "__main__":
    with open("legal_records.txt", "r", encoding="utf-8") as f:
        content = f.read()

    structured_addresses = extract_all_addresses(content)

    for i, addr in enumerate(structured_addresses, 1):
        print(f"\n📍 Address Block {i}")
        for k, v in addr.items():
            print(f"  {k}: {v}")
