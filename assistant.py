import asyncio
import os
import time
import subprocess

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.stream import StreamAudioEnded
import google.generativeai as genai
from edge_tts import Communicate

import speech_recognition as sr
from pydub import AudioSegment

# ================= CONFIG =================

API_ID = 26537336
API_HASH = "931051ff310e587ac41154ed3d516f06"
STRING_SESSION = ""          # REQUIRED
GEMINI_KEY = ""              # REQUIRED
TARGET_CHAT = -1003228624224

COOLDOWN_TIME = 10

# ================= STATE =================

user_cooldowns = {}
is_busy = False

# ================= AI SETUP =================

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-pro")
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

async def ai_reply_to_voice(text: str):
    """Generate AI response + TTS"""
    response = await asyncio.to_thread(model.generate_content, text)
    ai_text = response.text.strip()

    output = "ai_reply.mp3"
    tts = Communicate(ai_text, voice="hi-IN-MadhurNeural")
    await tts.save(output)

    return output, ai_text


def speech_to_text(input_file: str):
    """Convert voice to text"""
    wav = "temp.wav"
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


def yt_stream_url(query: str, video=False):
    """Get YouTube stream URL safely"""
    format_code = "best[height<=720]" if video else "bestaudio"

    cmd = [
        "yt-dlp",
        "-f", format_code,
        "--get-url",
        f"ytsearch:{query}",
    ]

    result = subprocess.check_output(cmd, text=True).splitlines()
    return result[0]


# ================= FEATURES =================

@app.on_message(filters.voice & filters.chat(TARGET_CHAT))
async def voice_ai_handler(_, message):
    global is_busy

    uid = message.from_user.id
    now = time.time()

    if is_busy:
        return

    if uid in user_cooldowns and now - user_cooldowns[uid] < COOLDOWN_TIME:
        return

    is_busy = True
    user_cooldowns[uid] = now

    status = await message.reply("👂 Sun raha hoon...")

    try:
        voice_path = await message.download()
        text = speech_to_text(voice_path)

        if not text:
            return await status.edit("❌ Awaz clear nahi thi bhai")

        await status.edit(f"📝 Tumne bola:\n`{text}`\n\n🤔 Soch raha hoon...")

        audio, reply = await ai_reply_to_voice(text)

        await calls.play(
            TARGET_CHAT,
            AudioPiped(audio),
        )

        await status.edit(f"🎙️ **AI Reply:**\n{reply}")

    except Exception as e:
        await status.edit(f"❌ Error:\n`{e}`")

    finally:
        is_busy = False
        for f in ("ai_reply.mp3", voice_path):
            if f and os.path.exists(f):
                os.remove(f)


@app.on_message(filters.command("play", ".") & filters.me)
async def play_music(_, message):
    if len(message.command) < 2:
        return await message.edit("🎵 Gane ka naam likh bhai")

    query = message.text.split(None, 1)[1]
    await message.edit(f"🎵 Play kar raha hoon:\n`{query}`")

    url = yt_stream_url(query)
    await calls.play(TARGET_CHAT, AudioPiped(url))


@app.on_message(filters.command("vplay", ".") & filters.me)
async def play_video(_, message):
    if len(message.command) < 2:
        return await message.edit("🎬 Video ka naam toh do")

    query = message.text.split(None, 1)[1]
    await message.edit(f"🎬 Video play ho raha hai:\n`{query}`")

    url = yt_stream_url(query, video=True)

    await calls.play(
        TARGET_CHAT,
        AudioVideoPiped(url, url),
    )


# ================= RUN =================

async def main():
    await app.start()
    await calls.start()

    print("🚀 AI Voice + Music Assistant LIVE")

    try:
        await calls.join_group_call(
            TARGET_CHAT,
            AudioPiped(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            ),
        )
    except Exception:
        pass

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())