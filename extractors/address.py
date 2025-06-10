import re

# Define regex patterns for Indian address components
ADDRESS_PATTERNS = {
    "house_number": r"\b(?:Flat\s+No|House\s+No|H\.?No|Bungalow|C[- ]?\d+|Plot\s+No|House)\s*[\w-]+",
    "building": r"(?:[A-Z][a-zA-Z0-9\s]*\s+(?:Towers|Residency|Apartments|Court|Heights))",
    "landmark": r"(?:Near|Opp\.?|Opposite|Behind|Beside)\s+[A-Z][\w\s&.-]+",
    "street": r"[A-Z][\w\s]*\s+(?:Road|Street|Lane|Marg)",
    "locality": r"(?:Bandra|Ballygunge|Shivajinagar|Somajiguda|Civil Lines|F\.?C\.? Road|Rajbhavan Road|Elgin Street)",
    "city": r"(Mumbai|Kolkata|Ajmer|Hyderabad|Pune|Chennai|Delhi|Bangalore|Ahmedabad|Jaipur)",
    "district": r"(Mumbai Suburban|Kolkata|Ajmer|Hyderabad|Pune|South Delhi|North Delhi)",
    "state": r"(Maharashtra|West Bengal|Rajasthan|Telangana|Delhi|Tamil Nadu|Karnataka|Gujarat)",
    "pincode": r"\b\d{6}\b",
    "country": r"India"
}

def extract_address_components(address: str):
    """Extracts structured address fields from one address string."""
    return {
        key: (re.search(pattern, address, re.IGNORECASE).group(0)
              if re.search(pattern, address, re.IGNORECASE)
              else '-')
        for key, pattern in ADDRESS_PATTERNS.items()
    }

def extract_all_addresses(text: str):
    """Finds all address blocks and extracts each one independently."""
    address_blocks = re.findall(r"Address:\s*(.*?)\n\n", text, re.DOTALL)
    return [extract_address_components(block.strip()) for block in address_blocks]

# Example usage with your pasted text (replace this with file reading in practice)
if __name__ == "__main__":
    with open("legal_records.txt", "r", encoding="utf-8") as f:
        content = f.read()

    structured_addresses = extract_all_addresses(content)

    for i, addr in enumerate(structured_addresses, 1):
        print(f"\n📍 Address {i}")
        for k, v in addr.items():
            print(f"  {k}: {v}")
