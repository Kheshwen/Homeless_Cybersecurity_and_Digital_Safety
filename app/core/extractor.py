import re
from app.core.normalizer import normalize_number

def extract_entities(text: str) -> dict:
    """
    Extracts URLs, money amounts, phone numbers, and bank accounts.
    Returns a dictionary of normalized, deduplicated entities.
    """
    entities = {
        "urls": [],
        "phones": [],
        "accounts": [],
        "money_amounts": []
    }
    
    # URL extraction: http/https and bare domains
    url_pattern = r'https?://\S+|\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/\S*)?\b'
    entities["urls"] = list(set(re.findall(url_pattern, text)))
    
    # Money amount extraction: RM followed by digits
    money_pattern = r'RM\s?\d[\d,]*(?:\.\d{2})?'
    entities["money_amounts"] = list(set(re.findall(money_pattern, text, re.IGNORECASE)))

    # Number extraction: Pull clusters of digits, spaces, and dashes
    # Then normalize and classify them to avoid overlaps
    raw_number_clusters = re.findall(r'(?:\+?60)?(?:\d[\s\-]*){9,16}', text)
    
    for raw_cluster in raw_number_clusters:
        norm_val = normalize_number(raw_cluster)
        
        # Phone: starts with 01 and is 10-11 digits
        if norm_val.startswith('01') and 10 <= len(norm_val) <= 11:
            if norm_val not in entities["phones"]:
                entities["phones"].append(norm_val)
        # Bank Account: 9-16 digits, excluding phone numbers
        elif norm_val.isdigit() and 9 <= len(norm_val) <= 16:
            if norm_val not in entities["accounts"]:
                entities["accounts"].append(norm_val)
                
    return entities