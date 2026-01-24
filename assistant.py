import asyncio
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, DecodingParameters
import google.generativeai as genai
from edge_tts import Communicate
import speech_recognition as sr

# --- CONFIG ---
API_ID = 27795164 
API_HASH = "931051ff310e587ac41154ed3d516f06"
STRING_SESSION = ""
GEMINI_KEY = ""
TARGET_CHAT = -1003228624224

# AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
recognizer = sr.Recognizer()

app = Client("LiveAssistant", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
call_py = PyTgCalls(app)

# --- VOICE LOGIC ---

async def get_ai_reply(text):
    """Gemini se jawab aur Voice generation"""
    response = model.generate_content(text)
    ai_text = response.text
    path = "reply.mp3"
    comm = Communicate(ai_text, "hi-IN-MadhurNeural")
    await comm.save(path)
    return path, ai_text

# --- REAL-TIME LISTENING (EXPERIMENTAL) ---
# Note: Telegram VC se live audio nikalna heavy process hai. 
# Yeh function tab trigger hoga jab koi kuch bolega.

@call_py.on_stream_audio_ended()
async def stream_ended(client, update):
    # Gana ya voice khatam hone par wapas listening mode ya default sound
    pass

@app.on_message(filters.command("live", ".") & filters.me)
async def start_live(client, message):
    await call_py.join_group_call(
        message.chat.id,
        AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    )
    await message.edit("🎙️ Assistant Live hai! Ab jo bhi bologe main sununga.")

# Music command
@app.on_message(filters.command("play", ".") & filters.me)
async def play_music(client, message):
    song = message.text.split(None, 1)[1]
    os.system(f'yt-dlp -f "bestaudio" --get-url "ytsearch:{song}" > link.txt')
    with open("link.txt", "r") as f:
        link = f.read().strip()
    await call_py.play(message.chat.id, AudioPiped(link))
    await message.edit(f"🎶 Playing: {song}")

# AI Voice Interaction
@app.on_message(filters.command("ai", ".") & filters.me)
async def manual_ai(client, message):
    query = message.text.split(None, 1)[1]
    audio, txt = await get_ai_reply(query)
    await call_py.play(message.chat.id, AudioPiped(audio))
    await message.edit(f"🤖 {txt}")

async def main():
    await app.start()
    await call_py.start()
    print("🚀 Live Assistant Ready!")
    # Khulte hi join hone ka logic
    try:
        await call_py.join_group_call(TARGET_CHAT, AudioPiped("https://example.com/silent.mp3"))
    except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
