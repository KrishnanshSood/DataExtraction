import re
from typing import List
from extractors.logger import get_logger

logger = get_logger("MobileExtractor")

# Regex pattern for Indian mobile numbers
# Allows: +91 98100 33445, 09810033445, 9810033445 etc.
MOBILE_REGEX = re.compile(
    r'(?:(?:\+91|91|0)[-\s]*)?([6-9]\d{4}[-\s]?\d{5})\b'
)

# Context words that should appear near a mobile number
CONTEXT_KEYWORDS = {"mobile", "contact", "phone", "cell", "tel"}

def extract_mobile_numbers(text: str) -> List[str]:
    logger.info("Extracting mobile numbers with context-aware filtering...")

    matches = list(MOBILE_REGEX.finditer(text))
    logger.debug(f"Total matches found: {len(matches)}")

    valid_numbers = set()

    for match in matches:
        raw = match.group(1)
        digits = re.sub(r'\D', '', raw)

        # Ensure it's a 10-digit number starting with 6-9
        if len(digits) == 10 and digits[0] in "6789":
            # Optional: apply context filtering (50 chars before match)
            context_start = max(match.start() - 50, 0)
            context = text[context_start:match.start()].lower()

            if any(keyword in context for keyword in CONTEXT_KEYWORDS):
                logger.debug(f"Context match ✅ for number: {digits}")
                valid_numbers.add(digits)
            else:
                logger.debug(f"No context → Skipped number: {digits}")

    logger.info(f"Final mobile numbers extracted: {len(valid_numbers)}")
    return sorted(valid_numbers)
