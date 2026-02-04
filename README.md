# Assistant-

Telegram voice assistant using Pyrogram, PyTgCalls, and Gemini (free-tier friendly).

## Setup

1. Install dependencies.
2. Configure environment variables:

```bash
export API_ID="your_telegram_api_id"
export API_HASH="your_telegram_api_hash"
export STRING_SESSION="your_pyrogram_string_session"
export GEMINI_KEY="your_gemini_api_key"
export TARGET_CHAT="-1001234567890"
```

## Run

```bash
python assistant.py
```

## Heroku Deploy

This repository is Heroku-ready with a worker dyno.

1. Create a Heroku app and add the required config vars:
   - `API_ID`
   - `API_HASH`
   - `STRING_SESSION`
   - `GEMINI_KEY`
   - `TARGET_CHAT`
2. Deploy the repo to Heroku.
3. Scale the worker dyno:

```bash
heroku ps:scale worker=1
```
