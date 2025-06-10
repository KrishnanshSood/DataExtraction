import re

SECTION_PATTERN = re.compile(
    r"""
    (Section\s+\d+[A-Z]?(?:\(\w+\))?)             # Group 1: Section number like 'Section 46(A)' or 'Section 80C'
    \s+(?:of|under)?\s*                           # Match 'of' or 'under' (optional)
    (?:the\s+)?                                   # Optional 'the'
    ([A-Z][a-zA-Z/&\-,.\s]+?)                     # Group 2: Act/Code name
    \s*(Act|Code|Regulation|Amendment|Rules)?     # Group 3: Act type (optional)
    ,?\s*(\d{4})?                                 # Group 4: Year (optional)
    (?=\W|$)                                      # Ensure non-word char or end of string follows
    """,
    re.IGNORECASE | re.VERBOSE
)

def extract_acts_sections(text: str):
    matches = SECTION_PATTERN.findall(text)
    results = []
    for section, act_name, act_type, year in matches:
        parts = [section, "of", act_name.strip()]
        if act_type:
            parts.append(act_type.strip())
        if year:
            parts.append(year)
        results.append(" ".join(parts))
    return results
