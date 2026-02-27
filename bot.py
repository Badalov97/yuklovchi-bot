import os
import telebot
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running..."

def run():
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = "8218860687:AAGQ5y-Cngt5fq0POA01UuEBXKPRli6F5kQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men Render-da muvaffaqiyatli ishlayapman!")

if __name__ == "__main__":
    print("Web server ishga tushmoqda...")
    keep_alive()
    print("Bot polling boshlandi...")
    bot.polling(none_stop=True)

