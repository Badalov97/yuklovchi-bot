import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def index(): return "Yuklovchi Bot Live!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run).start()

TOKEN = "8218860687:AAEtyN1gI1sgvgzwkPfMFKDEyWnFMLWvn-U"
bot = telebot.TeleBot(TOKEN)

def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Salom! Menga YouTube, TikTok yoki Instagram linkini yuboring. Men ularni yuklab berishga harakat qilaman!")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text
    if "http" in url:
        waiting_msg = bot.reply_to(message, "⏳ Tekshirilmoqda va yuklanmoqda, iltimos kuting...")
        try:
            file_path = download_media(url)
            with open(file_path, 'rb') as f:
                if os.path.getsize(file_path) > 50 * 1024 * 1024:
                    bot.send_document(message.chat.id, f)
                else:
                    bot.send_video(message.chat.id, f)
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, waiting_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Kechirasiz, yuklashda xatolik yuz berdi. Bu video himoyalangan yoki server chekloviga tushgan bo'lishi mumkin.\n\nXato: {str(e)[:100]}...", message.chat.id, waiting_msg.message_id)
    else:
        bot.reply_to(message, "Iltimos, video havolasini yuboring.")

if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    keep_alive()
    bot.polling(none_stop=True)

