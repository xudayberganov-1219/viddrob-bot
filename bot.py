import asyncio
import os
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import yt_dlp

nest_asyncio.apply()

TOKEN = '7619009078:AAF7TKU9j4QikKjIb46BZktox3-MCd9SbME'
CHANNEL_USERNAME = "@IT_kanal_oo1"
FFMPEG_PATH = r"C:\Users\User\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)

    if member.status not in ['member', 'creator', 'administrator']:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ])
        await update.message.reply_text("👋 Salom!\nBotdan foydalanish uchun avval kanalga obuna bo‘ling:", reply_markup=btn)
        return

    await update.message.reply_text("🎬 YouTube yoki Instagram link yuboring va formatni tanlang:")

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)

    if member.status not in ['member', 'creator', 'administrator']:
        await update.callback_query.answer("❌ Hali obuna bo‘lmadingiz!", show_alert=True)
    else:
        await update.callback_query.message.reply_text("✅ Obuna tasdiqlandi! Endi link yuboring.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data['url'] = url

    if "youtube.com" in url or "youtu.be" in url:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}")],
            [InlineKeyboardButton("🎥 MP4", callback_data=f"mp4|{url}")],
        ])
        await update.message.reply_text("📥 Yuklab olish formatini tanlang:", reply_markup=btn)

    elif "instagram.com" in url:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Yuklab olish", callback_data=f"insta|{url}")],
        ])
        await update.message.reply_text("📥 Instagram videoni yuklashni tasdiqlang:", reply_markup=btn)

    else:
        await update.message.reply_text("❌ Noto‘g‘ri link. Faqat YouTube yoki Instagram linklarini yuboring.")

async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    format_type, url = data.split("|", 1)
    await query.edit_message_text("⏬ Yuklab olinmoqda...")

    try:
        # Foyllarni toza saqlash uchun nom
        output = "%(title)s.%(ext)s"

        # Instagram uchun
        if format_type == "insta":
            ydl_opts = {
                'outtmpl': output,
                'quiet': True,
                'ffmpeg_location': FFMPEG_PATH,
            }
        # YouTube MP3
        elif format_type == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'ffmpeg_location': FFMPEG_PATH,
                'outtmpl': output,
                'noplaylist': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        # YouTube MP4
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio',
                'ffmpeg_location': FFMPEG_PATH,
                'outtmpl': output,
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
            }

        # Yuklab olish
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if format_type == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        # Yuborish
        with open(filename, "rb") as f:
            if filename.endswith(".mp3"):
                await query.message.reply_audio(f, caption="✅ MP3 tayyor!")
            else:
                await query.message.reply_video(f, caption="✅ Video tayyor!")

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"❌ Yuklab olishda xatolik:\n{e}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    app.add_handler(CallbackQueryHandler(download_file, pattern=r"^(mp3|mp4|insta)\|"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("✅ Bot ishga tushdi...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
