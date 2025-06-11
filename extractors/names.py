from typing import List, Tuple
from transformers import AutoTokenizer, AutoModelForTokenClassification
from flair.models import SequenceTagger
from flair.data import Sentence
import torch
import re
from difflib import SequenceMatcher
from extractors.logger import get_logger

logger = get_logger("HybridNER")

# Load IndicNER
INDIC_MODEL = "ai4bharat/IndicNER"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

logger.info(f"Loading IndicNER on {device}")
indic_tokenizer = AutoTokenizer.from_pretrained(INDIC_MODEL)
indic_model = AutoModelForTokenClassification.from_pretrained(INDIC_MODEL).to(device)
id2label = indic_model.config.id2label
logger.info("✅ IndicNER loaded")

# Load Flair NER
logger.info("Loading Flair NER...")
flair_tagger = SequenceTagger.load("ner").to(device)
logger.info("✅ Flair NER loaded")

# Keywords for ORG classification
ORG_KEYWORDS = {
    "ministry", "department", "board", "authority", "commission", "university",
    "institute", "directorate", "organization", "govt", "government", "council",
    "trust", "office", "corporation", "services", "company", "enterprises", "ltd",
    "limited", "llp", "inc", "bank", "association", "dgft", "division", "agency",
    "firm", "foundation", "group", "technologies", "systems", "cement", "factory", "house"
}

ADDRESS_WORDS = {
    "bhawan", "road", "street", "floor", "building", "lane", "nagar", "khana", "bazaar", "market", "block", "sector"
}

NARRATIVE_VERBS = {"said", "added", "told", "confessed", "loaded", "driven", "stated", "mentioned", "reported"}

# Regex for fallback orgs
PRIVATE_ORG_REGEX = re.compile(
    r"\b([A-Z][A-Za-z0-9&.\-]*\s(?:Enterprises|Industries|Technologies|Consultants|Corporation|Group|Exports|Services|Systems))\b",
    re.IGNORECASE
)

COMPANY_REGEX = re.compile(
    r"\bM/s\.?\s+([A-Z][A-Za-z0-9&().,\s\-]{2,}?(?:Pvt\.?\s*Ltd\.?|LLP|Limited|Corporation|Company|Inc\.?))\b",
    re.IGNORECASE
)

CEMENT_LIKE_REGEX = re.compile(
    r"\b([A-Z][\w\s&.,\-()]{2,}?(?:Cement|Factory|House|Corporation|Industries|Group))\b",
    re.IGNORECASE
)

# Improved M/s. pattern to avoid trailing clause text
MS_ORG_REGEX = re.compile(
    r"\bM/s\.?\s+([A-Z][\w&.-]*(?:\s+[A-Z][\w&.-]*){0,5})\b"
)

def chunk_text(text: str) -> List[str]:
    return [line.strip() for line in re.split(r'[\n;.]+', text) if line.strip()]

def clean_entity(e: str) -> str:
    return re.sub(r"\s+", " ", e.strip())

def is_valid_name(name: str) -> bool:
    if not name or len(name) < 3 or name.isupper() or re.fullmatch(r'\d+', name):
        return False
    words = name.split()
    return len(words) >= 2 and sum(w[0].isupper() for w in words if w) >= 2

def is_probable_org(text: str) -> bool:
    if any(word in text.lower() for word in ADDRESS_WORDS):
        return False
    count = sum(kw in text.lower() for kw in ORG_KEYWORDS)
    return count >= 1

def is_location_like(name: str) -> bool:
    return any(x.lower() in name.lower() for x in ["chowk", "road", "bazar", "chowpathy", "nagar", "block", "district", "market", "lane"])

def is_clean_org(org: str) -> bool:
    org = org.strip()
    if len(org) > 100:
        return False
    if re.match(r'^[a-z]', org):  # starts with lowercase
        return False
    if any(w in org.lower() for w in NARRATIVE_VERBS):
        return False
    if sum(1 for w in org.split() if w and w[0].isupper()) < 2:
        return False
    if len(org.split()) < 2:
        return False
    return True

def split_merged_orgs(text: str) -> List[str]:
    phrases = []
    while True:
        tokens = text.strip().split()
        if not tokens:
            break
        of_indices = [i for i, tok in enumerate(tokens) if tok.lower() == 'of']
        if len(of_indices) < 2:
            break
        second_of = of_indices[1]
        if second_of < 1:
            break
        phrase_tokens = tokens[:second_of - 1]
        if phrase_tokens:
            phrases.append(" ".join(phrase_tokens))
        tokens = tokens[second_of - 1:]
        text = " ".join(tokens)
    if text.strip():
        phrases.append(text.strip())
    return phrases

def extract_indic_names(text: str) -> List[str]:
    encoded = indic_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)

    with torch.no_grad():
        logits = indic_model(input_ids=input_ids, attention_mask=attention_mask).logits

    predictions = torch.argmax(logits, dim=2)[0]
    tokens = indic_tokenizer.convert_ids_to_tokens(input_ids[0])
    labels = [id2label[p.item()] for p in predictions]

    people = []
    current = []

    for token, label in zip(tokens, labels):
        token = token.replace("##", "")
        if token in {"[CLS]", "[SEP]"}:
            continue
        if label.startswith("B-"):
            if current:
                people.append(" ".join(current))
            current = [token]
        elif label.startswith("I-") and current:
            current.append(token)
        else:
            if current:
                people.append(" ".join(current))
            current = []
    if current:
        people.append(" ".join(current))

    return [clean_entity(p) for p in people if len(p.strip()) > 2]

def deduplicate_by_substring(entities: List[str]) -> List[str]:
    entities = sorted(set(entities), key=len, reverse=True)  # longest first
    final = []
    for entity in entities:
        if not any(entity != other and entity in other for other in final):
            final.append(entity)
    return final

def extract_names(text: str) -> Tuple[List[str], List[str]]:
    logger.info("🔍 Running hybrid NER pipeline...")
    people_set = set()
    orgs_set = set()

    chunks = chunk_text(text)

    for chunk in chunks:
        indic_people = extract_indic_names(chunk)
        people_set.update(p for p in indic_people if is_valid_name(p))

        sent = Sentence(chunk)
        flair_tagger.predict(sent)

        for span in sent.get_spans('ner'):
            label = span.get_label("ner").value
            entity = clean_entity(span.text)
            if label == "ORG":
                if is_probable_org(entity):
                    split_orgs = split_merged_orgs(entity)
                    orgs_set.update(split_orgs)
                else:
                    orgs_set.add(entity)
            elif label == "PER" and is_valid_name(entity):
                people_set.add(entity)

    for match in PRIVATE_ORG_REGEX.finditer(text):
        orgs_set.add(clean_entity(match.group(1)))
    for match in COMPANY_REGEX.finditer(text):
        orgs_set.add(clean_entity(match.group(1)))
    for match in CEMENT_LIKE_REGEX.finditer(text):
        orgs_set.add(clean_entity(match.group(1)))

    ms_matches = []
    for match in MS_ORG_REGEX.finditer(text):
        name = clean_entity(match.group(0))
        if 2 <= len(name.split()) <= 6:
            ms_matches.append(name)
    orgs_set.update(ms_matches)

    final_people = deduplicate_by_substring([
        p for p in people_set if is_valid_name(p) and not is_location_like(p)
    ])

    final_orgs = deduplicate_by_substring([
        o for o in orgs_set
        if o not in final_people and len(o) > 3 and is_probable_org(o) and is_clean_org(o)
    ])

    logger.info(f"🧑 People found: {len(final_people)} | 🏢 Organizations found: {len(final_orgs)}")
    return final_people, final_orgs
