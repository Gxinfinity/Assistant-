import asyncio
import os
import time
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, VideoPiped
import google.generativeai as genai
from edge_tts import Communicate
import speech_recognition as sr
from pydub import AudioSegment

# --- CONFIGURATION ---
API_ID = 26537336 
API_HASH = "931051ff310e587ac41154ed3d516f06"
STRING_SESSION = "" 
GEMINI_KEY = ""
TARGET_CHAT = -1003228624224 

# Anti-Spam & Status
user_cooldowns = {}
COOLDOWN_TIME = 10
is_busy = False 

# AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
recognizer = sr.Recognizer()

app = Client("MyAssistant", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
call_py = PyTgCalls(app)

# --- UTILS ---

async def get_ai_response(text):
    response = model.generate_content(text)
    ai_text = response.text
    path = "ai_reply.mp3"
    communicate = Communicate(ai_text, "hi-IN-MadhurNeural")
    await communicate.save(path)
    return path, ai_text

def transcribe_audio(file_path):
    w_path = "temp.wav"
    AudioSegment.from_file(file_path).export(w_path, format="wav")
    with sr.AudioFile(w_path) as source:
        data = recognizer.record(source)
        try: return recognizer.recognize_google(data, language="hi-IN")
        except: return None

# --- FEATURES ---

# 1. Voice Recognition & AI Reply
@app.on_message(filters.voice & filters.chat(TARGET_CHAT))
async def handle_voice(client, message):
    global is_busy
    uid = message.from_user.id
    if is_busy or (uid in user_cooldowns and time.time() - user_cooldowns[uid] < COOLDOWN_TIME):
        return
    
    is_busy = True
    user_cooldowns[uid] = time.time()
    msg = await message.reply("👂 Sun raha hoon...")
    
    try:
        file_path = await message.download()
        text = transcribe_audio(file_path)
        if text:
            await msg.edit(f"📝 Tune kaha: `{text}`\n🤔 Soch raha hoon...")
            audio_path, ai_text = await get_ai_response(text)
            await call_py.play(TARGET_CHAT, AudioPiped(audio_path))
            await msg.edit(f"🎙️ **AI:** {ai_text}")
        else:
            await msg.edit("Awaz nahi aayi bahi!")
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e: print(e)
    finally: is_busy = False

# 2. Video Playback Command (.vplay [song name])
@app.on_message(filters.command("vplay", ".") & filters.me)
async def vplay_cmd(client, message):
    if len(message.command) < 2:
        return await message.edit("Gane ka naam toh de!")
    
    query = message.text.split(None, 1)[1]
    await message.edit(f"🎬 Video play kar raha hoon: `{query}`")
    
    # Get direct video and audio link
    os.system(f'yt-dlp -f "best[height<=720]" --get-url "ytsearch:{query}" > vlink.txt')
    with open("vlink.txt", "r") as f:
        links = f.readlines()
        v_url = links[0].strip()
    
    await call_py.play(
        TARGET_CHAT,
        AudioPiped(v_url),
        VideoPiped(v_url)
    )

# 3. Normal Music Play (.play [song name])
@app.on_message(filters.command("play", ".") & filters.me)
async def play_cmd(client, message):
    query = message.text.split(None, 1)[1]
    await message.edit(f"🎵 Gana baja raha hoon: `{query}`")
    os.system(f'yt-dlp -f "bestaudio" --get-url "ytsearch:{query}" > alink.txt')
    with open("alink.txt", "r") as f:
        a_url = f.read().strip()
    await call_py.play(TARGET_CHAT, AudioPiped(a_url))

# --- RUN ---
async def main():
    await app.start()
    await call_py.start()
    print("🚀 All-in-One Video AI Assistant is LIVE!")
    try:
        await call_py.join_group_call(TARGET_CHAT, AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"))
    except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
