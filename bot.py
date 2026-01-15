import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ADMIN_UID = int(os.environ.get("ADMIN_UID"))

sessions = {}

SYSTEM_PROMPT = """
You are a hacker-style AI assistant.
Speak Bangla and English.
Teach ethical hacking, cybersecurity, Linux, Termux.
No illegal hacking, phishing, scams.
Tone: confident, professional.
"""

def ask_ai(history):
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history[-6:]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=60
    )

    return r.json()["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 HackerAI Bot Active\nবাংলা বা English এ প্রশ্ন করুন"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 Session cleared.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    history = sessions.get(uid, [])
    history.append({"role": "user", "content": text})

    reply = ask_ai(history)
    history.append({"role": "assistant", "content": reply})

    sessions[uid] = history
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
