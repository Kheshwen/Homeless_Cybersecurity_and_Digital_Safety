# 🛡️ ScamGuard by Team Homeless

**ScamGuard** is an AI-powered cybersecurity assistant designed to protect older adults and digital newcomers in Malaysia from online fraud. It verifies suspicious messages, links, screenshots, and bank accounts in under 10 seconds.

Built for the **UTP Codefest Hackathon 2026 (Track 4: Cybersecurity)**.

---

## 🧠 System Architecture

ScamGuard uses a **Hybrid 4-Tier Defense Engine** to ensure high accuracy, low latency, and graceful degradation if external APIs fail:

1. **Tier 1 (Database Match):** Instantly cross-references phone numbers and bank accounts against a seeded SQLite database of PDRM Semakmule and MCMC blacklists.
2. **Tier 2 (Heuristic Rules):** Uses regex and keyword mapping to detect common scam patterns (e.g., APK payloads, TAC requests, fake LHDN warnings).
3. **Tier 3 (URL Analysis):** Uses Levenshtein distance to detect lookalike phishing domains (e.g., `maybank2u-secure.com`).
4. **Tier 4 (LLM Intent):** If a message is ambiguous (Score 20-80), it falls back to OpenAI (`gpt-4o-mini`) for semantic analysis.

**One Engine, Three Front Doors:** The exact same analysis engine powers a Streamlit Web Dashboard, a Meta WhatsApp Cloud bot, and a Telegram bot.

---

## ⚙️ Prerequisites

- Python 3.9+
- [ngrok](https://ngrok.com/) (For WhatsApp Meta Webhook)
- OpenAI API Key
- Meta Developer Account (For WhatsApp Cloud API)
- Telegram Bot Token (via @BotFather)

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
Ensure your `.env` file contains:
```env
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///./scamguard.db

# Meta WhatsApp Cloud API
META_ACCESS_TOKEN=your_meta_token
META_PHONE_NUMBER_ID=your_phone_id
META_VERIFY_TOKEN=scamguard_secret_123

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 3. Run the Services (Open 3 Terminals)

**Terminal 1: Start the Backend & Telegram Bot**
This starts the FastAPI server, auto-seeds the mock database, and boots the Telegram long-polling bot in the background.
```bash
uvicorn app.main:app --reload
```

**Terminal 2: Start the Web UI**
This launches the Streamlit dashboard for browser-based testing.
```bash
streamlit run web/app.py
```

**Terminal 3: Connect WhatsApp via Ngrok**
Expose your local server to the public internet so Meta can send webhooks.
```bash
ngrok http 8000
```
*Take the generated HTTPS URL (e.g., `https://xxxx.ngrok-free.app`), append `/meta-webhook`, and paste it into your Meta Developer WhatsApp Webhook settings!*

---

## 🧪 Testing the Engine

Try sending this message to the WhatsApp bot, Telegram bot, or Web UI to trigger a **🔴 DANGER** alert:

> *"AMARAN LHDN: Anda mempunyai tunggakan cukai RM 1,850. Sila muat turun aplikasi semakan di http://hasil-cukai-my.com/lhdn.apk atau akaun bank anda akan dibekukan."*

---

**Built with ❤️ by Team Homeless**
