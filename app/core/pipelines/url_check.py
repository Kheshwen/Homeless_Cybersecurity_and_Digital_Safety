import os
import json
import Levenshtein

def load_official_domains() -> list[str]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path = os.path.join(base_dir, "data", "official_domains.json")
    with open(path, "r") as f:
        return json.load(f)

def check_urls(urls: list[str]) -> tuple[int, list[str]]:
    if not urls:
        return 0, []
        
    official_domains = load_official_domains()
    shorteners = ["bit.ly", "tinyurl", "s.id", "t.co"]
    suspicious_keywords = ["verify", "secure", "update", "login"]
    
    max_score = 0
    reasons = []
    
    for url in urls:
        lower_url = url.lower()
        
        # Safe domain bypass (still checks rest of message)
        if any(d in lower_url for d in official_domains) or ".gov.my" in lower_url:
            continue
            
        if ".apk" in lower_url:
            max_score = max(max_score, 90)
            reasons.append("Link initiates a direct .apk file download.")
            
        if any(s in lower_url for s in shorteners):
            max_score = max(max_score, 25)
            reasons.append("Uses a URL shortener to mask the destination.")
            
        # Lookalike and brand keyword checks
        for domain in official_domains:
            brand_name = domain.split('.')[0]
            
            if brand_name in lower_url and any(k in lower_url for k in suspicious_keywords):
                max_score = max(max_score, 80)
                reasons.append(f"Spoofs {brand_name} with suspicious keywords.")
                
            # Levenshtein distance check on domain core
            core_url_segment = lower_url.split('/')[0].replace("https://", "").replace("http://", "")
            if Levenshtein.distance(domain, core_url_segment) <= 3 and domain not in lower_url:
                max_score = max(max_score, 80)
                reasons.append(f"Lookalike domain closely resembling {domain}.")
                
    return max_score, reasons