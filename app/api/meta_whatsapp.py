import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.whatsapp import detect_lang, is_rate_limited
from app.core.analyzer import analyze
from app.core.formatter import format_whatsapp
from app.db.models import CheckLog
from app.db.session import get_db

load_dotenv()
router = APIRouter()

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v21.0")  # copy the version from your Meta dashboard

HELP_MSG = ("Send me a suspicious message, link, phone number or bank account to check.\n"
            "Hantar mesej, pautan, nombor telefon atau akaun bank yang mencurigakan untuk disemak.")
RATE_MSG = ("You have reached the limit of 10 checks per minute. Please try again later.\n"
            "Anda telah mencapai had 10 semakan seminit. Sila cuba sebentar lagi.")
IMG_MSG = ("Screenshots aren't supported on this channel yet. Please paste the message text instead.\n"
           "Tangkap layar belum disokong. Sila tampal teks mesej.")


async def send_text(to: str, text: str):
    if not (META_TOKEN and PHONE_ID):
        print("META_ACCESS_TOKEN or META_PHONE_NUMBER_ID is missing from .env")
        return
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {META_TOKEN}"},
            json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}},
        )
    if r.status_code >= 400:
        print("Meta send error:", r.status_code, r.text)


@router.get("/meta-webhook")
async def verify_meta_webhook(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and VERIFY_TOKEN and p.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=p.get("hub.challenge", ""), media_type="text/plain")
    return Response(content="Verification failed", status_code=403)


@router.post("/meta-webhook")
async def handle_meta_message(request: Request, db: Session = Depends(get_db)):
    start = time.time()
    body = await request.json()
    try:
        value = body["entry"][0]["changes"][0]["value"]
        messages = value.get("messages")
        if not messages:  # delivery/read status updates
            return {"status": "ignored"}

        msg = messages[0]
        sender = msg["from"]
        text = msg.get("text", {}).get("body", "").strip() if msg.get("type") == "text" else ""
        
        if is_rate_limited(sender):
            await send_text(sender, RATE_MSG)
        elif msg.get("type") != "text":
            await send_text(sender, IMG_MSG)
        elif not text:
            await send_text(sender, HELP_MSG)
        else:
            text = text[:2000]
            verdict = analyze(text, detect_lang(text))
            db.add(CheckLog(channel="meta", input_type="text", verdict=verdict.level,
                            score=verdict.score, latency_ms=int((time.time() - start) * 1000)))
            db.commit()
            await send_text(sender, format_whatsapp(verdict))
    except Exception as e:
        print("Meta webhook error:", e)
    return {"status": "ok"}