import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import yt_dlp

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7619009078:AAF7TKU9j4QikKjIb46BZktox3-MCd9SbME'  # O'zingizni haqiqiy tokeningizni kiriting
CHANNEL_USERNAME = "@IT_kanal_oo1"

FFMPEG_PATH = "/usr/bin/ffmpeg"  # Agar Railway yoki serverda ffmpeg o'rnatilgan bo'lsa
COOKIES_INSTAGRAM = "cookies_instagram.txt"
COOKIES_YOUTUBE = "cookies_youtube.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
    except Exception as e:
        logger.error(f"Kanal a'zoligini tekshirishda xato: {e}")
        member = None

    if not member or member.status not in ['member', 'creator', 'administrator']:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ])
        await update.message.reply_text("👋 Salom!\nBotdan foydalanish uchun kanalga obuna bo'ling:", reply_markup=btn)
        return

    await update.message.reply_text("🎬 YouTube yoki Instagram link yuboring:")

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
    except Exception as e:
        logger.error(f"Obunani tekshirishda xato: {e}")
        member = None

    if not member or member.status not in ['member', 'creator', 'administrator']:
        await update.callback_query.answer("❌ Obuna bo'lmagansiz!", show_alert=True)
    else:
        await update.callback_query.message.reply_text("✅ Obuna tasdiqlandi! Endi link yuboring.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data['url'] = url

    if "youtube.com" in url or "youtu.be" in url:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 MP3", callback_data="mp3")],
            [InlineKeyboardButton("🎥 MP4", callback_data="mp4")],
        ])
        await update.message.reply_text("📥 Yuklab olish formatini tanlang:", reply_markup=btn)

    elif "instagram.com" in url:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Yuklab olish", callback_data="insta")],
        ])
        await update.message.reply_text("📥 Instagram videoni yuklashni tasdiqlang:", reply_markup=btn)

    else:
        await update.message.reply_text("❌ Faqat YouTube yoki Instagram link yuboring.")

async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    format_type = query.data
    url = context.user_data.get('url')

    if not url:
        await query.message.reply_text("❗ Avval link yuboring.")
        return

    await query.edit_message_text("⏬ Yuklab olinmoqda...")

    try:
        output = "%(title)s.%(ext)s"
        ydl_opts = {
            'outtmpl': output,
            'quiet': True,
            'ffmpeg_location': FFMPEG_PATH,
            'noplaylist': True,
        }

        if "instagram.com" in url:
            ydl_opts['cookiefile'] = COOKIES_INSTAGRAM
        elif "youtube.com" in url or "youtu.be" in url:
            ydl_opts['cookiefile'] = COOKIES_YOUTUBE

        if format_type == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif format_type in ["mp4", "insta"]:
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        with open(filename, "rb") as f:
            if filename.endswith(".mp3"):
                await query.message.reply_audio(f, caption="✅ MP3 tayyor!")
            else:
                await query.message.reply_video(f, caption="✅ Video tayyor!")

        os.remove(filename)

    except Exception as e:
        logger.error(f"Yuklab olishda xato: {e}")
        await query.message.reply_text(f"❌ Yuklab olishda xatolik:\n{e}")

def main():
    # Botni ishga tushirish
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(download_file, pattern=r"^(mp3|mp4|insta)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Pollingni boshlash
    logger.info("Bot ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
