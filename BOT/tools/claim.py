from datetime import datetime, timedelta
from pyrogram import filters
from FUNC.usersdb_func import *  # Assuming users_collection or db funcs here

@Client.on_message(filters.command("claim", [".", "/"]))
async def cmd_claim(Client, message):
    try:
        user_id = str(message.from_user.id)

        # Assuming you have a function get_user_claim_data(user_id) returning user dict or None
        user = await get_user_claim_data(user_id)  

        now = datetime.utcnow()

        if user:
            last_claim = user.get("last_claim")
            if last_claim and (now - last_claim).total_seconds() < 24 * 3600:
                remaining_seconds = 24*3600 - (now - last_claim).total_seconds()
                hours = int(remaining_seconds // 3600)
                minutes = int((remaining_seconds % 3600) // 60)
                await message.reply_text(f"⏳ You can claim again in {hours}h {minutes}m.")
                return

            new_credits = user.get("credits", 0) + 500
            await update_user_claim_data(user_id, credits=new_credits, last_claim=now)
        else:
            new_credits = 500
            await create_user_claim_data(user_id, credits=new_credits, last_claim=now)

        await message.reply_text(f"🎉 You claimed 500 free credits! You now have {new_credits} credits.")

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text("❌ An error occurred while processing your claim.")

