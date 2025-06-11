import re
from typing import List, Tuple
from extractors.logger import get_logger

logger = get_logger("PhoneExtractor")

# Context keywords near numbers (optional future usage)
CONTEXT_KEYWORDS = {"mobile", "phone", "contact", "cell", "tel", "telephone", "ph", "ph."}

# Mobile number formats (both continuous and split)
MOBILE_REGEX = re.compile(
    r'(?:\+91|91|0)?[\s\-()]*([6-9]\d{9})\b|'                             # continuous match
    r'(?:\+91|91|0)?[\s\-()]*([6-9]\d{4})[\s\-]*([\d]{5})\b'              # split match (5+5)
)

# Landline numbers like 080-25537215, 0112345678
LANDLINE_REGEX = re.compile(r'\b(0\d{2,5}[\s\-]?\d{5,8})\b')

# Validators
MOBILE_PATTERN = re.compile(r'^[6-9]\d{9}$')
LANDLINE_PATTERN = re.compile(r'^(0\d{2,4}|\d{3,5})\d{5,8}$')


def extract_phone_numbers(text: str) -> Tuple[List[str], List[str]]:
    logger.info("Extracting phone numbers (mobile + landline)...")

    mobile_numbers = set()
    landline_numbers = set()

    # Normalize text for better matching
    clean_text = text.replace(";", " ").replace(")", " ").replace("(", " ")

    # Extract mobile numbers
    for match in MOBILE_REGEX.finditer(clean_text):
        digits = None
        if match.group(1):  # continuous 10-digit mobile
            digits = match.group(1)
        elif match.group(2) and match.group(3):  # split mobile (5+5)
            digits = match.group(2) + match.group(3)

        if digits and MOBILE_PATTERN.match(digits):
            logger.debug(f"✅ Mobile found: {digits}")
            mobile_numbers.add(digits)

    # Extract landline numbers
    for match in LANDLINE_REGEX.finditer(clean_text):
        raw = match.group(1)
        digits = re.sub(r'\D', '', raw)
        if 8 <= len(digits) <= 11 and LANDLINE_PATTERN.match(digits):
            logger.debug(f"📞 Landline found: {digits}")
            landline_numbers.add(digits)

    logger.info(f"✅ Mobiles: {len(mobile_numbers)} | 📞 Landlines: {len(landline_numbers)}")
    return sorted(mobile_numbers), sorted(landline_numbers)
