# ScamGuard

ScamGuard checks a suspicious message, link, screenshot, or bank account and replies in plain Malay or English with a verdict in under 10 seconds.

## Architecture

One engine, many front doors. Both the Web UI, Meta WhatsApp Cloud API webhook, and Telegram bot call the same `analyze()` function.

1. **Tier 1**: SQLite database lookup for mule accounts.
2. **Tier 2**: Keyword and regex rule engine.
3. **Tier 3**: URL heuristics (lookalikes, APKs, shorteners).
4. **Tier 4**: LLM intent classifier (only triggered if rule score is 20-80).

---

## Running Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```
2. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```env
   OPENAI_API_KEY=your-openai-key-here
   META_ACCESS_TOKEN=your-meta-token-here
   META_PHONE_NUMBER_ID=your-phone-id-here
   META_VERIFY_TOKEN=scamguard_secret_123
   TELEGRAM_BOT_TOKEN=your-telegram-token-here
   ```
3. **Start the API (auto-seeds database and boots Telegram bot in background):**
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Start the Web UI:**
   ```bash
   streamlit run web/app.py
   ```
5. **Connect Meta WhatsApp Cloud API (Optional):**
   Run `ngrok http 8000` and paste the URL with `/meta-webhook` into your Meta Developer App Webhook settings.

*Note: All mule data in the UI is seeded mock data for demo purposes.*