import asyncio, os, yt_dlp, uuid
from telebot.async_telebot import AsyncTeleBot
from telebot import types

TOKEN = "8218860687:AAGQ5y-Cngt5fq0POA01UuEBXKPRli6F5kQ"
bot = AsyncTeleBot(TOKEN)

link_storage = {}

async def download_logic(chat_id, url, mode):
    ext = 'mp3' if mode == 'mp3' else 'mp4'
    path = f"file_{chat_id}_{uuid.uuid4().hex[:6]}.{ext}"
    
    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'mp3' else 'best',
        'outtmpl': path,
        'quiet': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    if mode == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            fname = ydl.prepare_filename(info)
            if mode == 'mp3': fname = fname.rsplit('.', 1)[0] + ".mp3"

        async with bot.send_chat_action(chat_id, 'upload_document'):
            with open(fname, 'rb') as f:
                if mode == 'mp3':
                    await bot.send_audio(chat_id, f, caption=f"🎵 {info.get('title', 'Musiqa')}")
                else:
                    await bot.send_video(chat_id, f, caption="✅ @Yuklovchi_bot")
        
        if os.path.exists(fname): os.remove(fname)
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Xatolik: Fayl juda katta yoki linkda muammo bor.")
    finally:
        if 'fname' in locals() and os.path.exists(fname): os.remove(fname)

@bot.message_handler(func=lambda m: "http" in m.text)
async def handle_link(message):
    uid = str(uuid.uuid4())[:8]
    link_storage[uid] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎬 Video", callback_data=f"v_{uid}"),
               types.InlineKeyboardButton("🎵 Musiqa", callback_data=f"m_{uid}"))
    await bot.send_message(message.chat.id, "Formatni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
async def handle_search(message):
    sent = await bot.send_message(message.chat.id, "🔍 Qidirilmoqda...")
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            res = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch3:{message.text}", download=False))
        
        markup = types.InlineKeyboardMarkup()
        for e in res['entries']:
            uid = str(uuid.uuid4())[:8]
            link_storage[uid] = f"https://youtu.be/{e['id']}"
            markup.add(types.InlineKeyboardButton(f"🎵 {e['title'][:35]}", callback_data=f"m_{uid}"))
        
        await bot.edit_message_text("Natijalar:", message.chat.id, sent.message_id, reply_markup=markup)
    except:
        await bot.edit_message_text("❌ Hech narsa topilmadi.", message.chat.id, sent.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith(('v_', 'm_')))
async def callback_res(call):
    data = call.data.split('_')
    mode = 'mp3' if data[0] == 'm' else 'mp4'
    uid = data[1]
    
    url = link_storage.get(uid)
    if not url:
        await bot.answer_callback_query(call.id, "❌ Link eskirgan, qayta yuboring.")
        return

    await bot.edit_message_text("⏳ Yuklash va ishlov berish boshlandi...", call.message.chat.id, call.message.message_id)
    asyncio.create_task(download_logic(call.message.chat.id, url, mode))

if __name__ == "__main__":
    print("🚀 Bot ishga tushdi!")
    asyncio.run(bot.polling(none_stop=True))

