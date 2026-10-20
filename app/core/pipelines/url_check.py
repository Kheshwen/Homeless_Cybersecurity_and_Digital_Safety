import json
from urllib.parse import urlparse
import Levenshtein
from app.config import DATA_DIR

SHORTENERS = {"bit.ly", "tinyurl.com", "s.id", "t.co", "t.ly", "cutt.ly", "is.gd", "rebrand.ly"}
SUSPICIOUS_WORDS = ["verify", "secure", "update", "login", "claim", "refund"]

_official_cache: list[str] | None = None


def load_official_domains() -> list[str]:
    global _official_cache
    if _official_cache is None:
        with open(DATA_DIR / "official_domains.json", "r", encoding="utf-8-sig") as f:
            _official_cache = [d.lower() for d in json.load(f)]
    return _official_cache


def get_host(url: str) -> str:
    """Returns the lowercase hostname of a URL (works with or without http://)."""
    raw = url.strip()
    if "://" not in raw:
        raw = "http://" + raw
    host = (urlparse(raw).hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def is_official_host(host: str, official_domains: list[str]) -> bool:
    """True only if the host IS an official domain or a real subdomain of one."""
    if host.endswith(".gov.my") or host == "gov.my":
        return True
    return any(host == d or host.endswith("." + d) for d in official_domains)


def check_urls(urls: list[str]) -> tuple[int, list[str]]:
    if not urls:
        return 0, []

    official_domains = load_official_domains()
    max_score = 0
    reasons: list[str] = []

    def flag(score: int, reason: str):
        nonlocal max_score
        max_score = max(max_score, score)
        if reason not in reasons:
            reasons.append(reason)

    for url in urls:
        lower_url = url.lower()
        host = get_host(url)
        if not host:
            continue

        # Real official site: skip (the rest of the message is still checked elsewhere)
        if is_official_host(host, official_domains):
            continue

        path_and_query = lower_url.split(host, 1)[-1]

        if ".apk" in path_and_query or host.endswith(".apk"):
            flag(90, "Link downloads an .apk app file, which can steal your banking details.")

        if host in SHORTENERS:
            flag(25, "Uses a short link that hides the real website.")

        for domain in official_domains:
            brand = domain.split(".")[0]

            # e.g. maybank2u.com.my.evil.com or evil.com/maybank2u.com.my
            if domain in lower_url:
                flag(85, f"Pretends to be {domain} but the real website is {host}.")
                continue

            # e.g. maybank2u-verify.com, secure-maybank2u.net
            if len(brand) >= 4 and brand in host:
                flag(80 if any(w in lower_url for w in SUSPICIOUS_WORDS) else 60,
                     f"Website name copies {brand} but is not the official site.")
                continue

            # e.g. rnaybank2u.com.my (one or two letters changed)
            if abs(len(host) - len(domain)) <= 2 and Levenshtein.distance(domain, host) <= 2:
                flag(80, f"Lookalike website closely resembling {domain}.")

    return max_score, reasons
