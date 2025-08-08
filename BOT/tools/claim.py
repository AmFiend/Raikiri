from datetime import datetime, timedelta
from pyrogram import filters
from main import bot  # your client instance from main.py
from FUNC.usersdb_func import usersdb  # your users collection

@bot.on_message(filters.command("claim", [".", "/"]))
async def cmd_claim(client, message):
    try:
        user_id = str(message.from_user.id)
        now = datetime.utcnow()

        user = usersdb.find_one({"id": user_id})

        if user:
            last_claim = user.get("last_claim")
            if isinstance(last_claim, str):
                try:
                    last_claim = datetime.fromisoformat(last_claim)
                except Exception:
                    last_claim = None
            if last_claim and (now - last_claim) < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_claim)
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await message.reply_text(f"⏳ You can claim again in {hours}h {minutes}m.")
                return

            new_credits = user.get("credit", 0) + 500
            usersdb.update_one(
                {"id": user_id},
                {"$set": {"credit": new_credits, "last_claim": now.isoformat()}}
            )
        else:
            new_credits = 500
            usersdb.insert_one({
                "id": user_id,
                "credit": new_credits,
                "last_claim": now.isoformat()
            })

        await message.reply_text(f"🎉 You claimed 500 free credits! You now have {new_credits} credits.")

    except Exception as e:
        print(f"Error in /claim command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text("❌ An error occurred while processing your claim.")
