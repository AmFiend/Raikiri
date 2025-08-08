from datetime import datetime, timedelta
from pyrogram import filters
from FUNC.usersdb_func import usersdb  # Import your collection

@Client.on_message(filters.command("claim", [".", "/"]))
async def cmd_claim(Client, message):
    try:
        user_id = str(message.from_user.id)
        now = datetime.utcnow()

        user = usersdb.find_one({"id": user_id})

        if user:
            last_claim = user.get("last_claim")
            if isinstance(last_claim, str):
                last_claim = datetime.fromisoformat(last_claim)
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

    except Exception:
        import traceback
        print(traceback.format_exc())
        await message.reply_text("❌ An error occurred while processing your claim.")
