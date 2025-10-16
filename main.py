import os
import logging
from flask import Flask, request
import telebot
from openai import OpenAI
import requests

# ======================
# --- Configuration ----
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8216881905:AAFo0Lnufs8crn2IZ-p8gSaaxV3QK-i0KLs")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"  # FIXED: webhook path now explicit
WEBHOOK_URL = f"https://testing-20rh.onrender.com{WEBHOOK_PATH}"

# ======================
# --- Setup Logging ----
# ======================
logging.basicConfig(level=logging.INFO)

# ======================
# --- Init Flask & Bot --
# ======================
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# ======================
# --- Set Webhook -------
# ======================
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    res = requests.get(url)
    if res.status_code == 200:
        logging.info(f"Webhook set successfully ✅ -> {WEBHOOK_URL}")
    else:
        logging.error(f"Failed to set webhook ❌: {res.text}")

set_webhook()

# ======================
# --- Forex Answerer ----
# ======================
def get_forex_answer(question: str) -> str:
    """Generate AI-powered forex or trading answer"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are Sarah, a forex and trading assistant. "
                    "You only answer forex, trading, Bitcoin, or XAUUSD-related questions. "
                    "If a question is outside forex/trading, reply: "
                    "'Sorry, I only answer forex and trading-related questions.' "
                    "When explaining, use examples, steps, and simple explanations a beginner can understand."
                )},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return "Sorry, there was an error fetching your forex answer."

# ======================
# --- Telegram Routes ---
# ======================
@app.route(WEBHOOK_PATH, methods=["POST"])  # FIXED path
def webhook():
    update = request.get_json()
    if not update:
        return "No update", 400

    try:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    except Exception as e:
        logging.error(f"Error processing update: {e}")

    return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return "Sarah Forex Bot is live ✅", 200

# ======================
# --- Bot Commands -----
# ======================
@bot.message_handler(commands=["start"])
def start_command(message):
    bot.reply_to(
        message,
        "Hey there 👋 I’m Sarah — your forex trading assistant!\n\n"
        "I can help you understand trading concepts, calculate risk, "
        "and answer questions about forex, Bitcoin, or XAUUSD.\n\n"
        "Just type your question anytime, for example:\n"
        "• What does pip mean?\n"
        "• How can I calculate my lot size?\n"
        "• What are support and resistance zones?"
    )


@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    question = message.text.strip()

    # Only handle forex/trading related messages
    keywords = ["forex", "pip", "lot", "trade", "xauusd", "gold", "bitcoin", "btc", "support", "resistance"]
    if any(word in question.lower() for word in keywords):
        answer = get_forex_answer(question)
        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "Sorry, I only answer forex and trading-related questions.")


# ======================
# --- Run Flask --------
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
