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

# Konfiguratsiya
TOKEN = '7619009078:AAF7TKU9j4QikKjIb46BZktox3-MCd9SbME'
CHANNEL_USERNAME = '@IT_kanal_oo1'
FFMPEG_PATH = '/usr/bin/ffmpeg'
COOKIES_INSTAGRAM = 'cookies_instagram.txt'

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
    else:
        await update.message.reply_text("🎬 Instagram video linkini yuboring:")

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
        await update.callback_query.edit_message_text("✅ Obuna tasdiqlandi! Endi Instagram video linkini yuboring.")

async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not "instagram.com" in url:
        await update.message.reply_text("❌ Faqat Instagram link yuboring!")
        return
    
    context.user_data['url'] = url
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Yuklab olish", callback_data="download_insta")]
    ])
    await update.message.reply_text("📥 Yuklashni boshlash uchun tugmani bosing:", reply_markup=btn)

async def download_instagram_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get('url')
    
    if not url:
        await query.edit_message_text("❗ Avval Instagram link yuboring.")
        return
    
    await query.edit_message_text("⏬ Video yuklanmoqda...")
    
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'ffmpeg_location': FFMPEG_PATH,
            'cookiefile': COOKIES_INSTAGRAM,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, "rb") as video_file:
            await query.message.reply_video(
                video=video_file,
                caption="✅ Video muvaffaqiyatli yuklandi!",
                supports_streaming=True
            )

        os.remove(filename)
        
    except Exception as e:
        logger.error(f"Yuklab olishda xato: {e}")
        await query.edit_message_text(f"❌ Xatolik yuz berdi: {str(e)}")

def main():
    # Botni ishga tushirish
    application = ApplicationBuilder() \
        .token(TOKEN) \
        .concurrent_updates(False) \
        .build()

    # Xatolik handleri
    application.add_error_handler(lambda u, c: logger.error("Xatolik:", exc_info=c.error))

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(download_instagram_video, pattern="download_insta"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))

    # Botni ishga tushirish
    logger.info("Bot ishga tushdi...")
    
    # downloads papkasini yaratish
    os.makedirs("downloads", exist_ok=True)
    
    # Pollingni boshlash
    application.run_polling(
        drop_pending_updates=True,
        close_loop=False,
        stop_signals=None,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
