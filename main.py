import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# -----------------------------
# Environment Variables
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Set this in Render
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Set this in Render, e.g., https://testing-20rh.onrender.com/

# -----------------------------
# Flask App & Telegram Bot Setup
# -----------------------------
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)

# -----------------------------
# Store conversations per user
# -----------------------------
user_conversations = {}  # key: chat_id, value: list of previous messages

# -----------------------------
# /sarah command handler
# -----------------------------
def start_sarah(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_conversations[chat_id] = []  # start a new conversation
    bot.send_message(chat_id=chat_id, text="Hi! I'm Sarah, your Forex assistant. Ask me anything about trading, risk, lot size, pips, support/resistance, and account growth.")

dispatcher.add_handler(CommandHandler("sarah", start_sarah))

# -----------------------------
# Message handler for follow-up questions
# -----------------------------
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_text = update.message.text

    # Initialize conversation if not started
    if chat_id not in user_conversations:
        bot.send_message(chat_id=chat_id, text="Please start with /sarah to begin a Forex conversation.")
        return

    # Append user message to conversation
    user_conversations[chat_id].append({"role": "user", "content": message_text})

    # Generate response using Forex knowledge
    response_text = generate_forex_response(user_conversations[chat_id])

    # Append bot response to conversation
    user_conversations[chat_id].append({"role": "bot", "content": response_text})

    # Send response
    bot.send_message(chat_id=chat_id, text=response_text)

dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

# -----------------------------
# Forex response generator
# -----------------------------
def generate_forex_response(conversation):
    """
    This function simulates Sarah's Forex knowledge:
    - Pip definition & calculation
    - Lot size calculation based on risk
    - Support/resistance, supply/demand
    - Account growth steps
    - Risk management
    """
    last_user_msg = conversation[-1]["content"].lower()

    # Examples of intelligent handling:
    if "pip" in last_user_msg:
        return (
            "A pip is the smallest price move in a currency pair. "
            "To calculate pip value, multiply 0.0001 by your trade size in base currency. "
            "For JPY pairs, it's 0.01. To calculate profit/loss: (Pip change * lot size * pip value)."
        )
    elif "lot size" in last_user_msg or "risk" in last_user_msg:
        return (
            "To calculate lot size: "
            "1. Determine your account balance and risk per trade in dollars. "
            "2. Divide your risk by the stop-loss in pips multiplied by pip value. "
            "3. This gives your lot size. "
            "Example: $100 risk, stop-loss 50 pips, pip value $10 per standard lot → Lot size = 0.2 lots."
        )
    elif "account growth" in last_user_msg:
        return (
            "Steps to grow a Forex account: "
            "1. Define risk per trade (e.g., 1-2%). "
            "2. Plan entry/exit based on support/resistance and trend. "
            "3. Keep a consistent lot size. "
            "4. Use proper risk-reward (e.g., 1:2). "
            "5. Track performance and adjust strategies gradually."
        )
    else:
        # Default: general forex advice
        return (
            "I can help with any Forex question: calculating pips, lot sizes, risk management, "
            "support/resistance, supply/demand, or account growth. "
            "Please provide details if you want step-by-step guidance."
        )

# -----------------------------
# Flask route for Telegram webhook
# -----------------------------
@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200
    else:
        return "Sarah Forex Bot is running.", 200

# -----------------------------
# Set webhook on startup
# -----------------------------
if __name__ == "__main__":
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
