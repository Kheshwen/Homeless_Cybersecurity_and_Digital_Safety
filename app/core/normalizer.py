import re


def normalize_text(text: str) -> str:
    """Lowercases text and collapses multiple whitespaces into one."""
    return re.sub(r'\s+', ' ', text.lower()).strip()


def normalize_number(val: str) -> str:
    """Removes spaces and dashes, and converts the +60 / 60 country code to a leading 0.

    Malaysian mobile numbers look like 601XXXXXXXX (11-12 digits) with the country code.
    Bank accounts that happen to start with 60 are left alone unless they match that shape.
    """
    cleaned = re.sub(r'[\s\-]', '', val)
    if cleaned.startswith('+60'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('601') and 11 <= len(cleaned) <= 12:
        cleaned = '0' + cleaned[2:]
    return cleaned
