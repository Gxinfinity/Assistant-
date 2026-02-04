import asyncio
import os
import time
import subprocess
import uuid

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

import google.generativeai as genai
from edge_tts import Communicate

import speech_recognition as sr
from pydub import AudioSegment

# ================= CONFIG =================

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")
TARGET_CHAT = int(os.environ.get("TARGET_CHAT", "0"))

COOLDOWN_TIME = 10

# ================= STATE =================

user_cooldowns = {}
is_busy = False

# ================= AI SETUP =================

model = None
recognizer = sr.Recognizer()

# ================= CLIENTS =================

app = Client(
    name="MyAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
)

calls = PyTgCalls(app)

# ================= UTILS =================

def init_ai():
    global model
    genai.configure(api_key=GEMINI_KEY)
    # Free-tier friendly model.
    model = genai.GenerativeModel("gemini-1.5-flash")


async def ai_reply_to_voice(text: str):
    if model is None:
        raise RuntimeError("AI model not initialized.")
    response = await asyncio.to_thread(model.generate_content, text)
    ai_text = response.text.strip()

    output = f"ai_reply_{uuid.uuid4().hex}.mp3"
    tts = Communicate(ai_text, voice="hi-IN-MadhurNeural")
    await tts.save(output)

    return output, ai_text


def speech_to_text(input_file: str):
    wav = f"temp_{uuid.uuid4().hex}.wav"
    AudioSegment.from_file(input_file).export(wav, format="wav")

    with sr.AudioFile(wav) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="hi-IN")
    except Exception:
        return None
    finally:
        if os.path.exists(wav):
            os.remove(wav)


def yt_stream_url(query: str):
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--get-url",
        f"ytsearch:{query}",
    ]
    output = subprocess.check_output(cmd, text=True).splitlines()
    if not output:
        raise subprocess.CalledProcessError(1, cmd, "No URL returned by yt-dlp.")
    return output[0]


def missing_config():
    missing = []
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH")
    if not STRING_SESSION:
        missing.append("STRING_SESSION")
    if not GEMINI_KEY:
        missing.append("GEMINI_KEY")
    if not TARGET_CHAT:
        missing.append("TARGET_CHAT")
    return missing


# ================= FEATURES =================

@app.on_message(filters.voice & filters.chat(TARGET_CHAT))
async def voice_ai_handler(_, message):
    global is_busy

    uid = message.from_user.id
    now = time.time()

    if missing_config():
        return await message.reply("⚠️ Missing configuration. Check environment variables.")

    if is_busy:
        return

    if uid in user_cooldowns and now - user_cooldowns[uid] < COOLDOWN_TIME:
        return

    is_busy = True
    user_cooldowns[uid] = now

    status = await message.reply("👂 Sun raha hoon...")

    voice_path = None
    audio = None
    try:
        voice_path = await message.download()
        text = speech_to_text(voice_path)

        if not text:
            return await status.edit("❌ Awaz clear nahi thi")

        await status.edit(f"📝 Tumne bola:\n{text}\n\n🤔 Soch raha hoon...")

        audio, reply = await ai_reply_to_voice(text)

        await calls.play(
            TARGET_CHAT,
            AudioPiped(audio),
        )

        await status.edit(f"🎙️ AI Reply:\n{reply}")

    except Exception as e:
        await status.edit(f"❌ Error:\n{e}")

    finally:
        is_busy = False
        for f in (voice_path, audio):
            if f and os.path.exists(f):
                os.remove(f)


@app.on_message(filters.command("play", ".") & filters.me)
async def play_music(_, message):
    if len(message.command) < 2:
        return await message.edit("🎵 Gane ka naam likh bhai")

    query = message.text.split(None, 1)[1]
    await message.edit(f"🎵 Play kar raha hoon:\n{query}")

    if missing_config():
        return await message.edit("⚠️ Missing configuration. Check environment variables.")

    try:
        url = yt_stream_url(query)
    except subprocess.CalledProcessError as exc:
        return await message.edit(f"❌ yt-dlp error:\n{exc}")
    await calls.play(TARGET_CHAT, AudioPiped(url))


# ================= RUN =================

async def main():
    missing = missing_config()
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(f"Missing configuration: {missing_list}")

    init_ai()

    await app.start()
    await calls.start()

    print("🚀 AI Voice + Music Assistant LIVE")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
