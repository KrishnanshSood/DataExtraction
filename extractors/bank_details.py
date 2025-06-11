import re
from typing import Tuple, List
from extractors.logger import get_logger
from extractors.phone_numbers import extract_phone_numbers

logger = get_logger("BankDetailsExtractor")

# Standard IFSC code: 4 letters, 0, 6 alphanumeric
IFSC_REGEX = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# Account numbers: 9–18 digits
ACCOUNT_REGEX = re.compile(r'\b\d{9,18}\b')

def extract_bank_details(text: str) -> Tuple[List[str], List[str]]:
    logger.info("Extracting IFSC and Account Numbers...")

    # Extract raw values
    ifsc_codes = set(re.findall(IFSC_REGEX, text))
    all_accounts = set(re.findall(ACCOUNT_REGEX, text))

    # Extract phone numbers (mobile only)
    mobiles, _ = extract_phone_numbers(text)
    mobile_numbers = set(mobiles)

    # Filter out mobile-like numbers from account numbers
    cleaned_accounts = {
        acc for acc in all_accounts
        if acc not in mobile_numbers and len(acc) >= 11
    }

    logger.info(f"✅ Accounts: {len(cleaned_accounts)} | IFSCs: {len(ifsc_codes)}")
    return sorted(cleaned_accounts), sorted(ifsc_codes)
