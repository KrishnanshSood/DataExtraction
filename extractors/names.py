# extractors/names.py

from flair.data import Sentence
from flair.models import SequenceTagger
from typing import List, Tuple
import re
import torch
from extractors.logger import get_logger

logger = get_logger("FlairNER")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Loading Flair NER model on device: {device}")
tagger = SequenceTagger.load("ner").to(device)
logger.info("Flair NER model loaded successfully.")

JUNK_TERMS = {"mobile", "email", "pan", "gstin", "ifsc", "ref", "fax", "pin"}
ADDRESS_KEYWORDS = {
    "tower", "near", "road", "line", "block", "sector", "building", "post office",
    "street", "phase", "lane", "apartments", "residency", "complex", "floor"
}
ORG_SUFFIXES = {"Ltd", "Inc", "LLP", "Pvt", "Corp", "Company", "Corporation", "Technologies", "Bank", "Agency"}
ORG_KEYWORDS = {"Ministry", "Board", "Institute", "Council", "Commission", "University", "Trust", "Association"}

def is_valid_entity(text: str, label: str) -> bool:
    text = text.strip()
    lower = text.lower()

    if lower in JUNK_TERMS or len(text) < 3 or re.search(r"\d", text):
        return False

    if not re.search(r"[A-Z][a-z]+", text):
        return False

    if label == "ORG":
        # Normalize
        norm_text = text.lower()
        # Too address-like
        if any(word in norm_text for word in ADDRESS_KEYWORDS):
            return False
        # Vague or single-word without clear suffix
        if " " not in text and not any(suffix.lower() in norm_text for suffix in ORG_SUFFIXES):
            return False
        # Real-estate or location-like orgs
        if re.search(r"\b(Apartments?|Tower|Block|Sector|Road|Lines|Street|Phase|Valley|Park|Residency)\b", text, re.IGNORECASE):
            return False
        # Accept if it includes high-signal keywords
        if any(keyword in text for keyword in ORG_KEYWORDS):
            return True

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

    logger.info(f"People found: {len(people)} | Orgs found: {len(orgs)}")
    return sorted(people), sorted(orgs)
