import os
import telebot
from dotenv import load_dotenv

# .env fayldan tokenni olish
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# Boshlash komandasi
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 Salom! Men yuz parvarishi bo‘yicha maslahat beradigan botman.\n"
        "Avvalo teri turini aniqlab olaylik.\n"
        "Quyidagilardan birini tanlang:\n\n"
        "1️⃣ Yog‘li\n"
        "2️⃣ Quruq\n"
        "3️⃣ Aralash\n"
        "4️⃣ Sezgir\n"
        "5️⃣ Normal\n\n"
        "Masalan: '1' deb yuboring."
    )

# Javoblarni qabul qilish
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()

    if text == "1":
        bot.reply_to(message, "✨ Yog‘li teri uchun:\n- Gel asosidagi tozalagich ishlating\n- Engil krem yoki suyuq namlantiruvchi\n- SPF har kuni\n- Yog‘ni kamaytiruvchi maskalar haftasiga 2 marta")
    elif text == "2":
        bot.reply_to(message, "✨ Quruq teri uchun:\n- Yumshoq, sutli tozalagich\n- Qalin krem namlantiruvchi\n- Haftasiga 2-3 marta niqob (asal, yogurt)\n- SPF ni unutmang")
    elif text == "3":
        bot.reply_to(message, "✨ Aralash teri uchun:\n- Yengil gel tozalagich\n- T-zona uchun engil krem, boshqa joylar uchun namroq krem\n- Balanslashtiruvchi niqob")
    elif text == "4":
        bot.reply_to(message, "✨ Sezgir teri uchun:\n- Hidsiz va allergiyasiz mahsulotlar\n- Minimal tarkibli krem\n- Sovunsiz tozalagich\n- SPF juda muhim")
    elif text == "5":
        bot.reply_to(message, "✨ Normal teri uchun:\n- Engil tozalagich\n- Oddiy krem\n- Haftada 1-2 marta niqob\n- SPF har kuni")
    else:
        bot.reply_to(message, "❌ Noto‘g‘ri tanlov. Iltimos, 1 dan 5 gacha raqam yuboring.")

# Botni doimiy ishlatish
bot.polling()
