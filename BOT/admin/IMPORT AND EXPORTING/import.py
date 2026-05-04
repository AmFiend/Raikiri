import traceback
from pyrogram import Client, filters
from FUNC.usersdb_func import *
import asyncio
import pymongo
import json
from mongodb import client, folder
from pathlib import Path
import time

users_db = folder.USERSDB
chats_auth_db = folder.CHATS_AUTH
gc_db = folder.GCDB


@Client.on_message(filters.command("import", [".", "/"]))
async def stats(Client, message):
    try:
        user_id = str(message.from_user.id)
        OWNER_ID = json.loads(open("FILES/config.json", "r" , encoding="utf-8").read())["OWNER_ID"]
        if user_id not in OWNER_ID:
            resp = """✦ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ.
◈ ᴄᴏɴᴛᴀᴄᴛ @pipin_o
━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            msg1 = await message.reply_text(resp, message.id)
        else:
            try:
                file_name = "import.json"
                await message.reply_to_message.download(file_name=file_name)
                all_data = (
                    open("downloads/import.json", "r", encoding="UTF-8")
                    .read()
                    .splitlines()
                )
                data_list = []
                amt = 0
                for i in all_data:
                    amt += 1
                    data = json.loads(i)
                    data_list.append(data)
                getfile = True
            except Exception as e:
                getfile = False
            if getfile == True:
                try:
                    msg = message.text.split(" ")[1]
                    status = True
                except:
                    status = False
                    resp = f"""<b>
Wrong Format ❌

Usage:
For Users Data Import : /import users
For Chats Data Import : /import chats
For GC Data Import : /import gc
                   </b> """
                    await message.reply_text(resp, message.id)
                if "users" in msg and status == True:
                    try:
                        resp = "<b>✦ ɪᴍᴘᴏʀᴛɪɴɢ ᴛᴏ ᴅᴀᴛᴀʙᴀꜱᴇ... ✦</b>"
                        delete = await message.reply_text(resp, message.id)
                        start = time.time()
                        insert = users_db.insert_many(data_list)
                        end = time.time()
                        await Client.delete_messages(message.chat.id, delete.id)
                        resp = f"""<b>
IMPORT ᴅᴏɴᴇ ✓

◈ <b>ᴛᴏᴛᴀʟ :</b> {amt}
⟢ <b>ᴛʏᴘᴇ :</b> JSON
◈ <b>ᴜᴘᴅᴀᴛᴇᴅ :</b> a while ago
Time Taken: {end - start:0.4f}s
⟢ <b>ʀᴇǫᴜᴇꜱᴛᴇᴅ :</b> {message.date}
                        </b>"""
                        await message.reply_text(resp, message.id)
                        if insert:
                            name = "downloads/import.json"
                            my_file = Path(name)
                            my_file.unlink()
                    except:
                        await message.reply_text("ERROR HAPPEND IMPORTING", message.id)
                elif "chats" in msg and status == True:
                    try:
                        resp = "<b>✦ ɪᴍᴘᴏʀᴛɪɴɢ ᴛᴏ ᴅᴀᴛᴀʙᴀꜱᴇ... ✦</b>"
                        delete = await message.reply_text(resp, message.id)
                        start = time.time()
                        insert = chats_auth_db.insert_many(data_list)
                        end = time.time()
                        await Client.delete_messages(message.chat.id, delete.id)
                        resp = f"""<b>
IMPORT ᴅᴏɴᴇ ✓

◈ <b>ᴛᴏᴛᴀʟ :</b> {amt}
⟢ <b>ᴛʏᴘᴇ :</b> JSON
◈ <b>ᴜᴘᴅᴀᴛᴇᴅ :</b> a while ago
Time Taken: {end - start:0.4f}s
⟢ <b>ʀᴇǫᴜᴇꜱᴛᴇᴅ :</b> {message.date}
                        </b>"""
                        await message.reply_text(resp, message.id)
                        if insert:
                            name = "downloads/import.json"
                            my_file = Path(name)
                            my_file.unlink()
                    except:
                        await message.reply_text("ERROR HAPPEND IMPORTING", message.id)
                elif "gc" in msg and status == True:
                    try:
                        resp = "<b>✦ ɪᴍᴘᴏʀᴛɪɴɢ ᴛᴏ ᴅᴀᴛᴀʙᴀꜱᴇ... ✦</b>"
                        delete = await message.reply_text(resp, message.id)
                        start = time.time()
                        insert = gc_db.insert_many(data_list)
                        end = time.time()
                        await Client.delete_messages(message.chat.id, delete.id)
                        resp = f"""<b>
IMPORT ᴅᴏɴᴇ ✓

◈ <b>ᴛᴏᴛᴀʟ :</b> {amt}
⟢ <b>ᴛʏᴘᴇ :</b> JSON
◈ <b>ᴜᴘᴅᴀᴛᴇᴅ :</b> a while ago
Time Taken: {end - start:0.4f}s
⟢ <b>ʀᴇǫᴜᴇꜱᴛᴇᴅ :</b> {message.date}
                        </b>"""
                        await message.reply_text(resp, message.id)
                        if insert:
                            name = "downloads/import.json"
                            my_file = Path(name)
                            my_file.unlink()
                    except:
                        await message.reply_text(
                            "<b>✦ ɪᴍᴘᴏʀᴛ ᴇʀʀᴏʀ ✗ ✦</b>", message.id
                        )
                else:
                    await message.reply_text(
                        "<b>✦ ꜱᴘᴇᴄɪꜰʏ ᴅᴀᴛᴀʙᴀꜱᴇ ɴᴀᴍᴇ ✗ ✦</b>", message.id
                    )
            else:
                await message.reply_text(
                    "<b>✦ ᴘʀᴏᴠɪᴅᴇ ᴊꜱᴏɴ ꜰɪʟᴇ ✗ ✦</b>", message.id
                )
    except Exception as e:
        await message.reply_text(e, message.id)