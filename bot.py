import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from config.config import BOT_TOKEN, REDIS_URL
from handlers.video_handlers import (
    handle_video_message, thumbnail_callback, trim_callback,
    merge_callback, split_callback, optimize_callback,
    subtitle_callback, screenshot_callback
)
from handlers.audio_handlers import (
    audio_extract_callback, audio_convert_callback,
    remove_audio_callback, video_to_audio_callback
)
from handlers.archive_handlers import (
    archive_callback, extract_callback, bundle_callback
)
from utils.file_utils import cleanup_temp_files

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu"""
    keyboard = [
        [InlineKeyboardButton("🎥 Video Tools", callback_data="video_tools")],
        [InlineKeyboardButton("🔊 Audio Tools", callback_data="audio_tools")],
        [InlineKeyboardButton("📦 Archive Tools", callback_data="archive_tools")],
        [InlineKeyboardButton("⚙️ Metadata Editor", callback_data="metadata_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🤖 **All-in-One Video Tool Bot**

I can help you with:
• 🎥 Video editing & processing
• 🔊 Audio extraction & conversion  
• 📦 Archive creation & extraction
• 🖼️ Thumbnail & screenshot creation
• 📝 Subtitle management
• 🔍 Metadata editing

Send me a video file or choose a tool from the menu below!
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "video_tools":
        keyboard = [
            [InlineKeyboardButton("🖼️ Extract Thumbnails", callback_data="thumbnail")],
            [InlineKeyboardButton("✂️ Trim Video", callback_data="trim")],
            [InlineKeyboardButton("🔀 Merge Videos", callback_data="merge")],
            [InlineKeyboardButton("📏 Split Video", callback_data="split")],
            [InlineKeyboardButton("⚡ Optimize Video", callback_data="optimize")],
            [InlineKeyboardButton("📝 Add Subtitles", callback_data="subtitle")],
            [InlineKeyboardButton("📸 Take Screenshots", callback_data="screenshot")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_back")]
        ]
        text = "🎥 **Video Tools**\nChoose an option:"
        
    elif query.data == "audio_tools":
        keyboard = [
            [InlineKeyboardButton("🔊 Extract Audio", callback_data="extract_audio")],
            [InlineKeyboardButton("🎵 Convert Audio", callback_data="convert_audio")],
            [InlineKeyboardButton("🔇 Remove Audio", callback_data="remove_audio")],
            [InlineKeyboardButton("🎥 Video to Audio", callback_data="video_to_audio")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_back")]
        ]
        text = "🔊 **Audio Tools**\nChoose an option:"
        
    elif query.data == "archive_tools":
        keyboard = [
            [InlineKeyboardButton("📦 Create Archive", callback_data="create_archive")],
            [InlineKeyboardButton("📤 Extract Archive", callback_data="extract_archive")],
            [InlineKeyboardButton("📚 Bundle Files", callback_data="bundle_files")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_back")]
        ]
        text = "📦 **Archive Tools**\nChoose an option:"
        
    elif query.data == "main_back":
        keyboard = [
            [InlineKeyboardButton("🎥 Video Tools", callback_data="video_tools")],
            [InlineKeyboardButton("🔊 Audio Tools", callback_data="audio_tools")],
            [InlineKeyboardButton("📦 Archive Tools", callback_data="archive_tools")],
            [InlineKeyboardButton("⚙️ Metadata Editor", callback_data="metadata_tools")]
        ]
        text = "🤖 **Main Menu**\nChoose a category:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📖 **Bot Usage Guide**

**Basic Usage:**
1. Send a video/audio file directly
2. Use /start to see main menu
3. Choose your desired tool
4. Follow the instructions

**Supported Formats:**
• Video: MP4, AVI, MKV, MOV, WEBM
• Audio: MP3, AAC, WAV, OPUS, FLAC
• Archives: ZIP, 7Z, TAR.GZ

**Features:**
• Large file support (up to 2GB)
• Background processing
• Progress tracking
• Resume support

**Commands:**
/start - Show main menu
/help - This help message
/status - Check processing status
/cancel - Cancel current operation
    """
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current processing status"""
    # Implement status checking logic
    await update.message.reply_text("🔄 Checking processing status...")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    # Implement cancellation logic
    await update.message.reply_text("❌ Operation cancelled.")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Main menu handlers
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^(video_tools|audio_tools|archive_tools|metadata_tools|main_back)$"))
    
    # Video tool handlers
    application.add_handler(CallbackQueryHandler(thumbnail_callback, pattern="^thumbnail$"))
    application.add_handler(CallbackQueryHandler(trim_callback, pattern="^trim$"))
    application.add_handler(CallbackQueryHandler(merge_callback, pattern="^merge$"))
    application.add_handler(CallbackQueryHandler(split_callback, pattern="^split$"))
    application.add_handler(CallbackQueryHandler(optimize_callback, pattern="^optimize$"))
    application.add_handler(CallbackQueryHandler(subtitle_callback, pattern="^subtitle$"))
    application.add_handler(CallbackQueryHandler(screenshot_callback, pattern="^screenshot$"))
    
    # Audio tool handlers
    application.add_handler(CallbackQueryHandler(audio_extract_callback, pattern="^extract_audio$"))
    application.add_handler(CallbackQueryHandler(audio_convert_callback, pattern="^convert_audio$"))
    application.add_handler(CallbackQueryHandler(remove_audio_callback, pattern="^remove_audio$"))
    application.add_handler(CallbackQueryHandler(video_to_audio_callback, pattern="^video_to_audio$"))
    
    # Archive tool handlers
    application.add_handler(CallbackQueryHandler(archive_callback, pattern="^create_archive$"))
    application.add_handler(CallbackQueryHandler(extract_callback, pattern="^extract_archive$"))
    application.add_handler(CallbackQueryHandler(bundle_callback, pattern="^bundle_files$"))
    
    # File message handler
    application.add_handler(MessageHandler(
        filters.VIDEO | filters.Document.VIDEO | filters.Document.AUDIO | filters.AUDIO,
        handle_video_message
    ))
    
    # Start the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
