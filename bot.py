import os
import asyncio
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ==========================================
# 1. FLASK VEB-SERVER (Render o'chirmasligi uchun)
# ==========================================
server = Flask('')

@server.route('/')
def home():
    return "Bot tirik va ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    """Flask serverni alohida oqimda (thread) ishga tushirish"""
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# ==========================================
# 2. SOZLAMALAR VA KALITLAR (Environment)
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Sen foydalanuvchilar bilan qaysi tilda gaplashsa, o'sha tilda javob beradigan aqlli AI botsan. "
        "Agar senga o'zbekcha yozishsa — doimo o'zbekcha javob ber, agar ruscha yozishsa — doimo ruscha javob ber. "
        "Savollarga juda uzun bo'lmagan, qisqa va aniq javob qaytar."
    )
)

chat_sessions = {}

# ==========================================
# 3. BOT FUNKSIYALARI (Handlers)
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text(
        "Salom! Men Gemini AI botman. Savolingizni yo'llashingiz mumkin!\n"
        "Привет! Я бот Gemini AI. Вы можете задать свой вопрос!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    await update.message.reply_text(
        "Suhbat tarixi tozalandi! Yangi mavzuda gaplashishimiz mumkin.\n"
        "История чата очищена! Мы можем начать новую тему."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        response = chat_sessions[user_id].send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text(
            "Kechirasiz, xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.\n"
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
        )

# ==========================================
# 4. ASINXRON ISHGA TUSHIRISH (Event Loop Muammosini Yechish)
# ==========================================
async def start_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botni asinxron tarzda ishga tushiramiz va polling qilamiz
    await app.initialize()
    await app.updater.start_polling()
    await app.start()
    print("Bot muvaffaqiyatli ishga tushdi...")
    
    # Bot to'xtab qolmasligi uchun cheksiz sikl
    while True:
        await asyncio.sleep(1)

def main():
    # 1. Orqa fonda Flask veb-serverni yoqamiz
    keep_alive()
    
    # 2. Asinxron xotira zanjirini (Event Loop) xatosiz ishga tushiramiz
    asyncio.run(start_bot())

if __name__ == '__main__':
    main()
