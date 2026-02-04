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

## Docker

Build and run locally:

```bash
docker build -t assistant-bot .
docker run --rm \
  -e API_ID=... \
  -e API_HASH=... \
  -e STRING_SESSION=... \
  -e GEMINI_KEY=... \
  -e TARGET_CHAT=... \
  assistant-bot
```

## Heroku Deploy

This repository is Heroku-ready with a worker dyno.

### Deploy via Heroku Button (app.json)

1. Click the Heroku deploy button (add one in your fork if needed) or use:

```bash
heroku create
git push heroku main
```

2. Add the required config vars:
   - `API_ID`
   - `API_HASH`
   - `STRING_SESSION`
   - `GEMINI_KEY`
   - `TARGET_CHAT`
3. Scale the worker dyno:

```bash
heroku ps:scale worker=1
```

### Deploy via Heroku CLI (manual)

```bash
heroku create
heroku config:set API_ID=... API_HASH=... STRING_SESSION=... GEMINI_KEY=... TARGET_CHAT=...
git push heroku main
heroku ps:scale worker=1
```
