import re
from typing import Tuple, List
from extractors.logger import get_logger

logger = get_logger("PAN_GSTIN_Extractor")

# PAN Format: 5 letters + 4 digits + 1 letter
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# GSTIN Format: 2 digits + PAN + 1 char + Z + 1 char
GSTIN_REGEX = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b')


def extract_pan_and_gstin(text: str) -> Tuple[List[str], List[str]]:
    logger.info("Extracting PAN and GSTIN...")

    pans = set(re.findall(PAN_REGEX, text))
    gstins = set(re.findall(GSTIN_REGEX, text))

    # Filter PANs that are part of GSTIN
    embedded_pans = {gstin[2:12] for gstin in gstins}
    final_pans = pans - embedded_pans

    logger.info(f"PANs: {len(final_pans)} | GSTINs: {len(gstins)}")
    return sorted(final_pans), sorted(gstins)
