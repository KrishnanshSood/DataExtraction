import re
from typing import List
from extractors.logger import get_logger

logger = get_logger("EmailExtractor")

EMAIL_REGEX = re.compile(
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    re.IGNORECASE
)

# Acceptable top-level domains
VALID_TLDS = {"com", "in", "net", "org", "co", "gov", "edu", "biz"}

def is_valid_email(email: str) -> bool:
    try:
        domain = email.split("@")[1]
        tld = domain.split(".")[-1].lower()
        return tld in VALID_TLDS
    except Exception:
        return False

def extract_emails(text: str) -> List[str]:
    logger.info("Extracting email addresses...")
    matches = EMAIL_REGEX.findall(text)
    valid_emails = {email.strip() for email in matches}
    logger.info(f"Valid emails extracted: {len(valid_emails)}")
    return sorted(valid_emails)

