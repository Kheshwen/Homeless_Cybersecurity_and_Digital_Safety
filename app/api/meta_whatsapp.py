import os
import httpx
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.core.analyzer import analyze
from app.core.formatter import format_whatsapp
from app.db.session import get_db

router = APIRouter()

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "scamguard_secret_123")

@router.get("/meta-webhook")
async def verify_meta_webhook(request: Request):
    """Handles Meta's initial webhook verification handshake."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain", status_code=200)
    return Response(content="Verification failed", status_code=403)

@router.post("/meta-webhook")
async def handle_meta_message(request: Request, db: Session = Depends(get_db)):
    """Receives incoming messages from Meta WhatsApp Cloud API."""
    body = await request.json()
    
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages")
        
        if not messages:
            return {"status": "ignored"}
            
        msg_data = messages[0]
        sender_phone = msg_data.get("from")
        msg_type = msg_data.get("type")
        
        input_text = ""
        if msg_type == "text":
            input_text = msg_data.get("text", {}).get("body", "").strip()
        elif msg_type == "image":
            # Optional: Download image media via Meta Graph API if needed
            input_text = "[User sent a screenshot image]"
            
        if not input_text:
            input_text = "Please send text messages to verify."
            
        # Run through ScamGuard analysis engine
        verdict = analyze(input_text, "ms" if "yang" in input_text.lower() else "en")
        reply_text = format_whatsapp(verdict)
        
        # Send response back via Meta Graph API
        if META_TOKEN and PHONE_ID:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages",
                    headers={"Authorization": f"Bearer {META_TOKEN}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": sender_phone,
                        "text": {"body": reply_text}
                    },
                    timeout=10.0
                )
    except Exception as e:
        print(f"Meta webhook error: {e}")
        
    return {"status": "ok"}