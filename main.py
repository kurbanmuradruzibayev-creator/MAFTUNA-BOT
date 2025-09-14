import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiosqlite
from pathlib import Path

# Loglarni ko‘rish uchun
logging.basicConfig(level=logging.INFO)

# Tokenni olish
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise RuntimeError("Iltimos, TOKEN environment variable qilib o‘rnatib qo‘ying!")

# Bot va dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Formulalar
FORMULAS = {
    "matematika": {
        "description": "Asosiy formulalar (Matematika)",
        "items": [
            "Kvadrat tenglama: x = (-b ± sqrt(b**2 - 4ac)) / (2a)",
            "To‘g‘ri chiziq: y = kx + b",
            "Perimetr: P = 2*(a+b); Maydon: S = a*b (to‘rtburchak)"
        ]
    },
    "fizika": {
        "description": "Asosiy formulalar (Fizika)",
        "items": [
            "Tezlik: v = s / t",
            "Kuch: F = m * a",
            "Ish: A = F * s"
        ]
    },
    "ingliz": {
        "description": "Tez-tez ishlatiladigan inglizcha iboralar",
        "items": [
            "How are you? — Qalaysan?",
            "I don't understand — Men tushunmayapman",
            "Could you repeat, please? — Iltimos, takrorlaysizmi?"
        ]
    }
}

# Test savollari
QUESTIONS = {
    "matematika": [
        {"q": "2+2", "opts": ["3", "4", "5"], "a": "4"},
        {"q": "5*6", "opts": ["30", "25", "11"], "a": "30"},
        {"q": "sqrt(16)", "opts": ["3", "4", "5"], "a": "4"},
        {"q": "10-7", "opts": ["2", "3", "4"], "a": "3"},
        {"q": "12/4", "opts": ["2", "3", "4"], "a": "3"}
    ],
    "fizika": [
        {"q": "Agar s=100m va t=20s bo‘lsa v?", "opts": ["2 m/s", "5 m/s", "20 m/s"], "a": "5 m/s"},
        {"q": "Kuch formulasi?", "opts": ["F = m*a", "E = m*c^2", "P = V*I"], "a": "F = m*a"},
        {"q": "Yerda tortishish tezlanishi?", "opts": ["9.8 m/s^2", "3.14 m/s^2", "1 m/s^2"], "a": "9.8 m/s^2"},
        {"q": "Ish formulasi?", "opts": ["A = F * s", "V = I * R", "p = mv"], "a": "A = F * s"},
        {"q": "Tezlik formulasi?", "opts": ["v = s/t", "a = dv/dt", "p = F/A"], "a": "v = s/t"}
    ],
    "ingliz": [
        {"q": "'Good morning' ma‘nosi?", "opts": ["Xayr", "Hayrli tong", "Kechirasiz"], "a": "Hayrli tong"},
        {"q": "'Thank you' tarjimasi?", "opts": ["Rahmat", "Iltimos", "Salom"], "a": "Rahmat"},
        {"q": "'See you later' ma‘nosi?", "opts": ["Keyin ko‘rishguncha", "Hozir keling", "Xush kelibsiz"], "a": "Keyin ko‘rishguncha"},
        {"q": "'I'm fine' javobi?", "opts": ["Yaxshi", "Qayerda?", "Nima?"], "a": "Yaxshi"},
        {"q": "'Excuse me' nima uchun?", "opts": ["E'tibor jalb qilish", "Minnatdorchilik", "Xayr"], "a": "E'tibor jalb qilish"}
    ]
}

# Sessiyalar va DB manzili
sessions = {}
DB_PATH = Path('student_bot.db')

# Database yaratish
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            score INTEGER,
            total INTEGER,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.commit()

# Start/help
@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    text = (
        "👋 Assalomu alaykum! Men Student Helper botiman.\n\n"
        "Buyruqlar:\n"
        "📘 /formula <fan> - formulalar (matematika, fizika, ingliz)\n"
        "📝 /test <fan> - 5 savollik test\n"
        "📊 /myprogress - natijalaringiz\n"
    )
    await message.reply(text)

# Formulalar
@dp.message_handler(commands=['formula'])
async def cmd_formula(message: types.Message):
    args = message.get_args().strip().lower()
    if not args:
        await message.reply("Iltimos, fan nomini yozing. Masalan: /formula matematika")
        return
    if args not in FORMULAS:
        await message.reply("❌ Bu fan yo‘q. Mavjud: matematika, fizika, ingliz")
        return

    data = FORMULAS[args]
    text = f"📘 {data['description']}\n\n"
    for i, item in enumerate(data['items'], start=1):
        text += f"{i}. {item}\n"
    await message.reply(text)

# Testni boshlash
@dp.message_handler(commands=['test'])
async def cmd_test(message: types.Message):
    user = message.from_user
    args = message.get_args().strip().lower()
    if not args:
        await message.reply("Qaysi fan bo‘yicha test? Masalan: /test fizika")
        return
    if args not in QUESTIONS:
        await message.reply("❌ Bu fan bo‘yicha test mavjud emas.")
        return

    qs = QUESTIONS[args][:5]
    sessions[user.id] = {'subject': args, 'questions': qs, 'index': 0, 'score': 0}
    await send_question(user.id)

# Savol yuborish
async def send_question(user_id: int):
    session = sessions.get(user_id)
    if not session:
        return

    idx = session['index']
    if idx >= len(session['questions']):
        await finish_quiz(user_id)
        return

    q = session['questions'][idx]
    keyboard = types.InlineKeyboardMarkup()
    for opt in q['opts']:
        keyboard.add(types.InlineKeyboardButton(text=opt, callback_data=f"ans|{opt}"))

    await bot.send_message(user_id, f"❓ Savol {idx+1}: {q['q']}", reply_markup=keyboard)

# Javoblarni tekshirish
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ans|'))
async def process_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    session = sessions.get(user_id)
    if not session:
        await callback_query.answer("Sessiya topilmadi. /test bilan qaytadan boshlang.")
        return

    _, selected = callback_query.data.split('|', 1)
    idx = session['index']
    q = session['questions'][idx]

    if selected == q['a']:
        session['score'] += 1
        await callback_query.answer("✅ To‘g‘ri!")
    else:
        await callback_query.answer(f"❌ Noto‘g‘ri. To‘g‘ri javob: {q['a']}")

    session['index'] += 1
    await asyncio.sleep(0.3)
    await send_question(user_id)

# Test yakuni
async def finish_quiz(user_id: int):
    session = sessions.get(user_id)
    if not session:
        return

    score = session['score']
    total = len(session['questions'])
    subject = session['subject']

    await bot.send_message(user_id, f"🎉 Test tugadi!\nNatija: {score}/{total} ({subject})")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO scores (user_id, subject, score, total) VALUES (?, ?, ?, ?)",
                         (user_id, subject, score, total))
        await db.commit()

    sessions.pop(user_id, None)

# Natijalarni ko‘rish
@dp.message_handler(commands=['myprogress'])
async def cmd_progress(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT subject, score, total, ts FROM scores WHERE user_id = ? ORDER BY ts DESC LIMIT 10",
            (user_id,)
        )
        rows = await cur.fetchall()

    if not rows:
        await message.reply("📭 Sizda hali natija yo‘q. /test bilan boshlang.")
        return

    text = "📊 So‘nggi natijalaringiz:\n"
    for r in rows:
        text += f"🕒 {r[3]} — {r[0]}: {r[1]}/{r[2]}\n"

    await message.reply(text)

# Default
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("❓ Bu buyruqni tushunmadim. /help orqali foydalanishingiz mumkin.")

# Botni ishga tushirish
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(init_db())
    print("🚀 Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
