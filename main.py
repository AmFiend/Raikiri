from pyrogram import Client
import json
import os
from threading import Thread
from flask import Flask

from FUNC.server_stats import *

# Load config
with open("FILES/config.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)
    API_ID = DATA["API_ID"]
    API_HASH = DATA["API_HASH"]
    BOT_TOKEN = DATA["BOT_TOKEN"]

# Setup Pyrogram clients
user = Client(
    "Scrapper",
    api_id=API_ID,
    api_hash=API_HASH
)

plugins = dict(root="BOT")

bot = Client(
    "MY_BOT",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins
)

# Setup Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Uncomment if you want to send server alert on start
    # send_server_alert()

    print("Done Bot Active ✅")
    print("NOW START BOT ONCE MY MASTER")

    # Start Flask in a separate thread so it doesn't block bot
    Thread(target=run_flask).start()

    # Run the bot (this blocks)
    bot.run()
