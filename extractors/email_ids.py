import re
from typing import List
from extractors.logger import get_logger

logger = get_logger("EmailExtractor")

EMAIL_REGEX = re.compile(
    r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b'
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
    emails = re.findall(EMAIL_REGEX, text)
    logger.debug(f"Raw emails found: {emails}")

    valid_emails = {email.lower() for email in emails if is_valid_email(email)}
    logger.info(f"Valid emails extracted: {len(valid_emails)}")

    return sorted(valid_emails)
