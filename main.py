import os
import requests
import threading
import time
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
WEBHOOK_ENDPOINT = os.getenv("WEBHOOK_ENDPOINT", "sarah_webhook")
PORT = int(os.getenv("PORT", 5000))

# Flask setup
flask_app = Flask(__name__)

# Telegram bot setup
app_bot = Application.builder().token(TOKEN).build()

# In-memory user data
user_subscriptions = {}

# Basic AI reply simulation (replace later with real Sarah AI logic)
def sarah_ai_response(question):
    return f"Sarah 🤖: Hmm... interesting! Here's what I think about '{question}':\n\nThis is an educational insight about forex — stay consistent and you'll grow. 📈"

# Telegram command handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to FirePips Forex Academy 🔥\n"
        "I'm Sarah, your forex learning assistant.\n\n"
        "You can ask me anything using:\n"
        "`/ask your question here`\n\n"
        "Example:\n"
        "`/ask what is lot size in forex?`",
        parse_mode="Markdown"
    )

async def subscribe(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    payment_link = f"https://paylink.monnify.com/Triadpips?customerReference={user_id}"
    await update.message.reply_text(
        f"Subscription costs ₦20,000 for 30 days access.\n"
        f"Click below to make payment:\n\n{payment_link}\n\n"
        "After payment, access will be automatically activated. ✅"
    )

async def ask(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    question = " ".join(context.args)
    
    if not question:
        await update.message.reply_text("Please type your question after /ask.")
        return
    
    # ✅ For now, Sarah will reply to everyone (no payment restriction)
    response = sarah_ai_response(question)
    await update.message.reply_text(response)
    
    # Optional: Log question to your channel if provided
    if CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=int(CHANNEL_ID),
                                           text=f"User {user_id} asked:\n{question}")
        except Exception:
            pass

# Background thread for subscription checks (disabled logic for now)
def subscription_checker():
    while True:
        time.sleep(3600)  # Every hour
        # In the future, you can deactivate expired users here
        pass

# Flask webhook route
@flask_app.route(f"/{WEBHOOK_ENDPOINT}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_bot.bot)
    app_bot.update_queue.put(update)
    return "ok"

# Monnify webhook route (kept for future)
@flask_app.route("/monnify_webhook", methods=["POST"])
def monnify_webhook():
    data = request.json
    return "ok"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app_bot.run_polling()
