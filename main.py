import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging

# ------------------- Variables -------------------
BOT_TOKEN = "8216881905:AAFo0Lnufs8crn2IZ-p8gSaaxV3QK-i0KLs"  # your bot token
WEBHOOK_URL = "https://testing-20rh.onrender.com"              # your render app URL
# -------------------------------------------------

# ------------------ Logging ----------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
# -------------------------------------------------

# ------------- Flask & Bot Setup -----------------
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
# -------------------------------------------------

# ---------------- AI Answer Function -------------
def get_ai_answer(question):
    """
    Replace this with your AI logic or API call to fetch answers.
    For now, a simple placeholder function.
    """
    # Example of simple responses
    question_lower = question.lower()
    if "pip" in question_lower:
        return ("In forex, a pip (percentage in point) is the smallest price move "
                "that a given exchange rate can make based on market convention. "
                "For most currency pairs, 1 pip = 0.0001. To calculate pips: "
                "subtract the entry price from the exit price and multiply by 10,000.")
    elif "lot" in question_lower:
        return "A lot is a standardized quantity of the base currency in forex trading. 1 standard lot = 100,000 units."
    else:
        return "I'm searching the forex info... Here's a quick answer: " + question

# -------------------------------------------------

# ---------------- Commands -----------------------
def sarah_command(update, context):
    """Handle /sarah command for any forex question."""
    if context.args:
        user_question = ' '.join(context.args)
        answer = get_ai_answer(user_question)
    else:
        answer = "Please ask a forex-related question after /sarah."
    update.message.reply_text(answer)

# Add handlers
dispatcher.add_handler(CommandHandler("sarah", sarah_command))
# -------------------------------------------------

# ------------- Flask Webhook Route ---------------
@app.route('/', methods=['POST'])
def webhook():
    """Receives updates from Telegram."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is live!", 200
# -------------------------------------------------

# ---------------- Set Webhook --------------------
@app.before_first_request
def set_webhook():
    bot.set_webhook(WEBHOOK_URL)
# -------------------------------------------------

# ----------------- Run Flask ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# -------------------------------------------------
