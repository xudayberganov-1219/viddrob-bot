import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import yt_dlp
from urllib.parse import urlparse
import re

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
COOKIES_YOUTUBE = 'cookies_youtube.txt'

# Downloads papkasini yaratish
os.makedirs("downloads", exist_ok=True)

def is_valid_url(url):
    """URL validligini tekshirish"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_platform(url):
    """URL qaysi platformaga tegishli ekanligini aniqlash"""
    if 'instagram.com' in url:
        return 'instagram'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'tiktok.com' in url:
        return 'tiktok'
    else:
        return None

async def check_subscription_status(context, user_id):
    """Kanal a'zoligini tekshirish"""
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        logger.error(f"Kanal a'zoligini tekshirishda xato: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    
    # Kanal a'zoligini tekshirish
    is_subscribed = await check_subscription_status(context, user.id)
    
    if not is_subscribed:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Kanalga obuna bo'lish", 
                                url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ])
        
        welcome_text = f"""
👋 Assalomu alaykum, {user.first_name}!

🤖 **Video Downloader Bot**ga xush kelibsiz!

📱 **Qo'llab-quvvatlanadigan platformalar:**
• Instagram (Reels, IGTV, Post)
• YouTube (Video, Shorts)
• TikTok

📥 **Yuklab olish formatlari:**
• MP4 (Video)
• MP3 (Audio)

🎯 **Sifat tanlovi:**
• 144p, 228p, 556p, 1024p

⚠️ **Botdan foydalanish uchun kanalga obuna bo'ling:**
        """
        
        await update.message.reply_text(welcome_text, reply_markup=btn, parse_mode='Markdown')
    else:
        main_menu = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Instagram", callback_data="platform_instagram"),
             InlineKeyboardButton("🎬 YouTube", callback_data="platform_youtube")],
            [InlineKeyboardButton("🎵 TikTok", callback_data="platform_tiktok")],
            [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
        ])
        
        await update.message.reply_text(
            "🎬 **Video Downloader Bot**\n\n"
            "Platformani tanlang yoki to'g'ridan-to'g'ri link yuboring:",
            reply_markup=main_menu,
            parse_mode='Markdown'
        )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obunani tekshirish"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    is_subscribed = await check_subscription_status(context, user.id)
    
    if not is_subscribed:
        await query.answer("❌ Hali ham obuna bo'lmagansiz!", show_alert=True)
    else:
        main_menu = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Instagram", callback_data="platform_instagram"),
             InlineKeyboardButton("🎬 YouTube", callback_data="platform_youtube")],
            [InlineKeyboardButton("🎵 TikTok", callback_data="platform_tiktok")],
            [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
        ])
        
        await query.edit_message_text(
            "✅ **Obuna tasdiqlandi!**\n\n"
            "🎬 Platformani tanlang yoki to'g'ridan-to'g'ri link yuboring:",
            reply_markup=main_menu,
            parse_mode='Markdown'
        )

async def platform_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Platform tanlash"""
    query = update.callback_query
    await query.answer()
    
    platform = query.data.split('_')[1]
    
    platform_info = {
        'instagram': {
            'name': '📱 Instagram',
            'example': 'https://www.instagram.com/p/...',
            'formats': 'Reels, IGTV, Post videolari'
        },
        'youtube': {
            'name': '🎬 YouTube', 
            'example': 'https://www.youtube.com/watch?v=...',
            'formats': 'Video, Shorts, Music'
        },
        'tiktok': {
            'name': '🎵 TikTok',
            'example': 'https://www.tiktok.com/@username/video/...',
            'formats': 'TikTok videolari'
        }
    }
    
    info = platform_info[platform]
    
    back_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ])
    
    await query.edit_message_text(
        f"**{info['name']} Video Yuklovchi**\n\n"
        f"📋 **Qo'llab-quvvatlanadi:** {info['formats']}\n"
        f"🔗 **Misol:** `{info['example']}`\n\n"
        f"📤 Video linkini yuboring:",
        reply_markup=back_btn,
        parse_mode='Markdown'
    )
    
    context.user_data['selected_platform'] = platform

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyuga qaytish"""
    query = update.callback_query
    await query.answer()
    
    main_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Instagram", callback_data="platform_instagram"),
         InlineKeyboardButton("🎬 YouTube", callback_data="platform_youtube")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="platform_tiktok")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ])
    
    await query.edit_message_text(
        "🎬 **Video Downloader Bot**\n\n"
        "Platformani tanlang yoki to'g'ridan-to'g'ri link yuboring:",
        reply_markup=main_menu,
        parse_mode='Markdown'
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam bo'limi"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
🤖 **Video Downloader Bot - Yordam**

📱 **Qo'llab-quvvatlanadigan platformalar:**
• Instagram (Reels, IGTV, Post)
• YouTube (Video, Shorts, Music)
• TikTok

📥 **Yuklab olish formatlari:**
• MP4 (Video) - turli sifatlarda
• MP3 (Audio) - yuqori sifatda

🎯 **Video sifatlari:**
• 144p (Past sifat, kam hajm)
• 228p (O'rta-past sifat)
• 556p (O'rta sifat)
• 1024p (Yuqori sifat)

📋 **Foydalanish:**
1. Platformani tanlang
2. Video linkini yuboring
3. Format va sifatni tanlang
4. Yuklab oling!

⚠️ **Eslatma:** Faqat ochiq (public) videolarni yuklab olish mumkin.
    """
    
    back_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ])
    
    await query.edit_message_text(help_text, reply_markup=back_btn, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """URL ni qayta ishlash"""
    user = update.effective_user
    
    # Kanal a'zoligini tekshirish
    is_subscribed = await check_subscription_status(context, user.id)
    if not is_subscribed:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Kanalga obuna bo'lish", 
                                url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ])
        await update.message.reply_text(
            "❌ Avval kanalga obuna bo'ling!", 
            reply_markup=btn
        )
        return
    
    url = update.message.text.strip()
    
    # URL validligini tekshirish
    if not is_valid_url(url):
        await update.message.reply_text("❌ Noto'g'ri URL! Iltimos, to'g'ri link yuboring.")
        return
    
    # Platformani aniqlash
    platform = get_platform(url)
    if not platform:
        await update.message.reply_text(
            "❌ Qo'llab-quvvatlanmaydigan platforma!\n\n"
            "✅ Qo'llab-quvvatlanadigan platformalar:\n"
            "• Instagram\n• YouTube\n• TikTok"
        )
        return
    
    # URL ni saqlash
    context.user_data['url'] = url
    context.user_data['platform'] = platform
    
    # Format tanlash tugmalari
    format_buttons = [
        [InlineKeyboardButton("🎬 MP4 (Video)", callback_data="format_mp4"),
         InlineKeyboardButton("🎵 MP3 (Audio)", callback_data="format_mp3")]
    ]
    
    platform_names = {
        'instagram': '📱 Instagram',
        'youtube': '🎬 YouTube', 
        'tiktok': '🎵 TikTok'
    }
    
    await update.message.reply_text(
        f"✅ **{platform_names[platform]} linki qabul qilindi!**\n\n"
        f"🔗 **Link:** `{url[:50]}...`\n\n"
        f"📥 **Format tanlang:**",
        reply_markup=InlineKeyboardMarkup(format_buttons),
        parse_mode='Markdown'
    )

async def format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Format tanlash"""
    query = update.callback_query
    await query.answer()
    
    format_type = query.data.split('_')[1]
    context.user_data['format'] = format_type
    
    if format_type == 'mp4':
        # Video sifat tanlash
        quality_buttons = [
            [InlineKeyboardButton("📱 144p", callback_data="quality_144"),
             InlineKeyboardButton("📺 228p", callback_data="quality_228")],
            [InlineKeyboardButton("🖥️ 556p", callback_data="quality_556"),
             InlineKeyboardButton("🎬 1024p", callback_data="quality_1024")],
            [InlineKeyboardButton("🏆 Eng yaxshi sifat", callback_data="quality_best")]
        ]
        
        await query.edit_message_text(
            "🎬 **Video sifatini tanlang:**\n\n"
            "📱 **144p** - Past sifat, kam hajm\n"
            "📺 **228p** - O'rta-past sifat\n"
            "🖥️ **556p** - O'rta sifat\n"
            "🎬 **1024p** - Yuqori sifat\n"
            "🏆 **Eng yaxshi** - Mavjud eng yuqori sifat",
            reply_markup=InlineKeyboardMarkup(quality_buttons),
            parse_mode='Markdown'
        )
    else:
        # MP3 uchun to'g'ridan-to'g'ri yuklab olish
        context.user_data['quality'] = 'audio'
        await start_download(query, context)

async def quality_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sifat tanlash"""
    query = update.callback_query
    await query.answer()
    
    quality = query.data.split('_')[1]
    context.user_data['quality'] = quality
    
    await start_download(query, context)

async def start_download(query, context):
    """Yuklab olishni boshlash"""
    url = context.user_data.get('url')
    platform = context.user_data.get('platform')
    format_type = context.user_data.get('format')
    quality = context.user_data.get('quality')
    
    if not all([url, platform, format_type, quality]):
        await query.edit_message_text("❌ Ma'lumotlar to'liq emas. Qaytadan urinib ko'ring.")
        return
    
    # Yuklab olish jarayonini boshlash
    progress_msg = await query.edit_message_text("⏬ **Yuklab olish boshlandi...**\n\n🔄 Tayyorlanmoqda...")
    
    try:
        # yt-dlp sozlamalari
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': FFMPEG_PATH,
        }
        
        # Platform bo'yicha cookie fayl
        if platform == 'instagram':
            ydl_opts['cookiefile'] = COOKIES_INSTAGRAM
        elif platform == 'youtube':
            ydl_opts['cookiefile'] = COOKIES_YOUTUBE
        
        # Format va sifat sozlamalari
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # Video format
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif quality == '144':
                ydl_opts['format'] = 'worst[height<=144]/worst'
            elif quality == '228':
                ydl_opts['format'] = 'best[height<=240]/best'
            elif quality == '556':
                ydl_opts['format'] = 'best[height<=480]/best'
            elif quality == '1024':
                ydl_opts['format'] = 'best[height<=720]/best'
            
            ydl_opts['merge_output_format'] = 'mp4'
        
        # Progress callback
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = d.get('_percent_str', 'N/A')
                    speed = d.get('_speed_str', 'N/A')
                    asyncio.create_task(progress_msg.edit_text(
                        f"⏬ **Yuklab olish jarayoni:**\n\n"
                        f"📊 **Jarayon:** {percent}\n"
                        f"🚀 **Tezlik:** {speed}\n"
                        f"⏰ **Kutib turing...**",
                        parse_mode='Markdown'
                    ))
                except:
                    pass
        
        ydl_opts['progress_hooks'] = [progress_hook]
        
        # Yuklab olish
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await progress_msg.edit_text("🔍 **Video ma'lumotlari olinmoqda...**")
            
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            duration = info.get('duration', 0)
            
            # Fayl hajmini tekshirish (50MB limit)
            if info.get('filesize', 0) > 50 * 1024 * 1024:
                await progress_msg.edit_text(
                    "❌ **Fayl hajmi juda katta!**\n\n"
                    "📏 **Maksimal hajm:** 50MB\n"
                    "💡 **Tavsiya:** Pastroq sifatni tanlang"
                )
                return
            
            await progress_msg.edit_text("⏬ **Yuklab olish boshlandi...**")
            
            # Faylni yuklab olish
            ydl.download([url])
            
            # Yuklab olingan faylni topish
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            if not os.path.exists(filename):
                raise Exception("Fayl topilmadi")
            
            await progress_msg.edit_text("📤 **Fayl yuborilmoqda...**")
            
            # Faylni yuborish
            with open(filename, 'rb') as file:
                if format_type == 'mp3':
                    await query.message.reply_audio(
                        audio=file,
                        title=title,
                        caption=f"🎵 **{title}**\n\n✅ Muvaffaqiyatli yuklab olindi!",
                        parse_mode='Markdown'
                    )
                else:
                    await query.message.reply_video(
                        video=file,
                        caption=f"🎬 **{title}**\n\n"
                                f"📊 **Sifat:** {quality}p\n"
                                f"⏱️ **Davomiyligi:** {duration//60}:{duration%60:02d}\n\n"
                                f"✅ Muvaffaqiyatli yuklab olindi!",
                        supports_streaming=True,
                        parse_mode='Markdown'
                    )
            
            # Faylni o'chirish
            os.remove(filename)
            
            # Muvaffaqiyat xabari
            success_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Yana yuklab olish", callback_data="back_to_menu")]
            ])
            
            await progress_msg.edit_text(
                "✅ **Muvaffaqiyatli yakunlandi!**\n\n"
                "🎉 Video yuborildi!\n"
                "🔄 Yana video yuklab olish uchun tugmani bosing.",
                reply_markup=success_btn,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Yuklab olishda xato: {e}")
        
        error_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Qayta urinish", callback_data="back_to_menu")]
        ])
        
        await progress_msg.edit_text(
            f"❌ **Xatolik yuz berdi!**\n\n"
            f"🔍 **Sabab:** {str(e)[:100]}...\n\n"
            f"💡 **Tavsiyalar:**\n"
            f"• Video ochiq (public) ekanligini tekshiring\n"
            f"• Linkni qayta tekshiring\n"
            f"• Boshqa sifatni tanlang",
            reply_markup=error_btn,
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xatoliklarni qayta ishlash"""
    logger.error(f"Xatolik yuz berdi: {context.error}")

def main():
    """Asosiy funksiya"""
    # Botni yaratish
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(platform_handler, pattern="platform_"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    application.add_handler(CallbackQueryHandler(help_handler, pattern="help"))
    application.add_handler(CallbackQueryHandler(format_handler, pattern="format_"))
    application.add_handler(CallbackQueryHandler(quality_handler, pattern="quality_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Bot ishga tushdi...")
    
    # Botni ishga tushirish
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
