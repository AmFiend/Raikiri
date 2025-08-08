from pyrogram import Client, filters
from datetime import datetime, timedelta
from FUNC.usersdb_func import usersdb, check_negetive_credits
from FUNC.defs import error_log

# Instead of importing 'bot' from main.py, use this:
# The client will be passed automatically by plugin loader

@Client.on_message(filters.command("claim", [".", "/"]))
async def cmd_claim(client, message):
    try:
        user_id = str(message.from_user.id)
        now = datetime.utcnow()

        user = usersdb.find_one({"id": user_id})

        if user and "last_claim" in user:
            last_claim = user["last_claim"]
            if isinstance(last_claim, str):
                last_claim = datetime.fromisoformat(last_claim)
            if now - last_claim < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_claim)
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await message.reply_text(
                    f"⏳ You already claimed your free credits. "
                    f"Come back in {hours}h {minutes}m to claim again."
                )
                return

        if user:
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
                "last_claim": now.isoformat(),
                "status": "FREE",
                "plan": "N/A",
                "expiry": "N/A"
            })

        await message.reply_text(
            f"🎉 You have successfully claimed 500 free credits! "
            f"You now have {new_credits} credits."
        )

    except Exception as e:
        await error_log(f"Error in /claim command:\n{e}")
        await message.reply_text("❌ An error occurred while processing your claim. Please try again later.")
            
