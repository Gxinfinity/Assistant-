import asyncio
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.types.stream import StreamAudioEnded
import google.generativeai as genai
from edge_tts import Communicate

# --- CONFIGURATION ---
API_ID =  27795164           
API_HASH = "931051ff310e587ac41154ed3d516f06"    
STRING_SESSION = "" 
GEMINI_KEY = "" 
TARGET_CHAT =  -1003228624224    
# AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Client("Assistant", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
# Hum yahan ntgcalls engine ka reference de rahe hain compatibility ke liye
call_py = PyTgCalls(app)

# --- TEXT TO SPEECH (Alexa Voice) ---
async def generate_voice(text):
    path = "bot_reply.mp3"
    # 'hi-IN-MadhurNeural' ek natural sounding male voice hai
    comm = Communicate(text, "hi-IN-MadhurNeural")
    await comm.save(path)
    return path

# --- COMMANDS ---

@app.on_message(filters.command("ask", ".") & filters.me)
async def ask_ai(client, message):
    if len(message.command) < 2:
        return await message.edit("Bhai, kuch toh pooch?")
    
    query = message.text.split(None, 1)[1]
    await message.edit("⌛ Assistant soch raha hai...")
    
    try:
        # AI Response
        response = model.generate_content(query)
        full_text = response.text
        
        # Voice generation
        audio_file = await generate_voice(full_text)
        
        # Play in VC
        await call_py.change_stream(message.chat.id, AudioPiped(audio_file))
        await message.edit(f"🎙️ **AI:** {full_text}")
    except Exception as e:
        await message.edit(f"❌ Error: {e}")

@app.on_message(filters.command("play", ".") & filters.me)
async def play_music(client, message):
    if len(message.command) < 2:
        return await message.edit("Gane ka naam?")
    
    song = message.text.split(None, 1)[1]
    await message.edit(f"🔍 Searching: `{song}`")
    
    # yt-dlp to get direct stream link
    os.system(f'yt-dlp -f "bestaudio" --get-url "ytsearch:{song}" > link.txt')
    with open("link.txt", "r") as f:
        link = f.read().strip()
    
    await call_py.change_stream(message.chat.id, AudioPiped(link))
    await message.edit(f"🎶 Playing: **{song}**")

# --- AUTO JOIN ON START ---
async def start_assistant():
    await app.start()
    await call_py.start()
    print("🚀 AI Assistant is Live!")
    
    try:
        # Script khulte hi join kar lega
        await call_py.join_group_call(
            TARGET_CHAT, 
            AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
        )
        print("✅ Joined Voice Chat!")
    except:
        pass
        
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_assistant())
