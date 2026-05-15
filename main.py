# main.py
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import VolumeControl
from pytgcalls.exceptions import NoActiveGroupCall

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from database import save_active_chat, get_active_chat, clear_active_chat
from helpers.downloader import download_youtube_song, cleanup_downloads
from helpers.audio_utils import get_boosted_audio_stream, set_volume_500
from helpers.vc_manager import join_voice_chat, leave_voice_chat, active_calls, current_volume

# Create directories
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Initialize client
if API_ID and API_HASH and PHONE_NUMBER:
    app = Client("oggy_vc_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
else:
    print("\n🔥 OGGY_KILLER ULTIMATE USERBOT 🔥")
    print("="*50)
    API_ID = int(input("API ID: "))
    API_HASH = input("API HASH: ")
    PHONE_NUMBER = input("Phone number (+xxxxxxxxxx): ")
    app = Client("oggy_vc_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

call = PyTgCalls(app)

# Active chat tracking (auto join ke liye)
current_active_chat = get_active_chat()

# ============== MAIN COMMANDS ==============

@app.on_message(filters.command("start", prefixes="."))
async def start_cmd(_, message: Message):
    await message.reply_text("""
╔══════════════════════════════════════╗
║   🔥 **OGGY_KILLER VC USERBOT** 🔥   ║
║   💀 **CHUMT KA DARINDA** 💀          ║
╠══════════════════════════════════════╣
║                                       ║
║ 📌 **COMMANDS:**                      ║
║                                       ║
║ `.join <group_id/username>` - Join VC║
║ `.vcleave` - Leave current VC        ║
║ `.end` - Stop & leave VC             ║
║ `.stop` - Stop playing               ║
║ `.play <song>` - Play song (500%)    ║
║ `.rplay` - Reply to audio            ║
║ `.volume <1-500>` - Set volume       ║
║ `.active` - Show active chat         ║
║                                       ║
╠══════════════════════════════════════╣
║ 🎧 **VOLUME: 500% BOOST**             ║
║ 🔇 **MUTE BYPASS: ACTIVE**            ║
╚══════════════════════════════════════╝
    """)

@app.on_message(filters.command("join", prefixes="."))
async def join_cmd(_, message: Message):
    """VC join karega group mein"""
    global current_active_chat
    
    if len(message.command) < 2:
        await message.reply_text("**GROUP ID/Username DAL!** 🎤\n\n`.join -100123456789`\n`.join oggychat`")
        return
    
    chat_input = message.command[1]
    msg = await message.reply_text("🎧 **VOICE CHAT JOIN KAR RAHA...** 💀")
    
    try:
        chat_id, success, error = await join_voice_chat(call, app, chat_input)
        
        if success:
            current_active_chat = chat_id
            save_active_chat(chat_id)
            
            await msg.edit(f"""
╔══════════════════════════╗
║   🔥 **VC JOINED!** 🔥    ║
╠══════════════════════════╣
║ 📍 Chat ID: `{chat_id}`
║ 🔊 Volume: **500% BOOST**
║ 🔇 Mute Bypass: **ON**
║ 💀 **OGGY_KILLER ACTIVE**
╚══════════════════════════╝
            """)
        else:
            await msg.edit(f"**ERROR:** {error}")
            
    except Exception as e:
        await msg.edit(f"**GALTI:** `{str(e)[:100]}`")

@app.on_message(filters.command(["vcleave", "end", "leave"], prefixes="."))
async def leave_cmd(_, message: Message):
    """VC leave karega"""
    global current_active_chat
    
    chat_id = current_active_chat or get_active_chat()
    
    if not chat_id:
        await message.reply_text("**KOI ACTIVE CHAT NAHI HAI!** 🤡\nPehle `.join` kar.")
        return
    
    msg = await message.reply_text("🔇 **VOICE CHAT LEAVE KAR RAHA...**")
    
    success = await leave_voice_chat(call, chat_id)
    
    if success:
        clear_active_chat()
        current_active_chat = None
        cleanup_downloads()
        await msg.edit("✅ **VC LEFT!** \n\nChala gaya CHUMT KE DUSHMAN se.")
    else:
        await msg.edit("**KOI ACTIVE CALL NAHI THI!**")

@app.on_message(filters.command("stop", prefixes="."))
async def stop_cmd(_, message: Message):
    """Playing stop karega but VC mein rahega"""
    chat_id = current_active_chat or get_active_chat()
    
    if not chat_id:
        await message.reply_text("**KOI ACTIVE CHAT NAHI!**")
        return
    
    if chat_id in active_calls and active_calls[chat_id]:
        await call.leave_group_call(chat_id)
        await call.join_group_call(chat_id, stream_type=0)
        active_calls[chat_id] = None
        cleanup_downloads()
        await message.reply_text("⏹️ **STOPPED!** \n\nGaana band, VC mein abhi bhi hu.")
    else:
        await message.reply_text("**KOI GAANA NAHI BAJ RAHA!**")

@app.on_message(filters.command("play", prefixes="."))
async def play_cmd(_, message: Message):
    """Song play karega 500% volume pe"""
    if len(message.command) < 2:
        await message.reply_text("**KUCH TOH DAL!** 🎧\n\n`.play dilbar dilbar`\n`.play https://youtu.be/xxx`")
        return
    
    chat_id = current_active_chat or get_active_chat()
    
    if not chat_id:
        await message.reply_text("**PEHLE `.join` KAR!** 🎤\nKisi group mein pehle join kar.")
        return
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text("🎧 **500% VOLUME PE SONG LA RAHA...** 😈💀")
    
    try:
        # Leave if already playing
        if chat_id in active_calls and active_calls[chat_id]:
            await call.leave_group_call(chat_id)
            cleanup_downloads()
        
        # Download song
        file_path, title = download_youtube_song(query)
        
        if file_path and title:
            # Play with 500% boost
            await call.join_group_call(
                chat_id,
                get_boosted_audio_stream(file_path, 500),
                stream_type=0
            )
            
            active_calls[chat_id] = file_path
            
            await msg.edit(f"""
╔════════════════════════════╗
║   🔥 **500% VOLUME MODE** 🔥 ║
╠════════════════════════════╣
║ 🎵 **{title[:35]}**
║ 🔊 Volume: **500% (BOOSTED)**
║ 🔇 Mute Bypass: **ACTIVE**
║ 💀 **CHUMT KA DARINDA**
╚════════════════════════════╝
            """)
        else:
            await msg.edit(f"**GAANA NAHI MILA!** 🤡\n{title}")
            
    except NoActiveGroupCall:
        await msg.edit("**VOICE CHAT START KAR!** 🎤\nPehle voice chat enable kar.")
    except Exception as e:
        await msg.edit(f"**ERROR:** `{str(e)[:100]}`")
        await call.leave_group_call(chat_id)
        active_calls[chat_id] = None

@app.on_message(filters.command("rplay", prefixes="."))
async def reply_play_cmd(_, message: Message):
    """Reply wala audio play karega 500% pe"""
    if not message.reply_to_message:
        await message.reply_text("**KISI AUDIO KO REPLY KAR!** 🎧\n\n`.rplay` (reply to audio)")
        return
    
    chat_id = current_active_chat or get_active_chat()
    
    if not chat_id:
        await message.reply_text("**PEHLE `.join` KAR!**")
        return
    
    audio = message.reply_to_message
    if not (audio.audio or audio.voice):
        await message.reply_text("**SIRF AUDIO/VOICE PE REPLY KAR!**")
        return
    
    msg = await message.reply_text("🔊 **500% VOLUME PE AUDIO LAGA RAHA...** 💀")
    
    try:
        if chat_id in active_calls and active_calls[chat_id]:
            await call.leave_group_call(chat_id)
        
        file_path = await audio.download(DOWNLOAD_PATH)
        
        if file_path:
            await call.join_group_call(
                chat_id,
                get_boosted_audio_stream(file_path, 500),
                stream_type=0
            )
            
            active_calls[chat_id] = file_path
            audio_name = audio.audio.file_name if audio.audio else "voice_message"
            
            await msg.edit(f"""
╔════════════════════════════╗
║   🔥 **REPLY AUDIO MODE** 🔥 ║
╠════════════════════════════╣
║ 🎵 **{audio_name[:35]}**
║ 🔊 **500% VOLUME LAGA DIYA**
║ 🔇 **MUTE BYPASS ACTIVE**
║ 💀 **CHUMT KA DARINDA**
╚════════════════════════════╝
            """)
        else:
            await msg.edit("**DOWNLOAD FAIL!**")
            
    except Exception as e:
        await msg.edit(f"**ERROR:** `{str(e)[:100]}`")

@app.on_message(filters.command("volume", prefixes="."))
async def volume_cmd(_, message: Message):
    """Volume set karega 1 se 500 tak"""
    if len(message.command) < 2:
        current = current_volume.get(current_active_chat, 500)
        await message.reply_text(f"**CURRENT VOLUME:** `{current}%`\n\nChange: `.volume 500` (max 500)")
        return
    
    chat_id = current_active_chat or get_active_chat()
    
    if not chat_id:
        await message.reply_text("**KOI ACTIVE CHAT NAHI!**")
        return
    
    try:
        vol = int(message.command[1])
        if vol < 1:
            vol = 1
        if vol > 500:
            vol = 500
        
        current_volume[chat_id] = vol
        
        # Re-process current audio with new volume
        if chat_id in active_calls and active_calls[chat_id]:
            current_file = active_calls[chat_id]
            await call.leave_group_call(chat_id)
            await asyncio.sleep(1)
            
            await call.join_group_call(
                chat_id,
                get_boosted_audio_stream(current_file, vol),
                stream_type=0
            )
        
        await message.reply_text(f"""
🔊 **VOLUME UPDATED!**

📊 From: `{current_volume.get(chat_id, 500)}%`
🔊 To: `{vol}%`
💀 Boost: **{vol/100}x**
        """)
        
    except:
        await message.reply_text("**NUMBER DAL BHAI!** `.volume 500`")

@app.on_message(filters.command("active", prefixes="."))
async def active_cmd(_, message: Message):
    """Current active chat dikhayega"""
    chat_id = current_active_chat or get_active_chat()
    
    if chat_id:
        try:
            chat = await app.get_chat(chat_id)
            chat_name = chat.title or str(chat_id)
            await message.reply_text(f"""
╔══════════════════════════╗
║   📍 **ACTIVE CHAT**      ║
╠══════════════════════════╣
║ 📛 Name: `{chat_name}`
║ 🆔 ID: `{chat_id}`
║ 🔊 Volume: `{current_volume.get(chat_id, 500)}%`
║ 🎧 Status: **ACTIVE**
╚══════════════════════════╝
            """)
        except:
            await message.reply_text(f"**ACTIVE CHAT ID:** `{chat_id}`")
    else:
        await message.reply_text("**KOI ACTIVE CHAT NAHI!**\nPehle `.join` kar.")

# Stream end handler
@call.on_stream_end()
async def stream_end_handler(_, chat_id: int):
    """Cleanup after stream ends"""
    if chat_id in active_calls:
        if active_calls[chat_id] and os.path.exists(active_calls[chat_id]):
            try:
                os.remove(active_calls[chat_id])
                boosted_file = active_calls[chat_id].replace(".mp3", "_boosted.mp3")
                if os.path.exists(boosted_file):
                    os.remove(boosted_file)
            except:
                pass
        active_calls[chat_id] = None

# ============== STARTUP ==============

async def main():
    print("""
╔═════════════════════════════════════════════╗
║   🔥 OGGY_KILLER ULTIMATE VC USERBOT 🔥     ║
║   💀 CHUMT KA DARINDA - 500% VOLUME 💀       ║
║   🎧 MUTE BYPASS + AUTO CHAT SAVE           ║
╚═════════════════════════════════════════════╝
    """)
    
    await app.start()
    await call.start()
    
    print("[✓] Pyrogram client started")
    print("[✓] PyTgCalls started")
    
    if current_active_chat:
        print(f"[✓] Active chat loaded: {current_active_chat}")
    
    print("\n🔥 USERBOT AKTIVATED! 🔥")
    print("\n📌 Commands: .start ya .help")
    print("="*50)
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 CHUMT KE PYASA, FIR MILENGE! 💀")
        cleanup_downloads()
