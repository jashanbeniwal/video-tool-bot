import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.video_processor import (
    extract_thumbnail, trim_video, merge_videos, split_video,
    optimize_video, add_subtitles, take_screenshots
)

async def handle_video_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming video files"""
    message = update.message
    user_id = message.from_user.id
    
    # Check if file is too large
    if message.video:
        file_size = message.video.file_size
    elif message.document:
        file_size = message.document.file_size
    else:
        file_size = 0
    
    if file_size > 50 * 1024 * 1024:  # 50MB limit for direct processing
        await message.reply_text("📁 File is large. Please use the specific tools from the menu for better processing.")
        return
    
    # Show processing options
    keyboard = [
        [InlineKeyboardButton("🖼️ Extract Thumbnail", callback_data=f"quick_thumb_{user_id}")],
        [InlineKeyboardButton("✂️ Trim", callback_data=f"quick_trim_{user_id}")],
        [InlineKeyboardButton("🔊 Extract Audio", callback_data=f"quick_extract_{user_id}")],
        [InlineKeyboardButton("⚡ Optimize", callback_data=f"quick_optimize_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🎥 What would you like to do with this video?",
        reply_markup=reply_markup
    )

async def thumbnail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle thumbnail extraction request"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Single Frame", callback_data="thumb_single")],
        [InlineKeyboardButton("Multiple Frames", callback_data="thumb_multiple")],
        [InlineKeyboardButton("Custom Time", callback_data="thumb_custom")],
        [InlineKeyboardButton("🔙 Back", callback_data="video_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🖼️ **Thumbnail Extractor**\nChoose extraction type:",
        reply_markup=reply_markup
    )

async def trim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video trim request"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✂️ **Video Trimmer**\nPlease send the video you want to trim, then I'll ask for start and end times.\n\n"
        "Format: HH:MM:SS or seconds\nExample: 00:01:30 or 90"
    )
    context.user_data['awaiting_trim'] = True

async def merge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video merge request"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔀 **Video Merger**\nPlease send multiple videos in the order you want them merged.\n"
        "Send /done when you've sent all videos."
    )
    context.user_data['merging_videos'] = []
    context.user_data['awaiting_merge'] = True

async def split_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video split request"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("By Time Intervals", callback_data="split_time")],
        [InlineKeyboardButton("Into Equal Parts", callback_data="split_parts")],
        [InlineKeyboardButton("By Size", callback_data="split_size")],
        [InlineKeyboardButton("🔙 Back", callback_data="video_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📏 **Video Splitter**\nChoose split method:",
        reply_markup=reply_markup
    )

async def optimize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video optimization request"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("High Quality (Large)", callback_data="optimize_high")],
        [InlineKeyboardButton("Balanced", callback_data="optimize_balanced")],
        [InlineKeyboardButton("Small Size", callback_data="optimize_small")],
        [InlineKeyboardButton("Custom", callback_data="optimize_custom")],
        [InlineKeyboardButton("🔙 Back", callback_data="video_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚡ **Video Optimizer**\nChoose optimization preset:",
        reply_markup=reply_markup
    )

async def subtitle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subtitle request"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Burn Subtitles", callback_data="subtitle_burn")],
        [InlineKeyboardButton("Soft Subtitles", callback_data="subtitle_soft")],
        [InlineKeyboardButton("Multiple Languages", callback_data="subtitle_multi")],
        [InlineKeyboardButton("🔙 Back", callback_data="video_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📝 **Subtitle Manager**\nChoose subtitle type:",
        reply_markup=reply_markup
    )

async def screenshot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot request"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Single Screenshot", callback_data="screenshot_single")],
        [InlineKeyboardButton("Multiple at Interval", callback_data="screenshot_interval")],
        [InlineKeyboardButton("At Specific Times", callback_data="screenshot_times")],
        [InlineKeyboardButton("🔙 Back", callback_data="video_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📸 **Screenshot Tool**\nChoose screenshot type:",
        reply_markup=reply_markup
    )
