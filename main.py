import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from apscheduler.schedulers.background import BackgroundScheduler

# -------------------------
# Config
# -------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Telegram bot token
bot = Bot(token=BOT_TOKEN)
app = Flask(_name_)

# -------------------------
# Dispatcher setup
# -------------------------
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# -------------------------
# Command Handlers
# -------------------------
def start(update, context):
    update.message.reply_text("Hi! I'm Sarah, your Forex assistant. 💹")

def help_command(update, context):
    update.message.reply_text("Commands available:\n/start\n/help")

def echo(update, context):
    update.message.reply_text(f"You said: {update.message.text}")

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# -------------------------
# Webhook route
# -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# -------------------------
# Health check route
# -------------------------
@app.route("/")
def index():
    return "Sarah bot is running ✅"

# -------------------------
# Optional Scheduler (example)
# -------------------------
def periodic_task():
    print("Periodic task running...")  # Replace with any recurring task

scheduler = BackgroundScheduler()
scheduler.add_job(periodic_task, 'interval', minutes=5)
scheduler.start()

# -------------------------
# Run Flask app (Render port fix)
# -------------------------
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
