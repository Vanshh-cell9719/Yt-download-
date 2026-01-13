
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Fake web server for Render (free hosting)
web_app = Flask("")

@web_app.route("/")
def home():
    return "YT Downloader Bot is running"

def run():
    web_app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()

# Telegram Bot Token (from Render Environment)
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 YouTube Video Downloader Bot\n\n"
        "Send any YouTube link and I will give you the video in MP4."
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ Downloading your video...")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_video(video=open("video.mp4", "rb"))

    except:
        await update.message.reply_text("❌ Error downloading. Try another link.")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

app.run_polling()
