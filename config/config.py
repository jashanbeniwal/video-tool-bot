import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# File Configuration
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
TEMP_DIR = "temp"
OUTPUT_DIR = "output"

# Supported formats
VIDEO_FORMATS = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv', '.wmv']
AUDIO_FORMATS = ['.mp3', '.aac', '.wav', '.opus', '.flac', '.m4a']
ARCHIVE_FORMATS = ['.zip', '.7z', '.tar.gz', '.rar']

# Create directories if they don't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
