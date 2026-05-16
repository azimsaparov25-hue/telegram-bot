import os
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ==========================================
# 1. FLASK VEB-SERVER (Render uchun)
# ==========================================
server = Flask('')

@server.route('/')
def home():
    return "Bot tirik va ishlamoqda!"

def run():
    # Render avtomatik taqdim etadigan portni tinglaymiz
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    """Veb-serverni alohida oqimda (thread) ishga tushirish"""
    t = threading.Thread(target=run)
    t.start()

# ==========================================
# 2. SOZLAMALAR VA KALITLAR (Environment)
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini AI konfiguratsiyasi (Ikki tilda javob berish sozlamasi bilan)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Sen foydalanuvchilar bilan qaysi tilda gaplashsa, o'sha tilda javob beradigan aqlli AI botsan. "
        "Agar senga o'zbekcha yozishsa — doimo o'zbekcha javob ber, agar ruscha yozishsa — doimo ruscha javob ber. "
        "Savollarga juda uzun bo'lmagan, qisqa va aniq javob qaytar."
    )
)

# Har bir foydalanuvchi uchun alohida suhbat tarixi xotirasi
chat_sessions = {}

# ==========================================
# 3. BOT FUNKSIYALARI (Handlers)
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'i berilganda"""
    user_id = update.effective_user.id
    # Yangi suhbat kontekstini ochish (tarixni tozalash)
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text(
        "Salom! Men Gemini AI botman. Savolingizni yo'llashingiz mumkin!\n"
        "Привет! Я бот Gemini AI. Вы можете задать свой вопрос!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/reset buyrug'i berilganda tarixni o'chirish"""
    user_id = update.effective_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    await update.message.reply_text(
        "Suhbat tarixi tozalandi! Yangi mavzuda gaplashishimiz mumkin.\n"
        "История чата очищена! Мы можем начать новую тему."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE
