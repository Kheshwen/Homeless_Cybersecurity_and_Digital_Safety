import time
from collections import defaultdict
from fastapi import APIRouter, Depends, Request, Response, Form

# Simple in-memory rate limiter: {phone_number: [timestamp1, timestamp2, ...]}
rate_limits = defaultdict(list)

def is_rate_limited(phone_number: str) -> bool:
    now = time.time()
    # Keep only timestamps from the last 60 seconds
    rate_limits[phone_number] = [t for t in rate_limits[phone_number] if now - t < 60]
    if len(rate_limits[phone_number]) >= 10: # 10 checks per minute per number
        return True
    rate_limits[phone_number].append(now)
    return False

# ... inside your @router.post("/whatsapp-webhook") function ...

    if is_rate_limited(From):
        resp = MessagingResponse()
        resp.message("You have reached the limit of 10 checks per minute. Please try again later.")
        return Response(content=str(resp), media_type="application/xml")

    # Truncate very long inputs to 2,000 characters
    if len(input_text) > 2000:
        input_text = input_text[:2000]