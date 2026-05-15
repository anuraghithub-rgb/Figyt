# config.py
import os

# API Credentials (TERI INFO DAL)
API_ID = int(os.environ.get("API_ID", 39447635))
API_HASH = os.environ.get("API_HASH", "fc12fa4f90b177af21e2648441bcde59")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "4915773609881")

# Volume Settings (500% BOOST)
MAX_VOLUME = 500  # 0-500 (500 = 5x boost via FFmpeg)
BITRATE = 512000  # 512 kbps
DOWNLOAD_PATH = "downloads/"

# FFmpeg volume filter (actual boost)
FFMPEG_VOLUME_FILTER = "volume=5.0"  # 5.0 = 500%

# Active chat tracking (auto-save)
ACTIVE_CHAT_FILE = "active_chat.txt"
