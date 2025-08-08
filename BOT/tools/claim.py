from datetime import datetime, timedelta
from pyrogram import filters

@Client.on_message(filters.command("claim"))
async def claim_credits(client, message):
    user_id = message.from_user.id
    now = datetime.utcnow()

    user = await users_collection.find_one({"user_id": user_id})

    if user:
        last_claim = user.get("last_claim")
        if last_claim and now - last_claim < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_claim)
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await message.reply(f"⏳ You can claim again in {hours}h {minutes}m.")
            return

        new_credits = user.get("credits", 0) + 500
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"credits": new_credits, "last_claim": now}}
        )
    else:
        new_credits = 500
        await users_collection.insert_one({
            "user_id": user_id,
            "credits": new_credits,
            "last_claim": now
        })

    await message.reply(f"🎉 You claimed 500 free credits! You now have {new_credits} credits.")
