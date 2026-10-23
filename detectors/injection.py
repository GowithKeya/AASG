import re

PATTERNS = [
    r"ignore\s+(all\s+|prior\s+|previous\s+|standard\s+)?instructions",
    r"system\s+(override|directive|instruction)",
    r"disregard\s+(all\s+|prior\s+|previous\s+)?(constraints|rules|instructions)",
    r"bypass\s+(safety|security|policy|guard)",
    r"you\s+are\s+now\s+(in\s+developer\s+mode|dan|unrestricted)",
    r"developer\s+mode\s+enabled",
    r"admin\s+directive",
    r"critical\s+alert",
    r"jailbreak",
]


def injection_score(text: str) -> float:
    if not text:
        return 0.0
    text_lower = text.lower()
    matches = 0
    for pattern in PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1
    if matches >= 2:
        return 0.95
    if matches == 1:
        return 0.85
    if "override" in text_lower or "jailbreak" in text_lower:
        return 0.6
    return 0.05
