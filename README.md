# 🎬 Professional Video Downloader Bot

Professional Telegram bot for downloading videos from Instagram, YouTube, and TikTok.

## 🚀 Railway Deployment

### Quick Setup:
1. Fork this repository
2. Connect to Railway
3. Set environment variables:
   - `TOKEN`: Your Telegram bot token
   - `CHANNEL_USERNAME`: Your channel username (e.g., @your_channel)
4. Deploy!

### Features:
- ✅ Instagram, YouTube, TikTok support
- ✅ Multiple quality options (144p-1080p)
- ✅ MP3 and MP4 formats
- ✅ Channel subscription verification
- ✅ Professional UI/UX
- ✅ Error handling and recovery
- ✅ No Docker required

### Environment Variables:
\`\`\`
TOKEN=your_telegram_bot_token
CHANNEL_USERNAME=@your_channel
\`\`\`

### Supported Platforms:
- **Instagram**: Posts, Reels, Stories
- **YouTube**: Videos, Shorts
- **TikTok**: Videos

### Quality Options:
- **Video**: 144p, 360p, 720p, 1080p
- **Audio**: 128kbps, 192kbps, 320kbps

## 🛠️ Local Development

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Set environment variables:
\`\`\`bash
export TOKEN="your_bot_token"
export CHANNEL_USERNAME="@your_channel"
\`\`\`

3. Run the bot:
\`\`\`bash
python bot.py
\`\`\`

## 📋 Troubleshooting

### Common Issues:
- **YouTube errors**: Bot automatically handles authentication issues
- **File size limits**: Maximum 50MB per file
- **Duration limits**: Maximum 15 minutes per video
- **Private content**: Only public videos are supported

### Error Recovery:
- Automatic retry mechanisms
- Graceful error handling
- User-friendly error messages
- Detailed logging for debugging

## 🔧 Technical Details

- **Python**: 3.11+
- **Framework**: python-telegram-bot 20.3
- **Downloader**: yt-dlp (latest)
- **Deployment**: Railway (no Docker)
- **Architecture**: Async/await based

## 📞 Support

For issues:
1. Check Railway logs
2. Verify environment variables
3. Test with different video links
4. Contact developer if needed

---

**Made with ❤️ for seamless video downloading**
