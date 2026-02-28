import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def index(): return "Instagram Downloader Live!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run).start()

TOKEN = "8218860687:AAEtyN1gI1sgvgzwkPfMFKDEyWnFMLWvn-U"
bot = telebot.TeleBot(TOKEN)

def download_instagram(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'add_header': [
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language:en-US,en;q=0.9',
        ],
        'extractor_args': {'instagram': {'get_test': ['']}}, # Instagram uchun maxsus argument
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Salom! Menga Instagram Reels yoki YouTube linkini yuboring, men uni yuklab beraman! 🚀")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text
    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        msg = bot.reply_to(message, "🚀 Instagram Reels yuklanmoqda, iltimos kuting...")
        try:
            file_path = download_instagram(url)
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Yuklab bo'lmadi. Video shaxsiy (private) bo'lishi mumkin.\nXato: {str(e)[:100]}", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "Faqat Instagram, YouTube yoki TikTok linklarini yuboring!")

if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    keep_alive()
    bot.polling(none_stop=True)

