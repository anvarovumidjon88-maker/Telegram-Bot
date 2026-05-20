import asyncio
import logging
import random
import sqlite3
from datetime import date
from io import BytesIO

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from PIL import Image, ImageDraw, ImageFont

# ================= KONSTANTALAR =================
BOT_TOKEN = "8892596460:AAH_ytQjhzwBQ0zaHLcIPQUJkO6R5DE4tNI"

# ================= BAZA (SQLite3) =================
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        last_try_date TEXT,
        best_score INTEGER DEFAULT 0
    )
''')
conn.commit()

# ================= SAVOLLAR BAZASI (Foundation - 10 tadan) =================
QUESTIONS = {
    "Python": [
        {"q": "Python dasturlash tili kim tomonidan yaratilgan?",
         "options": ["Guido van Rossum", "Dennis Ritchie", "Bjarne Stroustrup", "James Gosling"],
         "a": "Guido van Rossum"},
        {"q": "Pythonda ekranga ma'lumot chiqarish funksiyasi qaysi?",
         "options": ["print()", "echo", "cout", "console.log()"], "a": "print()"},
        {"q": "O'zgaruvchi turini aniqlash uchun qaysi funksiya ishlatiladi?",
         "options": ["type()", "id()", "len()", "int()"], "a": "type()"},
        {"q": "Ro'yxat (list) yaratish uchun qaysi qavsdan foydalaniladi?", "options": ["[ ]", "{ }", "( )", "< >"],
         "a": "[ ]"},
        {"q": "Python fayllari qaysi kengaytma bilan saqlanadi?", "options": [".py", ".pt", ".python", ".pyt"],
         "a": ".py"},
        {"q": "Qaysi ma'lumot turi faqat True yoki False qiymat oladi?", "options": ["bool", "str", "int", "float"],
         "a": "bool"},
        {"q": "Pythonda satrlar (string) qanday belgilar ichida yoziladi?",
         "options": ["Qo'shtirnoq yoki tirnoq", "Faqat qo'shtirnoq", "Burchakli qavs", "Foiz belgisi"],
         "a": "Qo'shtirnoq yoki tirnoq"},
        {"q": "Ro'yxat oxiriga element qo'shish funksiyasi qaysi?",
         "options": ["append()", "add()", "push()", "insert()"], "a": "append()"},
        {"q": "Pythonda bir qatorli izoh qaysi belgi bilan boshlanadi?", "options": ["#", "//", "/*", "<!--"],
         "a": "#"},
        {"q": "Matn uzunligini o'lchaydigan funksiyani toping.", "options": ["len()", "length()", "size()", "count()"],
         "a": "len()"}
    ],
    "C++": [
        {"q": "C++ dasturlash tili kim tomonidan yaratilgan?",
         "options": ["Bjarne Stroustrup", "Dennis Ritchie", "Linus Torvalds", "Guido van Rossum"],
         "a": "Bjarne Stroustrup"},
        {"q": "C++ dasturlarida konsolga chiqarish obyekti qaysi?", "options": ["cout", "cin", "print", "printf"],
         "a": "cout"},
        {"q": "Har bir C++ dasturi qaysi asosiy funksiyadan boshlanadi?",
         "options": ["main()", "start()", "init()", "void()"], "a": "main()"},
        {"q": "Siklni to'xtatish yoki undan chiqish uchun nima ishlatiladi?",
         "options": ["break", "continue", "exit", "stop"], "a": "break"},
        {"q": "C++ da har bir qator oxiriga qaysi belgi qo'yiladi?",
         "options": ["; (Nuqtali vergul)", ": (Ikki nuqta)", ". (Nuqta)", ", (Vergul)"], "a": "; (Nuqtali vergul)"},
        {"q": "Butun sonlarni e'lon qilish uchun qaysi kalit oo'z ishlatiladi?",
         "options": ["int", "float", "double", "char"], "a": "int"},
        {"q": "C++ fayllarining kengaytmasi qanday bo'ladi?", "options": [".cpp", ".c", ".cp", ".exe"], "a": ".cpp"},
        {"q": "Faqat bitta belgini saqlashga mo'ljallangan ma'lumot turi?",
         "options": ["char", "string", "int", "bool"], "a": "char"},
        {"q": "Konsoldan ma'lumot kiritish (o'qish) obyekti qaysi?", "options": ["cin", "cout", "scanf", "input"],
         "a": "cin"},
        {"q": "C++ da bir qatorli izoh qanday yoziladi?",
         "options": ["// izoh", "# izoh", "/* izoh */", "<!-- izoh -->"], "a": "// izoh"}
    ],
    "HTML+CSS": [
        {"q": "HTML qisqartmasining kengaytmasi nima?",
         "options": ["HyperText Markup Language", "HighText Machine Language", "Hyperlink Text Management Language",
                     "Home Tool Markup Language"], "a": "HyperText Markup Language"},
        {"q": "Eng katta sarlavha tegi qaysi?", "options": ["<h1>", "<h6>", "<head>", "<heading>"], "a": "<h1>"},
        {"q": "Yangi qatorga o'tish (line break) tegi qaysi?", "options": ["<br>", "<lb>", "<break>", "<p>"],
         "a": "<br>"},
        {"q": "HTML da havola (link) yaratish uchun qaysi teg ishlatiladi?",
         "options": ["<a>", "<link>", "<href>", "<src>"], "a": "<a>"},
        {"q": "CSS ning to'liq nomi nima?",
         "options": ["Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets",
                     "Colorful Style Sheets"], "a": "Cascading Style Sheets"},
        {"q": "Fon rangini o'zgartirish uchun qaysi CSS xossasi ishlatiladi?",
         "options": ["background-color", "color", "bgcolor", "text-color"], "a": "background-color"},
        {"q": "Matnni qalin (bold) qilish uchun qaysi CSS xossasi kerak?",
         "options": ["font-weight", "font-style", "text-style", "bold"], "a": "font-weight"},
        {"q": "Tegning ID identifikatoriga CSS da qanday murojaat qilinadi?",
         "options": ["# (panjara)", ". (nuqta)", "* (yulduzcha)", "@ belgi"], "a": "# (panjara)"},
        {"q": "Tegning klassiga (class) CSS da qanday murojaat qilinadi?",
         "options": [". (nuqta)", "# (panjara)", "$ belgi", "! belgi"], "a": ". (nuqta)"},
        {"q": "HTML hujjatning asosiy ko'rinadigan qismi qaysi teg ichida yoziladi?",
         "options": ["<body>", "<head>", "<html>", "<title>"], "a": "<body>"}
    ],
    "JS": [
        {"q": "JavaScriptda o'zgaruvchi e'lon qilish kalit so'zini toping.",
         "options": ["let", "variable", "int", "def"], "a": "let"},
        {"q": "Brauzer konsoliga ma'lumot chiqarish buyrug'i qaysi?",
         "options": ["console.log()", "print()", "document.write()", "alert()"], "a": "console.log()"},
        {"q": "JS da bir qatorli izoh qanday yoziladi?",
         "options": ["// izoh", "# izoh", "<!-- izoh -->", "/* izoh */"], "a": "// izoh"},
        {"q": "JS fayllari qaysi kengaytmada saqlanadi?", "options": [".js", ".javascript", ".jsc", ".script"],
         "a": ".js"},
        {"q": "Massivning (array) uzunligini bilish uchun qaysi xususiyat ishlatiladi?",
         "options": ["length", "size", "count", "len"], "a": "length"},
        {"q": "Foydalanuvchiga ogohlantirish oynasini chiqarish funksiyasi?",
         "options": ["alert()", "prompt()", "confirm()", "msg()"], "a": "alert()"},
        {"q": "Ikkita qiymat va turning tengligini tekshirish operatori qaysi?", "options": ["===", "==", "=", "!=="],
         "a": "==="},
        {"q": "O'zgarmas (qiymatini o'zgartirib bo'lmaydigan) o'zgaruvchi qanday e'lon qilinadi?",
         "options": ["const", "let", "var", "immutable"], "a": "const"},
        {"q": "Satrni butun songa o'tkazuvchi funksiyani toping.",
         "options": ["parseInt()", "Number.toInteger()", "stringToInt()", "floor()"], "a": "parseInt()"},
        {"q": "JS da funksiya qanday boshlanadi?",
         "options": ["function myFunc()", "def myFunc()", "func myFunc()", "void myFunc()"], "a": "function myFunc()"}
    ],
    "React": [
        {"q": "React nima?",
         "options": ["JavaScript kutubxonasi", "Dasturlash tili", "Ma'lumotlar bazasi", "CSS freymvorki"],
         "a": "JavaScript kutubxonasi"},
        {"q": "React kim (qaysi kompaniya) tomonidan ishlab chiqilgan?",
         "options": ["Meta (Facebook)", "Google", "Microsoft", "Twitter"], "a": "Meta (Facebook)"},
        {"q": "React-da qayta ishlatiladigan UI bo'laklari nima deyiladi?",
         "options": ["Komponent (Component)", "Funksiya", "Modul", "Teg (Tag)"], "a": "Komponent (Component)"},
        {"q": "React-da ma'lumotlarni komponent ichida saqlash uchun nima ishlatiladi?",
         "options": ["State", "Props", "Variables", "HTML"], "a": "State"},
        {"q": "Tepadan pastga (ota komponentdan farzandga) ma'lumot uzatish nima deyiladi?",
         "options": ["Props", "State", "Context", "Redux"], "a": "Props"},
        {"q": "React-da har bir komponent bitta umumiy teg qaytarishi shartmi?",
         "options": ["Ha", "Yo'q", "Faqat klass komponentlar", "Faqat div bo'lishi shart"], "a": "Ha"},
        {"q": "State o'zgarishini kuzatish va unga reaksiyadosh bo'lish uchun qaysi Hook ishlatiladi?",
         "options": ["useEffect", "useState", "useContext", "useReducer"], "a": "useEffect"},
        {"q": "Komponentda stateni e'lon qilish uchun qaysi Hook kerak?",
         "options": ["useState", "useEffect", "useRef", "useMemo"], "a": "useState"},
        {"q": "React loyihalarini tezkor yig'ish (build) uchun zamonaviy instrument?",
         "options": ["Vite", "Python", "HTML", "C++"], "a": "Vite"},
        {"q": "React komponentlari odatda qaysi kengaytmada yoziladi?",
         "options": [".jsx / .tsx", ".html", ".css", ".py"], "a": ".jsx / .tsx"}
    ],
    "PHP": [
        {"q": "PHP kodlari qayerda (qaysi tomonda) bajariladi?",
         "options": ["Server tomonida (Backend)", "Brauzerda (Frontend)", "Faqat foydalanuvchi kompyuterida",
                     "Ma'lumotlar bazasida"], "a": "Server tomonida (Backend)"},
        {"q": "PHP da barcha o'zgaruvchilar qaysi belgi bilan boshlanadi?", "options": ["$", "@", "#", "&"], "a": "$"},
        {"q": "PHP da ekranga matn chiqarish uchun qaysi operator ko'p ishlatiladi?",
         "options": ["echo", "print_text", "cout", "console.log"], "a": "echo"},
        {"q": "PHP fayllari qaysi kengaytma bilan tugaydi?", "options": [".php", ".html", ".ph", ".script"],
         "a": ".php"},
        {"q": "PHP da satrlarni birlashtirish (string concatenation) uchun qaysi belgi ishlatiladi?",
         "options": [". (nuqta)", "+ (plyus)", "& (ampersand)", ", (vergul)"], "a": ". (nuqta)"},
        {"q": "PHP kodlari qaysi maxsus teglar ichiga yoziladi?",
         "options": ["<?php ... ?>", "<script> ... </script>", "<?php ... ?>", "<!--?php ... ?-->"],
         "a": "<?php ... ?>"},
        {"q": "PHP da qator oxiri qaysi belgi bilan tugaydi?", "options": [";", ":", ".", "->"], "a": ";"},
        {"q": "PHP dagi superglobal massivni toping.", "options": ["$_POST", "$POST", "$_VARIABLE", "$GLOBAL_ALL"],
         "a": "$_POST"},
        {"q": "PHP da funksiya qanday e'lon qilinadi?",
         "options": ["function myFunc()", "def myFunc()", "func myFunc()", "create myFunc()"],
         "a": "function myFunc()"},
        {"q": "PHP dasturlash tilining asosiy vazifasi nima?",
         "options": ["Dinamik veb-sahifalar yaratish", "O'yinlar yaratish", "Mobil ilovalar tuzish",
                     "Tizimli dasturlash"], "a": "Dinamik veb-sahifalar yaratish"}
    ]
}


# ================= FSM HOLATLAR =================
class TestState(StatesGroup):
    taking_test = State()
    waiting_for_name = State()


# ================= SERTIFIKAT YASASH FUNKSIYASI =================
def generate_certificate(name: str, subject: str, percent: int, rank: int) -> BytesIO:
    try:
        img = Image.open("cert_template.png")
    except FileNotFoundError:
        img = Image.new('RGB', (2000, 1414), color=(255, 255, 255))

    W, H = img.size
    draw = ImageDraw.Draw(img)

    # 🌟 MAJBURIY KATTA O'LCHAMLAR (Piksellarda)
    # Agar rasm o'ta katta bo'lsa, bu qiymatlarni yanada kattalashtirish mumkin
    TITLE_SIZE = 120  # "SERTIFIKAT" yozuvi uchun
    NAME_SIZE = 100  # Ism va Familiya uchun (ENG KATTA)
    INFO_SIZE = 55  # Kurs va natijalar uchun
    SUB_SIZE = 45  # Kirish matni va sana uchun

    try:
        # Shriftni yuklashga urinish
        font_title = ImageFont.truetype("font.ttf", TITLE_SIZE)
        font_name = ImageFont.truetype("font.ttf", NAME_SIZE)
        font_info = ImageFont.truetype("font.ttf", INFO_SIZE)
        font_sub = ImageFont.truetype("font.ttf", SUB_SIZE)
    except IOError as e:
        # ⚠️ Agar shrift yuklanmasa, terminalga xatolikni chiqaradi
        print(f"\n[XATOLIK] 'font.ttf' faylini o'qib bo'lmadi! Xato: {e}")
        print("[YORDAM] Shrift yuklanmagani uchun standart mayda font ishlayapti.\n")
        font_title = font_name = font_info = font_sub = ImageFont.load_default()

    # --- MATNLARNI JOYLASHUVINI TO'G'RILASH ---

    # 1. Kirish matni
    intro_text = "Ushbu sertifikat IT akademiyasi kursini muvaffaqiyatli tamomlagani uchun berildi:"
    left, top, right, bottom = draw.textbbox((0, 0), intro_text, font=font_sub)
    draw.text(((W - (right - left)) / 2, int(H * 0.38)), intro_text, fill=(70, 70, 70), font=font_sub)

    # 2. Ism va Familiya (Juda yirik va to'q ko'k rangda)
    name_text = name.title()
    left, top, right, bottom = draw.textbbox((0, 0), name_text, font=font_name)
    draw.text(((W - (right - left)) / 2, int(H * 0.46)), name_text, fill=(20, 30, 50), font=font_name)

    # 3. Fan va Natija ma'lumotlari
    info_text = f"Yo'nalish: {subject} Foundation   |   Natija: {percent}%   |   O'rin: {rank}-o'rin"
    left, top, right, bottom = draw.textbbox((0, 0), info_text, font=font_info)
    draw.text(((W - (right - left)) / 2, int(H * 0.58)), info_text, fill=(30, 30, 30), font=font_info)

    # 4. Sana
    date_text = f"Sana: {date.today().strftime('%d.%m.%Y')}"
    left, top, right, bottom = draw.textbbox((0, 0), date_text, font=font_sub)
    draw.text(((W - (right - left)) / 2, int(H * 0.68)), date_text, fill=(90, 90, 90), font=font_sub)

    bio = BytesIO()
    bio.name = 'certificate.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio


# ================= BOT VA DISPATCHER =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ================= HANDLERLAR =================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # KUNLIK TAQIQ LOGIKASI BU YERDAN TO'LIQ OLIB TASHLANDI 🚀

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐍 Python", callback_data="subject_Python"),
         InlineKeyboardButton(text="⚙️ C++", callback_data="subject_C++")],
        [InlineKeyboardButton(text="🌐 HTML + CSS", callback_data="subject_HTML+CSS"),
         InlineKeyboardButton(text="🟨 JavaScript", callback_data="subject_JS")],
        [InlineKeyboardButton(text="⚛️ React", callback_data="subject_React"),
         InlineKeyboardButton(text="🐘 PHP", callback_data="subject_PHP")]
    ])

    await message.answer("🎯 <b>Smart Test & Sertifikat Botiga xush kelibsiz!</b>\n\n"
                         "Test 10 ta savoldan iborat. Sertifikat olish uchun kamida 50% natija ko'rsatishingiz kerak.\n\n"
                         "Boshlash uchun fanlardan birini tanlang:", reply_markup=kb, parse_mode="HTML")


@dp.callback_query(F.data.startswith("subject_"))
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    subject = callback.data.split("_")[1]
    all_q = QUESTIONS.get(subject, [])

    selected_questions = random.sample(all_q, min(len(all_q), 10))

    await state.update_data(
        subject=subject,
        questions=selected_questions,
        current_q_index=0,
        score=0
    )

    await callback.message.edit_text(f"🏁 <b>{subject}</b> bo'yicha test boshlandi! Omad yor bo'lsin!",
                                     parse_mode="HTML")
    await send_question(callback.message, state)
    await state.set_state(TestState.taking_test)


async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    q_index = data['current_q_index']
    questions = data['questions']

    if q_index >= len(questions):
        await finish_test(message, state)
        return

    question_data = questions[q_index]
    options = list(question_data['options'])
    random.shuffle(options)

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for idx, opt in enumerate(options):
        kb.inline_keyboard.append([InlineKeyboardButton(text=opt, callback_data=f"ans_{idx}")])

    await state.update_data(current_options=options)
    await message.answer(f"❓ <b>Savol {q_index + 1}/10:</b>\n\n{question_data['q']}", reply_markup=kb,
                         parse_mode="HTML")


@dp.callback_query(TestState.taking_test, F.data.startswith("ans_"))
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    opt_index = int(callback.data.split("_")[1])
    selected_answer = data['current_options'][opt_index]

    q_index = data['current_q_index']
    correct_answer = data['questions'][q_index]['a']

    if selected_answer == correct_answer:
        await state.update_data(score=data['score'] + 1)

    await callback.message.delete()
    await state.update_data(current_q_index=q_index + 1)
    await send_question(callback.message, state)


async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    score = data['score']
    subject = data['subject']
    percent = int((score / 10) * 100)

    rank = None
    if 90 <= percent <= 100:
        rank = 1
    elif 80 <= percent <= 89:
        rank = 2
    elif 70 <= percent <= 79:
        rank = 3
    elif 60 <= percent <= 69:
        rank = 4
    elif 50 <= percent <= 59:
        rank = 5

    user_id = message.chat.id
    today = str(date.today())
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE users SET last_try_date=?, best_score=MAX(best_score, ?) WHERE user_id=?",
                   (today, percent, user_id))
    conn.commit()

    await state.update_data(percent=percent, rank=rank)
    text = f"📊 <b>Test yakunlandi!</b>\n\nFan: {subject}\nTo'g'ri javoblar: {score}/10\nNatija: {percent}%\n\n"

    if rank:
        text += f"🎉 Ajoyib! Siz TOP-5 likka kirib, <b>{rank}-o'rinni</b> egalladirgiz.\n\nSertifikatingizga yoziladigan ism-familiyangizni yozib yuboring:"
        await message.answer(text, parse_mode="HTML")
        await state.set_state(TestState.waiting_for_name)
    else:
        text += "😔 Sertifikat olish uchun kamida 50% natija kerak edi. Xafa bo'lish yo'q, bilimlaringizni oshirib qaytadan urinib ko'ring!"
        await message.answer(text, parse_mode="HTML")
        await state.clear()


@dp.message(TestState.waiting_for_name)
async def get_name_and_send_cert(message: types.Message, state: FSMContext):
    full_name = message.text
    data = await state.get_data()

    await message.answer("⏳ Sertifikatingiz tayyorlanmoqda, iltimos kuting...")

    cert_bio = generate_certificate(
        name=full_name,
        subject=data['subject'],
        percent=data['percent'],
        rank=data['rank']
    )

    photo = BufferedInputFile(cert_bio.read(), filename="sertifikat.png")
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=f"🏆 <b>Sertifikat muvaffaqiyatli topshirildi!</b>\n\n👤 O'quvchi: {full_name}\n📚 Yo'nalish: {data['subject']} Foundation\n📈 Ball: {data['percent']}%"
    )

    cursor.execute("UPDATE users SET full_name=? WHERE user_id=?", (full_name, message.from_user.id))
    conn.commit()
    await state.clear()


@dp.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    cursor.execute(
        "SELECT full_name, best_score FROM users WHERE full_name IS NOT NULL ORDER BY best_score DESC LIMIT 10")
    top_users = cursor.fetchall()

    if not top_users:
        await message.answer("Reyting hali shakllanmadi.")
        return

    text = "🏆 <b>Eng yuqori natijalar (Leaderboard):</b>\n\n"
    for i, (name, score) in enumerate(top_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
        text += f"{medal} {i}. {name} — {score}%\n"

    await message.answer(text, parse_mode="HTML")


async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())