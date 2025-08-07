from pyrogram import Client, filters
from pyrogram.types import Message
import time
from datetime import date
from plugins.func.users_sql import fetchinfo, updatedata  # adjust path if needed

@Client.on_message(filters.command("claim", [".", "/"]))
async def claim_credits(Client, message: Message):
    try:
        user_id = str(message.from_user.id)
        username = message.from_user.username or "None"
        now = int(time.time())

        user_data = fetchinfo(user_id)
        if user_data is None:
            await message.reply_text("❌ You're not registered. Please use /register first.")
            return

        last_claim = user_data.get("last_claim", 0)
        credits = int(user_data.get("credits", 0))

        if now - last_claim < 86400:  # 24 hours = 86400 seconds
            remaining = 86400 - (now - last_claim)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await message.reply_text(f"⏳ You can claim again in {hours}h {minutes}m.")
            return

        new_credits = credits + 500
        updatedata(user_id, "credits", new_credits)
        updatedata(user_id, "last_claim", now)

        await message.reply_text(f"🎁 You've claimed 500 credits!\n💰 New Balance: {new_credits}")

    except Exception as e:
        import traceback
        await message.reply_text("❌ Something went wrong.")
        print(traceback.format_exc())
