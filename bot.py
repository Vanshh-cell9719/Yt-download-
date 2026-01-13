import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# -----------------------------
# Fake web server for Render
# -----------------------------
web_app = Flask("")

@web_app.route("/")
def home():
    return "YT Downloader Bot is running"

def run():
    web_app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()

# -----------------------------
# Telegram Bot
# -----------------------------
TOKEN = os.getenv("TOKEN")

# Store user links
user_links = {}

# Referral system
referrals = {}

def has_premium(uid):
    return referrals.get(uid, 0) >= 3

# -----------------------------
# Commands
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # Referral tracking
    if args:
        try:
            ref_id = int(args[0])
            if ref_id != user.id:
                referrals[ref_id] = referrals.get(ref_id, 0) + 1
        except:
            pass

    await update.message.reply_text(
        "🎬 YouTube Video Downloader\n\n"
        "Send a YouTube link to download.\n\n"
        "🎁 Invite 3 friends to unlock 1080p HD!\n"
        f"Your referral link:\nhttps://t.me/{context.bot.username}?start={user.id}"
    )

async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_links[update.effective_user.id] = url

    keyboard = [
        [InlineKeyboardButton("360p", callback_data="360")],
        [InlineKeyboardButton("480p", callback_data="480")],
        [InlineKeyboardButton("720p", callback_data="720")],
        [InlineKeyboardButton("1080p (Premium)", callback_data="1080")]
    ]

    await update.message.reply_text(
        "Choose video quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    quality = query.data
    url = user_links.get(uid)

    if not url:
        await query.edit_message_text("❌ Please send the YouTube link again.")
        return

    # Premium check for 1080p
    if quality == "1080" and not has_premium(uid):
        await query.edit_message_text(
            "❌ 1080p is for premium users.\n\n"
            "Invite 3 friends to unlock HD!\n"
            f"Your link:\nhttps://t.me/{context.bot.username}?start={uid}"
        )
        return

    await query.edit_message_text(f"⏳ Downloading {quality}p video...")

    ydl_opts = {
        "format": f"best[height<={quality}]",
        "outtmpl": f"{uid}.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_video(video=open(f"{uid}.mp4", "rb"))

    except:
        await query.message.reply_text("❌ Error downloading video.")

# -----------------------------
# Run Bot
# -----------------------------
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))
app.add_handler(CallbackQueryHandler(download))

app.run_polling()
