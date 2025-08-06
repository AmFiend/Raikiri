import os
import json
from pathlib import Path
from pyrogram import Client, filters
from FUNC.defs import *
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *
from FUNC.scraperfunc import *


with open("FILES/config.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)
    API_ID = DATA["API_ID"]
    API_HASH = DATA["API_HASH"]

user = Client("Scrapper", api_id=API_ID, api_hash=API_HASH)


@Client.on_message(filters.command("scr", [".", "/"]))
async def scrapper_cc(Client, message):
    try:
        checkall = await check_all_thing(Client, message)
        if checkall[0] is False:
            return

        user_id = str(message.from_user.id)
        chat_type = message.chat.type
        chat_id = str(message.chat.id)

        # Parse command arguments
        try:
            splitter = message.text.split(" ")[1:]
            channel_link = splitter[0]
            limit = int(splitter[1])
        except:
            usage_text = """<b>
𝗪𝗿𝗼𝗻𝗴 𝗙𝗼𝗿𝗺𝗮𝘁 ❌

𝗨𝘀𝗮𝗴𝗲:
𝗙𝗼𝗿 𝗣𝘂𝗯𝗹𝗶𝗰 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr username 50</code>

𝗙𝗼𝗿 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr https://t.me/+invitecode 50</code>
</b>"""
            await message.reply_text(usage_text, reply_to_message_id=message.id)
            return

        regdata = fetchinfo(user_id)
        if regdata is None:
            await message.reply_text(
                "𝗬𝗢𝗨 𝗔𝗥𝗘 𝗡𝗢𝗧 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗 ⚠️ 𝗨𝗦𝗘 /register",
                reply_to_message_id=message.id
            )
            return

        status = regdata[2]
        credit = int(regdata[5])
        GROUP = open("plugins/group.txt").read().splitlines()

        if chat_type == "private" and status == "FREE":
            await message.reply_text(
                "𝗢𝗡𝗟𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗠𝗕𝗘𝗥𝗦 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗕𝗢𝗧 𝗜𝗡 𝗣𝗠 ⚠️ @livechargeapproved",
                reply_to_message_id=message.id
            )
            return

        if chat_type in ["group", "supergroup"] and chat_id not in GROUP:
            await message.reply_text(
                "𝗨𝗡𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗖𝗛𝗔𝗧 ❌. 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 @Nairobiangoon",
                reply_to_message_id=message.id
            )
            return

        if credit < 3:
            await message.reply_text(
                "𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗖𝗥𝗘𝗗𝗜𝗧 ⚠️. 𝗨𝗦𝗘 /buy 𝗧𝗢 𝗥𝗘𝗖𝗛𝗔𝗥𝗚𝗘.",
                reply_to_message_id=message.id
            )
            return

        if status == 'FREE' and limit > 5000:
            await message.reply_text(
                "𝗙𝗥𝗘𝗘 𝗨𝗦𝗘𝗥𝗦 𝗔𝗥𝗘 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗧𝗢 5000 ❌",
                reply_to_message_id=message.id
            )
            return

        if status == 'PREMIUM' and limit > 60000:
            await message.reply_text(
                "𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥𝗦 𝗔𝗥𝗘 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗧𝗢 𝟲𝟬𝗞 ❌",
                reply_to_message_id=message.id
            )
            return

        delete = await message.reply_text("𝗦𝗰𝗿𝗮𝗽𝗶𝗻𝗴 𝗪𝗮𝗶𝘁...", reply_to_message_id=message.id)

        # Join group/channel
        title = ""
        try:
            if "https" in channel_link:
                join = await user.join_chat(channel_link)
                title = join.title
                channel_id = join.id
            else:
                chat_info = await user.get_chat(channel_link)
                title = chat_info.title
                channel_id = chat_info.id
        except Exception as e:
            await Client.delete_messages(message.chat.id, delete.id)
            await message.reply_text(f"𝗝𝗼𝗶𝗻 𝗘𝗿𝗿𝗼𝗿 ❌\n\n{str(e)}", reply_to_message_id=message.id)
            return

        amt_cc = 0
        duplicate = 0
        file_name = f"{limit}x_CC_Scraped_By_@BarryxBot.txt"
        cclist = []

        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                cclist = f.read().splitlines()

        async for msg in user.get_chat_history(channel_id, limit):
            if msg.text:
                all_cards = msg.text.split('\n')
                for x in all_cards:
                    car = getcards(x)
                    if car:
                        cc, mes, ano, cvv = car
                        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
                        if fullcc in cclist:
                            duplicate += 1
                        else:
                            with open(file_name, "a") as f:
                                f.write(f"{fullcc}\n")
                            cclist.append(fullcc)
                            amt_cc += 1

        cc_found = amt_cc
        await Client.delete_messages(message.chat.id, delete.id)

        if cc_found == 0:
            await message.reply_text("𝗡𝗢 𝗩𝗔𝗟𝗜𝗗 𝗖𝗔𝗥𝗗𝗦 𝗙𝗢𝗨𝗡𝗗 ❌", reply_to_message_id=message.id)
            return

        caption = f"""
[ϟ] 𝑪𝑪 𝑺𝒄𝒓𝒂𝒑𝒆𝒅 ✅
━━━━━━━━━━━━━━━━━━
[ϟ] Source: {title}
[ϟ] Requested: <code>{limit}</code>
[ϟ] Found: <code>{cc_found}</code>
[ϟ] Duplicates: <code>{duplicate}</code>
[ϟ] User: <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> [{status}]
[ϟ] Bot By: <a href="tg://user?id=6440962840">Nairobiangoon</a>
━━━━━━━━━━━━━━━━━━
"""
        await message.reply_document(document=file_name, caption=caption, reply_to_message_id=message.id)

        # Deduct credit
        updatedata(user_id, "credits", credit - 1)

        # Delete file after sending
        Path(file_name).unlink(missing_ok=True)

    except Exception as e:
        await message.reply_text(f"𝗘𝗿𝗿𝗼𝗿: {str(e)}", reply_to_message_id=message.id)
