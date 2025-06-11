import re

SECTION_PATTERN = re.compile(
    r"""
    \b
    (Section|Sec)                                # Section or Sec
    \s+(\d+[A-Z]?[\s]?(?:\(\d+\))?)              # Section number: e.g. 11, 11A, 11 (2)
    \s*(?:of|under)\s*                           # 'of' or 'under'
    (?:the\s+)?                                  # optional 'the'
    ([\w\s,&/()\-.]+?)                           # Act name
    \s+
    (Act|Code|Regulation|Amendment|Rules)        # Act type
    ,?\s*(\d{4})?                                # Optional year
    (?=\s*(?:as\s+amended|thereunder|and\s+rules)?[\.,;:\n]|$)  # Stop after act/year
    """,
    re.IGNORECASE | re.VERBOSE
)

def smart_title(word):
    return word if word in {"&", "(", ")", "-", "/", "of", "the"} else word.capitalize()

def title_case_act_name(name):
    tokens = re.split(r'(\W+)', name)
    return ''.join(smart_title(token) for token in tokens)

def extract_acts_sections(text: str):
    matches = SECTION_PATTERN.findall(text)
    results = set()
    for section_word, section_num, act_name_part, act_type, year in matches:
        section_cleaned = f"Section {section_num}".replace("  ", " ").replace(" (", "(").strip()
        act_name_part = act_name_part.strip()
        act_type = act_type.strip() if act_type else ""
        full_act_name = f"{act_name_part} {act_type}".strip()
        full_act_name_titled = title_case_act_name(full_act_name)

        parts = [section_cleaned, "of", full_act_name_titled]
        if year:
            parts.append(year)
        results.add(" ".join(parts))
    return sorted(results)
