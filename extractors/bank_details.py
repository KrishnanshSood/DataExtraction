import re
from typing import Tuple, List
from extractors.logger import get_logger
from extractors.mobile_numbers import extract_mobile_numbers

logger = get_logger("BankDetailsExtractor")

IFSC_REGEX = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')
ACCOUNT_REGEX = re.compile(r'\b\d{9,18}\b')

def extract_bank_details(text: str) -> Tuple[List[str], List[str]]:
    logger.info("Extracting IFSC and Account Numbers...")

    ifsc_codes = set(re.findall(IFSC_REGEX, text))
    all_accounts = set(re.findall(ACCOUNT_REGEX, text))

    mobile_numbers = set(extract_mobile_numbers(text))
    cleaned_accounts = {
        acc for acc in all_accounts
        if acc not in mobile_numbers and len(acc) >= 11
    }

    logger.info(f"Accounts: {len(cleaned_accounts)} | IFSCs: {len(ifsc_codes)}")
    return sorted(cleaned_accounts), sorted(ifsc_codes)
