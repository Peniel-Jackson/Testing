# main.py
import os
import re
import requests
import json
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# -------------------------
# Config via environment
# -------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BING_API_KEY = os.getenv("BING_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 5000))

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not set in environment.")

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)
active_chats = set()

# -------------------------
# Web Search Helpers
# -------------------------
def search_with_serper(query, limit=5):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": limit}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        j = r.json()
        results = []
        for item in j.get("organic", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}")
        return results
    except Exception as e:
        return [f"Serper error: {e}"]

def search_with_bing(query, limit=5):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": limit}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        j = r.json()
        results = []
        for item in j.get("webPages", {}).get("value", [])[:limit]:
            title = item.get("name", "")
            snippet = item.get("snippet", "")
            link = item.get("url", "")
            results.append(f"{title}\n{snippet}\n{link}")
        return results
    except Exception as e:
        return [f"Bing error: {e}"]

def web_search(query):
    if SERPER_API_KEY:
        return search_with_serper(query)
    elif BING_API_KEY:
        return search_with_bing(query)
    else:
        return ["No search API configured. Provide SERPER_API_KEY or BING_API_KEY."]

# -------------------------
# Summarization
# -------------------------
def simple_summarize(query, snippets):
    text = "\n\n".join(snippets)
    return text[:1500] + "\n\n(Summary compiled from web data.)"

def summarize_with_openai(query, snippets):
    if not OPENAI_API_KEY:
        return simple_summarize(query, snippets)
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "You are Sarah, a professional forex and commodity trading assistant. "
        "Explain the answer in a simple, educational way for a trader. "
        "Use the web snippets below to answer clearly with examples, short paragraphs, "
        "and actionable insight (no financial advice disclaimers)."
    )
    user_prompt = f"Question: {query}\n\nWeb snippets:\n" + "\n---\n".join(snippets)
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 450,
        "temperature": 0.3,
    }
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return simple_summarize(query, snippets) + f"\n\n(OpenAI fallback due to: {e})"

# -------------------------
# Topic filters
# -------------------------
ALLOWED_KEYWORDS = [
    "forex","fx","pip","lot","lots","stop loss","take profit","support","resistance",
    "supply","demand","risk","account","strategy","trend","spread","leverage","margin",
    "entry","exit","indicator","btc","bitcoin","xau","xauusd","gold","trading"
]

def is_allowed_question(text):
    t = text.lower()
    return any(k in t for k in ALLOWED_KEYWORDS)

# -------------------------
# Lot size calculator
# -------------------------
def calculate_lot_size(pair, risk_usd, sl_pips, balance=None):
    pair = pair.upper()
    pip_value_per_standard = 10.0

    # adjust pip value for certain pairs
    if "JPY" in pair:
        pip_value_per_standard = 9.1
    elif "XAU" in pair:
        pip_value_per_standard = 1.0
    elif "BTC" in pair:
        pip_value_per_standard = 0.1

    lot = round(risk_usd / (sl_pips * pip_value_per_standard), 3)
    result = f"🧮 *Lot Size Estimate*\nRisk: ${risk_usd}\nStop Loss: {sl_pips} pips\nPair: {pair}\nEstimated Lot Size: {lot} standard lots (1.00 = 100k units)"
    if balance:
        risk_percent = (risk_usd / balance) * 100
        result += f"\nThis equals about {risk_percent:.2f}% of your ${balance} account."
    return result

# -------------------------
# Telegram Handlers
# -------------------------
def start_cmd(update, context):
    chat_id = update.effective_chat.id
    active_chats.add(chat_id)
    msg = (
        "👋 *Hey, I’m Sarah — your personal trading assistant.*\n\n"
        "I answer *Forex, Bitcoin (BTC), and Gold (XAUUSD)* trading questions.\n"
        "Examples:\n"
        "• What is support and resistance?\n"
        "• How to calculate lot size if I risk $50 with 20 pips SL?\n"
        "• How to grow a $100 account?\n"
        "• How to trade XAUUSD during news?\n\n"
        "Type your trading question anytime 👇🏽"
    )
    bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)

def handle_message(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text or ""

    if chat_id not in active_chats:
        bot.send_message(chat_id=chat_id, text="Please activate me first with /start.")
        return

    if not is_allowed_question(text):
        bot.send_message(chat_id=chat_id, text="⚠️ I only answer Forex, Bitcoin, and Gold trading questions.")
        return

    bot.send_chat_action(chat_id=chat_id, action="typing")

    # lot size quick calc
    try:
        match = re.search(r'(\w{6})', text.replace("/", "").upper())
        risk_match = re.search(r'\$(\d+(?:\.\d+)?)', text)
        pips_match = re.search(r'(\d+(?:\.\d+)?)\s*pips?', text.lower())
        bal_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:balance|account|usd)', text.lower())

        if match and risk_match and pips_match:
            pair = match.group(1)
            risk = float(risk_match.group(1))
            pips = float(pips_match.group(1))
            balance = float(bal_match.group(1)) if bal_match else None
            bot.send_message(chat_id=chat_id, text=calculate_lot_size(pair, risk, pips, balance), parse_mode=ParseMode.MARKDOWN)
            return
    except Exception:
        pass

    snippets = web_search(text)
    summary = summarize_with_openai(text, snippets) if OPENAI_API_KEY else simple_summarize(text, snippets)
    bot.send_message(chat_id=chat_id, text=summary[:4000], parse_mode=ParseMode.MARKDOWN)

# -------------------------
# Routes
# -------------------------
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Sarah AI Trading Assistant is live.", 200

dispatcher.add_handler(CommandHandler("start", start_cmd))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

if __name__ == "__main__":
    if WEBHOOK_URL:
        url = WEBHOOK_URL.rstrip("/") + "/" + TELEGRAM_BOT_TOKEN
        try:
            bot.set_webhook(url=url)
            print("✅ Webhook set to:", url)
        except Exception as e:
            print("⚠️ Could not set webhook:", e)
    app.run(host="0.0.0.0", port=PORT)
