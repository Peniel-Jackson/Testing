import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# ===== VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram bot token
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your webhook URL
CONVERSATION_MEMORY = {}  # Memory to track ongoing conversations with users

# ===== FLASK APP =====
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# ===== /SARAH COMMAND =====
def start_sarah(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    CONVERSATION_MEMORY[user_id] = []  # Initialize session memory
    update.message.reply_text(
        "Hello! I am Sarah, your Forex assistant. Ask me anything about Forex now, "
        "and I will respond step by step."
    )

# ===== HANDLE MESSAGES =====
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    # Ignore messages if user hasn't started /sarah session
    if user_id not in CONVERSATION_MEMORY:
        return

    # Save user message
    CONVERSATION_MEMORY[user_id].append({"role": "user", "content": text})

    # Generate a response based on conversation memory
    response = generate_forex_response(CONVERSATION_MEMORY[user_id])

    # Save bot response
    CONVERSATION_MEMORY[user_id].append({"role": "assistant", "content": response})

    # Send response
    update.message.reply_text(response)

# ===== FOREX RESPONSE FUNCTION =====
def generate_forex_response(conversation):
    """
    This function simulates Sarah answering any Forex question.
    Handles everything: pips, lot size, risk management, strategies, support/resistance, etc.
    """
    last_question = conversation[-1]["content"].lower()

    # Examples of calculations and knowledge handling:
    if "pip" in last_question and "calculate" in last_question:
        return (
            "A pip is usually the fourth decimal in a currency pair (0.0001). "
            "To calculate pip value: (Pip in decimal) x (Lot size) x (Exchange rate)."
        )
    elif "lot size" in last_question and "risk" in last_question and "$" in last_question:
        return (
            "To calculate lot size based on risk: Lot Size = Risk Amount / "
            "(Stop Loss in pips x Pip Value per lot). "
            "Provide me your account balance, pips you want to risk, and risk in USD, "
            "and I can calculate it for you."
        )
    elif "grow account" in last_question or "balance" in last_question:
        return (
            "To grow an account safely: \n"
            "1. Determine risk per trade (1-2% recommended).\n"
            "2. Identify high-probability setups.\n"
            "3. Use proper lot sizing.\n"
            "4. Keep track of trades and adjust strategies over time.\n"
            "5. Be consistent and avoid revenge trading."
        )
    else:
        # Default knowledge response
        return (
            "I can explain pips, lot sizes, risk management, strategies, "
            "support/resistance, supply/demand, leverage, position sizing, and more. "
            "Ask me anything about Forex step by step."
        )

# ===== DISPATCHER HANDLERS =====
dispatcher.add_handler(CommandHandler("sarah", start_sarah))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

# ===== FLASK ROUTE =====
@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200
    else:
        return "Hello, Sarah Bot is running.", 200

# ===== MAIN =====
if __name__ == "__main__":
    # Set webhook automatically
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set and bot running...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
