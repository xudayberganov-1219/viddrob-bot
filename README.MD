# 🎬 Professional Video Downloader Bot

Professional Telegram bot for downloading videos from Instagram, YouTube, and TikTok with multiple quality options.

## 🚀 Features

### 📱 Supported Platforms
- **Instagram**: Posts, Reels, Stories
- **YouTube**: Videos, Shorts
- **TikTok**: Videos

### 🎯 Quality Options
**Video (MP4):**
- 144p - Small size
- 228p - Medium quality
- 556p - Good quality  
- 1024p - High quality

**Audio (MP3):**
- 128 kbps - Standard
- 192 kbps - Good
- 320 kbps - Best

### ✨ Professional Features
- 🔐 Channel subscription verification
- 📊 Progress tracking during download
- 📈 Download statistics
- 🎨 Professional UI/UX
- ⚡ Fast and reliable downloads
- 🛡️ Error handling and validation
- 📱 Responsive design
- 🔄 Auto-platform detection

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- FFmpeg installed on system
- Telegram Bot Token
- Channel for subscription verification

### Setup Steps

1. **Clone and install dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. **Configure bot settings in `bot.py`:**
```python
TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_USERNAME = '@your_channel'
