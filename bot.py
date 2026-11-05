import re
import time
import os
import instaloader
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token will come from Render Environment Variable, not from here
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def get_insta_data(input_text):
    match = re.search(r'instagram\.com/([^/?#]+)', input_text)
    if match:
        username = match.group(1)
    else:
        username = input_text.replace('@', '').strip().split('/')[0]
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    total_likes = 0
    total_comments = 0
    reels_count = 0
    photo_count = 0
    checked = 0
    POST_LIMIT = 10000
    for post in profile.get_posts():
        if checked >= POST_LIMIT:
            break
        total_likes += post.likes
        total_comments += post.comments
        if post.is_video:
            reels_count += 1
        else:
            photo_count += 1
        checked += 1
        if checked % 100 == 0:
            time.sleep(1)
    result = (
        f"✅ Instagram Report Found\n\n"
        f"👤 Username: @{profile.username}\n"
        f"🆔 User ID: {profile.userid}\n"
        f"📛 Name: {profile.full_name}\n"
        f"📝 Bio: {profile.biography}\n"
        f"✔️ Verified: {profile.is_verified}\n\n"
        f"👥 Followers: {profile.followers}\n"
        f"👣 Following: {profile.followees}\n"
        f"🖼️ Total Posts: {profile.mediacount}\n\n"
        f"📊 Full Analysis ({checked} Posts Checked):\n"
        f"🎬 Reels: {reels_count}\n"
        f"📸 Photos: {photo_count}\n"
        f"❤️ Total Likes: {total_likes}\n"
        f"💬 Total Comments: {total_comments}\n"
        f"⭐ Avg Likes: {total_likes // checked if checked else 0}"
    )
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = user.username if user.username else user.first_name
    keyboard = [["🔍 Search Instagram"], ["ℹ️ Help"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    welcome_text = (
        f"Welcome {username} and {chat_id} to our XYZ bot ☺️\n\n"
        f"Please give us a Instagram account name or Link/URL.🌐"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔍 Search Instagram":
        await update.message.reply_text("Please send Instagram username or Link 🌐")
        return
    if text == "ℹ️ Help":
        await update.message.reply_text("Just send @username or Instagram Link, I will send full report.")
        return
    processing_msg = await update.message.reply_text("processing..plz wait.. ⏳\nThis may take 2-5 minutes for big accounts.")
    try:
        result = get_insta_data(text)
        await processing_msg.edit_text(result)
    except Exception as e:
        await processing_msg.edit_text(f"❌ Not Found. Please check username or link and try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
