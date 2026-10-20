import re

def normalize_text(text: str) -> str:
    """Lowercases text and collapses multiple whitespaces into one."""
    return re.sub(r'\s+', ' ', text.lower()).strip()

def normalize_number(val: str) -> str:
    """Removes spaces and dashes, and replaces +60 or 60 prefixes with 0."""
    cleaned = re.sub(r'[\s\-]', '', val)
    if cleaned.startswith('+60'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('60') and not cleaned.startswith('601'):
        # Safety check: replace 60 if it's a country code for mobile
        cleaned = '0' + cleaned[2:]
    return cleaned