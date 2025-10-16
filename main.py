from flask import Flask, request
import requests
import openai
import os

# ✅ FIX for proxy bug — use the older stable OpenAI library syntax
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ Sarah AI Forex Expert Function
def ask_sarah(prompt):
    # Topics allowed: forex, bitcoin trading, gold (xauusd) trading
    forex_keywords = ["forex", "trading", "support", "resistance", "candlestick", "chart", "pip", "lot", "eurusd", "gbpusd", "usd", "xauusd", "gold", "btc", "bitcoin"]
    if not any(word in prompt.lower() for word in forex_keywords):
        return "⚠️ I only answer Forex, Bitcoin trading, and XAUUSD (gold) related questions. Please ask something in that area."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Sarah, a friendly and intelligent forex mentor from FirePips Forex Academy. "
                        "You explain concepts like price action, support/resistance, risk management, candlestick patterns, "
                        "and trading psychology clearly and helpfully. "
                        "You can also explain Bitcoin and XAUUSD trading concepts, but nothing outside trading."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("Sarah error:", e)
        return "😅 Sarah is currently unavailable. Please try again soon."

# ✅ Send Telegram message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# ✅ Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    # Start command
    if text.lower() == "/start":
        send_message(
            chat_id,
            "👋 Hello! I'm *Sarah*, your Forex mentor from FirePips Forex Academy.\n\n"
            "You can ask me any trading question — like:\n"
            "💬 /sarah what are support and resistance zones?\n"
            "💬 /sarah how do I trade gold (XAUUSD)?\n\n"
            "I only answer forex, bitcoin, or gold-related trading questions."
        )
        return "ok"

    # Sarah command
    if text.lower().startswith("/sarah"):
        user_question = text[6:].strip()
        if not user_question:
            send_message(chat_id, "Please ask a question after /sarah, e.g. `/sarah what is a stop loss?`")
            return "ok"

        answer = ask_sarah(user_question)
        send_message(chat_id, answer)
        return "ok"

    # Fallback for non-sarah commands
    send_message(chat_id, "Use /sarah followed by your trading question, or /start to begin.")
    return "ok"

@app.route("/")
def home():
    return "🔥 Sarah AI Forex Bot Running Successfully!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
