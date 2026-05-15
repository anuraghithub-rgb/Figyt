# helpers/downloader.py
import os
import yt_dlp
from config import DOWNLOAD_PATH

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_PATH}%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'quiet': True,
    'no_warnings': True,
}

def download_youtube_song(query: str):
    """YouTube se gaana download karega"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)['entries'][0]
            url = f"https://youtube.com/watch?v={info['id']}"
            title = info['title']
            
            ydl.download([url])
            
            files = os.listdir(DOWNLOAD_PATH)
            for f in files:
                if f.endswith(".mp3"):
                    return os.path.join(DOWNLOAD_PATH, f), title
        
        return None, None
    except Exception as e:
        return None, str(e)

def cleanup_downloads():
    """Downloads folder saaf karega"""
    if os.path.exists(DOWNLOAD_PATH):
        for f in os.listdir(DOWNLOAD_PATH):
            try:
                os.remove(os.path.join(DOWNLOAD_PATH, f))
            except:
                pass
