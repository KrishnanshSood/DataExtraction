import re
from typing import List
from extractors.logger import get_logger

logger = get_logger("PassportExtractor")

# Indian passport format: one letter (excluding Q, X, Z) followed by 7 digits
PASSPORT_REGEX = re.compile(r'\b(?:Passport\s*[:\-]?\s*)?([A-PR-WYa-pr-wy][1-9]\d{6})\b')


def extract_passport_numbers(text: str) -> List[str]:
    logger.info("Extracting passport numbers...")

    # Find all matching groups (only the passport number part)
    matches = PASSPORT_REGEX.findall(text)

    # Normalize to uppercase and remove duplicates
    unique_passports = sorted(set(m.upper() for m in matches))

    logger.info(f"Passport numbers found: {len(unique_passports)}")
    return unique_passports
