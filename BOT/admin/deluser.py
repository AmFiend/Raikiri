import traceback
import json
from pyrogram import Client, filters
from FUNC.usersdb_func import *


async def remove_user_from_db(user_id):
    try:
        await usersdb.delete_one({"id": user_id})
    except:
        pass


@Client.on_message(filters.command("deluser", [".", "/"]))
async def cmd_deluser(Client, message):
    try:
        user_id = str(message.from_user.id)
        OWNER_ID = json.loads(
            open("FILES/config.json", "r", encoding="utf-8").read())["OWNER_ID"]

        if user_id not in OWNER_ID:
            resp = """<b>✦ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ ✦

⟢ To perform this action, you need admin level power. 

◈ ᴄᴏɴᴛᴀᴄᴛ @pipin_o</b>"""
            await message.reply_text(resp, message.id)
            return

        try:
            if message.reply_to_message:
                user_id = str(message.reply_to_message.from_user.id)
            else:
                user_id = str(message.text.split(" ")[1])
        except Exception as e:
            resp = """<b>
✦ ɪɴᴠᴀʟɪᴅ ɪᴅ ✦

⟢ Not Found Valid ID From Your Input.
            </b>"""
            await message.reply_text(resp, message.id)
            return

        await remove_user_from_db(user_id)

        resp = f"""
✧ ᴜꜱᴇʀ ʀᴇᴍᴏᴠᴇᴅ ✧

◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ User has been removed from the database.
        """
        await message.reply_text(resp, message.id)

    except Exception as e:
        await error_log(traceback.format_exc())