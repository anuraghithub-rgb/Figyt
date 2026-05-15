# helpers/audio_utils.py
import asyncio
import subprocess
import os

def boost_audio_file(input_path: str, output_path: str, volume_multiplier: float = 5.0):
    """Audio file ko 500% boost dega via FFmpeg"""
    cmd = [
        "ffmpeg", "-i", input_path,
        "-af", f"volume={volume_multiplier}",
        "-c:a", "mp3", "-b:a", "512k",
        output_path, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def get_boosted_audio_stream(file_path: str, volume_boost: int = 500):
    """Volume boost wala stream return karega"""
    from pytgcalls.types import AudioParameters
    from pytgcalls.types.input_stream import AudioStream, AudioPiped
    
    # Create boosted version
    boosted_path = file_path.replace(".mp3", "_boosted.mp3")
    boost_audio_file(file_path, boosted_path, volume_boost / 100)
    
    return AudioStream(
        AudioPiped(boosted_path),
        AudioParameters(
            bitrate=512000,
            volume=200,  # PyTgCalls max 200, FFmpeg already boosted
        )
    )

async def set_volume_500(call, chat_id: int):
    """Volume forcefully 500% equivalent set karega"""
    from pytgcalls.types import VolumeControl
    
    try:
        # Mic band (bypass mute)
        await call.set_is_mute(chat_id, True)
        await asyncio.sleep(0.3)
        
        # Volume max
        await call.change_volume_call(chat_id, VolumeControl(volume=200, muted=False))
        await asyncio.sleep(0.3)
        
        # Mic band rakh (audio baajta rahega)
        await call.set_is_mute(chat_id, True)
        
        return True
    except:
        return False
