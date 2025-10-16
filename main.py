import os
import logging
from flask import Flask, request
import requests
from openai import OpenAI

# ---------------- CONFIG ----------------
TELEGRAM_BOT_TOKEN = "8216881905:AAFo0Lnufs8crn2IZ-p8gSaaxV3QK-i0KLs"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # set this on Render
WEBHOOK_URL_PATH = "/webhook"

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ----------------------------------------
def send_message(chat_id, text):
    """Send a message to the Telegram user."""
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# ----------------------------------------
@app.route("/", methods=["GET"])
def home():
    return "Sarah AI Forex Bot is live!", 200

@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    """Main webhook to handle Telegram updates."""
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()

        # Handle /start
        if text.lower() == "/start":
            send_message(chat_id, "👋 Hi, I’m Sarah — your Forex assistant.\nAsk me any Forex, Bitcoin, or XAUUSD-related trading question!")
            return "ok", 200

        # Handle /sarah
        elif text.lower() == "/sarah":
            send_message(chat_id, "✅ Sarah is now active! You can now ask your Forex, Bitcoin, or XAUUSD questions.")
            return "ok", 200

        else:
            # Only respond to trading-related questions
            if any(keyword in text.lower() for keyword in ["forex", "xauusd", "gold", "btc", "bitcoin", "pip", "lot", "risk", "leverage", "support", "resistance", "trading", "account"]):
                answer = ask_sarah(text)
                send_message(chat_id, answer)
            else:
                send_message(chat_id, "⚠️ Sorry, I only answer Forex, Bitcoin, and XAUUSD-related trading questions.")
    return "ok", 200

# ----------------------------------------
def ask_sarah(question):
    """Ask Sarah AI (OpenAI model) to answer the trading question."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are Sarah, an advanced forex trading assistant. "
                    "Answer in a simple, detailed, and practical way. "
                    "Explain calculations (like pip, lot size, risk %), strategies, and price concepts. "
                    "You can also answer about Bitcoin and XAUUSD, but only in trading context. "
                    "Do NOT answer non-trading questions."
                )},
                {"role": "user", "content": question}
            ],
            temperature=0.6,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Sarah error: {e}")
        return "❌ Sorry, I had an issue answering that. Please try again."

# ----------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
