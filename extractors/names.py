from flair.data import Sentence
from flair.models import SequenceTagger
from typing import List, Tuple
import re
import torch
from extractors.logger import get_logger

logger = get_logger("FlairNER")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Loading Flair NER model on device: {device}")
tagger = SequenceTagger.load("ner").to(device)
logger.info("Flair NER model loaded successfully.")

# Junk/utility terms to discard
JUNK_TERMS = {"mobile", "email", "pan", "gstin", "ifsc", "ref", "fax", "pin", "tel"}

# Address/real-estate related words
ADDRESS_KEYWORDS = {
    "tower", "near", "road", "line", "block", "sector", "building", "post office",
    "street", "phase", "lane", "apartments", "residency", "complex", "floor", "park", "sadan"
}

# Valid suffixes and keywords for organizations
ORG_SUFFIXES = {
    "Ltd", "Inc", "LLP", "Pvt", "Corp", "Company", "Corporation",
    "Technologies", "Systems", "Bank", "Agency", "Enterprises", "Services"
}

ORG_KEYWORDS = {
    "Ministry", "Board", "Institute", "Council", "Commission", "University",
    "Trust", "Association", "Department", "Authority", "Office", "Government",
    "Directorate", "Chamber", "Organization", "DGFT", "Govt", "Division"
}

# Fallback pattern for missed company mentions like "M/s. XYZ Pvt Ltd"
COMPANY_REGEX = re.compile(
    r"\bM/s\.?\s+([A-Z][A-Za-z0-9&().,\s\-]*?(?:Pvt\.?\s*Ltd\.?|LLP|Limited|Corporation|Company|Inc\.?))",
    re.IGNORECASE
)

def is_valid_entity(text: str, label: str) -> bool:
    text = text.strip()
    lower = text.lower()

    if lower in JUNK_TERMS or len(text) < 3 or re.search(r"\d{5,}", text):
        return False

    if not re.search(r"[A-Z][a-z]+", text):
        return False  # Must contain at least one capitalized word

    if label == "ORG":
        norm_text = text.lower()

        # Block address-like or real-estate orgs
        if any(word in norm_text for word in ADDRESS_KEYWORDS):
            return False

        # Block misclassified policy-like entities
        if re.search(r'\bPolicy\b', text, re.IGNORECASE):
            return False

        # Allow if suffix or high-confidence keywords found
        if any(kw.lower() in norm_text for kw in ORG_KEYWORDS | ORG_SUFFIXES):
            return True

        # Allow multi-word org names like "AMC Cookware"
        if len(text.split()) >= 2:
            return True

        return False  # One-word orgs w/o suffix/keyword → discard

    return True

def extract_names(text: str) -> Tuple[List[str], List[str]]:
    logger.info("Running Flair NER prediction...")
    sentence = Sentence(text)
    tagger.predict(sentence)
    logger.info("NER prediction completed.")

    people = set()
    orgs = set()

    for entity in sentence.get_spans('ner'):
        label = entity.get_label("ner").value
        cleaned = entity.text.strip()
        logger.debug(f"Entity found: {cleaned} ({label})")

        if is_valid_entity(cleaned, label):
            if label == "PER":
                people.add(cleaned)
            elif label == "ORG":
                orgs.add(cleaned)
        else:
            logger.debug(f"Entity discarded: {cleaned}")

    # ➕ Add fallback orgs detected via regex
    fallback_orgs = {
        match.group(1).strip()
        for match in COMPANY_REGEX.finditer(text)
    }
    orgs.update(fallback_orgs)

    logger.info(f"People found: {len(people)} | Orgs found: {len(orgs)}")
    return sorted(people), sorted(orgs)
