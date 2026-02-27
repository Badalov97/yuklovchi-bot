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

def download_media(url, mode):
    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'audio' else 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Salom! Link yuboring, men uni yuklab beraman (Video, Audio yoki Rasm).")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text
    if "http" in url:
        msg = bot.reply_to(message, "Yuklanmoqda, kuting...")
        try:
            
            file_path = download_media(url, 'video')
            with open(file_path, 'rb') as f:                bot.send_video(message.chat.id, f)
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"Xatolik: {str(e)}", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "Iltimos, haqiqiy havola yuboring.")

if __name__ == "__main__":
    if not os.path.exists('downloads'): os.makedirs('downloads')
    keep_alive()
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)

