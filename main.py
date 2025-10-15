import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.ext.dispatcher import run_async

# ===== VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your Telegram bot token
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your webhook URL
CONVERSATION_MEMORY = {}  # Stores ongoing conversations with users

# ===== FLASK APP =====
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# ===== COMMANDS =====
def start_sarah(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    CONVERSATION_MEMORY[user_id] = []  # Initialize conversation memory
    update.message.reply_text("Hello! I am Sarah, your Forex assistant. Ask me anything about Forex.")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    # If user hasn't started /sarah session, ignore
    if user_id not in CONVERSATION_MEMORY:
        return

    # Append message to conversation memory
    CONVERSATION_MEMORY[user_id].append({"role": "user", "content": text})

    # Generate response based on conversation memory
    response = generate_forex_response(CONVERSATION_MEMORY[user_id])

    # Append bot response to memory
    CONVERSATION_MEMORY[user_id].append({"role": "assistant", "content": response})

    # Send response
    update.message.reply_text(response)

# ===== FOREX RESPONSE FUNCTION =====
def generate_forex_response(conversation):
    """
    Simulate Sarah answering Forex questions.
    This function can be extended with your AI logic.
    """
    last_question = conversation[-1]["content"]

    # Example simple logic (expand this for real AI knowledge)
    response = f"Answering your Forex question: '{last_question}'.\n\n" \
               "I can explain pips, lot sizes, risk management, strategies, " \
               "support/resistance, supply/demand, leverage, and more."
    return response

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
