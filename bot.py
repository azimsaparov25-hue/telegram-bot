import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""Sen o'zbek tilida yordam beradigan aqlli yordamchisan.
Foydalanuvchilarga har qanday savolga qisqa, aniq va foydali javob ber.
Gepatit B kasalligi bo'lgan odamlarga ham sog'liq bo'yicha maslahat bera olasan.
Doim o'zbek tilida javob ber. Agar rus tilida so'rashsa, o'zbek tilida javob ber."""
)

# Har foydalanuvchi uchun suhbat tarixi
chat_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋 Men sun'iy intellekt yordamchisiman.\n"
        "Har qanday savolingizga javob beraman!\n\n"
        "Shunchaki yozing... 💬"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Typing ko'rsatish
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        # Har foydalanuvchi uchun alohida chat sessiyasi
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])

        chat = chat_sessions[user_id]
        response = chat.send_message(user_text)
        reply = response.text

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(
            "Kechirasiz, xatolik yuz berdi. Qayta urinib ko'ring! 🙏"
        )
        print(f"Xato: {e}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    await update.message.reply_text("Suhbat tozalandi! Yangi suhbat boshlashingiz mumkin. 🔄")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
