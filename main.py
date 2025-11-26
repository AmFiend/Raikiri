from pyrogram import Client 
import json
from FUNC.server_stats import *

plugins = dict(root="BOT")

with open("FILES/config.json", "r", encoding="utf-8") as f:
    DATA      = json.load(f)
    API_ID    = DATA["API_ID"]
    API_HASH  = DATA["API_HASH"]
    BOT_TOKEN = DATA["BOT_TOKEN"]

user = Client(
    "Scrapper",
    api_id=API_ID,
    api_hash=API_HASH,
    parse_mode="HTML"   # ← correct for your version
)

bot = Client(
    "MY_BOT",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins,
    parse_mode="HTML"   # ← correct for your version
)

if __name__ == "__main__":
    print("Done Bot Active ✅")
    print("NOW START BOT ONCE MY MASTER")
    bot.run()
