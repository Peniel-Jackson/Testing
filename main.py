import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging

# ---------- Variables ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Make sure to set this in Render
PORT = int(os.environ.get("PORT", "5000"))

# ---------- Flask App ----------
app = Flask(__name__)

# ---------- Telegram Bot ----------
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# ---------- Logging ----------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ---------- Bot Commands ----------
def start(update: Update, context):
    update.message.reply_text("Hello! I'm Sarah. Ask me anything about Forex or your subscriptions.")

def help_command(update: Update, context):
    update.message.reply_text("Available commands:\n/start - Start bot\n/help - Show this message\n/subscribe - Subscribe to services")

def subscribe(update: Update, context):
    update.message.reply_text("To subscribe, send your payment and details. Once confirmed, you'll have access for 30 days.")

def handle_text(update: Update, context):
    user_text = update.message.text
    # Placeholder: replace with AI / Web search response logic
    response = f"Searching for: {user_text}\n[This would be Sarah's AI answer]"
    update.message.reply_text(response)

# ---------- Handlers ----------
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("subscribe", subscribe))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

# ---------- Flask route for Telegram webhook ----------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# ---------- Run Flask ----------
if __name__ == "__main__":
    # Set webhook on deployment
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., "https://yourapp.onrender.com/{BOT_TOKEN}"
    if WEBHOOK_URL:
        bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=PORT)
