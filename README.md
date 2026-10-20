# ScamGuard 🛡️

ScamGuard checks a suspicious message, link, screenshot, or bank account and replies in plain Malay or English with a verdict in under 10 seconds.

## Architecture
One engine, many front doors. Both the Web UI and WhatsApp bot call the same `analyze()` function.
1. **Tier 1**: SQLite database lookup for mule accounts.
2. **Tier 2**: Keyword and regex rule engine.
3. **Tier 3**: URL heuristics (lookalikes, APKs, shorteners).
4. **Tier 4**: LLM intent classifier (only triggered if rule score is 20-80).

## Running Locally (Laptop + ngrok deployment)
1. `pip install -r requirements.txt`
2. Configure `.env` with `OPENAI_API_KEY` and `TWILIO_AUTH_TOKEN`.
3. Start the API: `uvicorn app.main:app --reload`
4. Start the Web UI: `streamlit run web/app.py`
5. Connect WhatsApp: Run `ngrok http 8000` and paste the URL into your Twilio Sandbox webhook.

*Note: All mule data in the UI is seeded mock data for demo purposes.*