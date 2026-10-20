import time
from collections import defaultdict

import httpx
from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings
from app.core.analyzer import analyze
from app.core.formatter import format_whatsapp
from app.db.models import CheckLog
from app.db.session import get_db

router = APIRouter()

# Simple in-memory rate limiter: {phone_number: [timestamps]}
rate_limits: dict[str, list[float]] = defaultdict(list)

MALAY_HINTS = {"yang", "dan", "anda", "akaun", "sila", "bayar", "tunggakan", "segera",
               "untuk", "ini", "dengan", "kepada", "telah", "wang", "tidak", "boleh", "apa"}


def is_rate_limited(phone_number: str) -> bool:
    now = time.time()
    timestamps = [t for t in rate_limits[phone_number] if now - t < 60]
    if not timestamps:
        rate_limits.pop(phone_number, None)
    else:
        rate_limits[phone_number] = timestamps

    if len(rate_limits.get(phone_number, [])) >= 10:
        return True
    rate_limits[phone_number].append(now)
    return False


def detect_lang(text: str) -> str:
    words = set(text.lower().split())
    return "ms" if len(words & MALAY_HINTS) >= 1 else "en"


def reply(message: str) -> Response:
    resp = MessagingResponse()
    resp.message(message)
    return Response(content=str(resp), media_type="application/xml")


@router.post("/whatsapp-webhook")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    db: Session = Depends(get_db),
):
    start = time.time()

    if is_rate_limited(From):
        return reply("You have reached the limit of 10 checks per minute. Please try again later.\n"
                     "Anda telah mencapai had 10 semakan seminit. Sila cuba sebentar lagi.")

    input_text = Body.strip()
    input_type = "text"

    # Screenshot: download from Twilio and OCR it
    if NumMedia > 0 and MediaUrl0:
        input_type = "image"
        try:
            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as http:
                media = await http.get(MediaUrl0, auth=auth)
            from app.core.ocr import extract_text_from_image
            input_text = (input_text + " " + extract_text_from_image(media.content)).strip()
        except Exception:
            if not input_text:
                return reply("Sorry, I could not read that image. Please paste the message text instead.\n"
                             "Maaf, saya tidak dapat membaca gambar itu. Sila tampal teks mesej.")

    if not input_text:
        return reply("Send me a suspicious message, link, phone number or bank account to check.\n"
                     "Hantar mesej, pautan, nombor telefon atau akaun bank yang mencurigakan untuk disemak.")

    input_text = input_text[:2000]  # truncate very long inputs
    verdict = analyze(input_text, detect_lang(input_text))

    db.add(CheckLog(channel="whatsapp", input_type=input_type, verdict=verdict.level,
                    score=verdict.score, latency_ms=int((time.time() - start) * 1000)))
    db.commit()

    return reply(format_whatsapp(verdict))
