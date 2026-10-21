import os
import time

import httpx
from dotenv import load_dotenv

from app.api.whatsapp import detect_lang, is_rate_limited
from app.core.analyzer import analyze
from app.core.formatter import format_whatsapp
from app.db.models import CheckLog
from app.db.session import get_db

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is missing from .env")

API = f"https://api.telegram.org/bot{TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"

WELCOME = ("Send me a suspicious message, link, phone number or bank account to check.\n"
           "Hantar mesej, pautan, nombor telefon atau akaun bank yang mencurigakan untuk disemak.")
RATE_MSG = ("You have reached the limit of 10 checks per minute. Please try again later.\n"
            "Anda telah mencapai had 10 semakan seminit. Sila cuba sebentar lagi.")
IMG_FAIL = ("Sorry, I could not read that image. Please paste the message text instead.\n"
            "Maaf, saya tidak dapat membaca gambar itu. Sila tampal teks mesej.")


def send(client, chat_id, text):
    r = client.post(f"{API}/sendMessage",
                    data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    if r.status_code != 200:  # Markdown failed, so resend as plain text
        client.post(f"{API}/sendMessage", data={"chat_id": chat_id, "text": text})


def read_photo(client, sizes):
    file_id = sizes[-1]["file_id"]  # the largest version of the photo
    info = client.get(f"{API}/getFile", params={"file_id": file_id}).json()
    path = info["result"]["file_path"]
    data = client.get(f"{FILE_API}/{path}").content
    from app.core.ocr import extract_text_from_image
    return extract_text_from_image(data)


def log_check(input_type, verdict, start):
    try:
        db = next(get_db())
        try:
            db.add(CheckLog(channel="telegram", input_type=input_type, verdict=verdict.level,
                            score=verdict.score, latency_ms=int((time.time() - start) * 1000)))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print("Log error:", e)


def handle(client, msg):
    chat_id = msg["chat"]["id"]
    start = time.time()
    text = (msg.get("text") or msg.get("caption") or "").strip()

    if text.startswith("/start"):
        send(client, chat_id, WELCOME)
        return
    if is_rate_limited(str(chat_id)):
        send(client, chat_id, RATE_MSG)
        return

    input_type = "text"
    if msg.get("photo"):
        input_type = "image"
        try:
            text = (text + " " + read_photo(client, msg["photo"])).strip()
        except Exception as e:
            print("Image error:", e)
            if not text:
                send(client, chat_id, IMG_FAIL)
                return

    if not text:
        send(client, chat_id, WELCOME)
        return

    text = text[:2000]
    verdict = analyze(text, detect_lang(text))
    log_check(input_type, verdict, start)
    send(client, chat_id, format_whatsapp(verdict))


def main():
    print("Telegram bot running. Press Ctrl+C to stop.")
    offset = None
    with httpx.Client(timeout=40) as client:
        while True:
            try:
                r = client.get(f"{API}/getUpdates", params={"timeout": 30, "offset": offset}).json()
                for update in r.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        try:
                            handle(client, update["message"])
                        except Exception as e:
                            print("Error handling message:", e)
            except Exception as e:
                print("Connection error:", e)
                time.sleep(3)


if __name__ == "__main__":
    main()
    