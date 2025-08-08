from pyrogram import Client, filters

@Client.on_message(filters.command("referral", [".", "/"]))
async def referral_cmd(client, message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    await message.reply_text(
        f"🎉 Your referral link:\n\n{referral_link}\n\n"
        "Share this link with friends and earn credits when they start the bot using it!"
    )
  
