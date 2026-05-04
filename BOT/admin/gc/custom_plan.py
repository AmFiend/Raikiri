import traceback, json
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from datetime import date, timedelta

@Client.on_message(filters.command("csplan", [".", "/"]))
async def cmd_plan1(Client, message):
    try:
        user_id = str(message.from_user.id)
        OWNER_ID = json.loads(open("FILES/config.json", "r" , encoding="utf-8").read())["OWNER_ID"]
        if user_id not in OWNER_ID:
            resp = """✦ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ.
◈ ᴄᴏɴᴛᴀᴄᴛ @pipin_o
━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, message.id)
            return

        args = message.text.split(" ")
        if len(args) < 3:
            resp = """<b>Invalid command format. Usage: /csplan <user_id> <days></b>"""
            await message.reply_text(resp, message.id)
            return

        user_id = args[1]
        try:
            days = int(args[2])
        except ValueError:
            resp = """<b>Invalid number of days. Please provide an integer value.</b>"""
            await message.reply_text(resp, message.id)
            return

        paymnt_method = "Custom"
        registration_check = await getuserinfo(user_id)
        registration_check = str(registration_check)
        if registration_check == "None":
            resp = f"""<b>
Starter Plan Activation ꜰᴀɪʟᴇᴅ ✗
━━━━━━━━━━━━━━━━━━━━
◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> <a href="tg://user?id={user_id}"> {user_id}</a> 
⟢ <b>ᴘʟᴀɴ :</b> Starter Plan For {days} Days 
⟢ <b>ʀᴇᴀꜱᴏɴ :</b> Unregistered Users

◈ <b>ꜱᴛᴀᴛᴜꜱ :</b> ꜰᴀɪʟᴇᴅ ✗
</b>"""
            await message.reply_text(resp, message.id)
            return

        await check_negetive_credits(user_id)
        await csplan(user_id)
        receipt_id = await randgen(len=10)
        gettoday = str(date.today()).split("-")
        yy = gettoday[0]
        mm = gettoday[1]
        dd = gettoday[2]
        today = f"{dd}-{mm}-{yy}"
        getvalidity = str(date.today() + timedelta(days=days)).split("-")
        yy = getvalidity[0]
        mm = getvalidity[1]
        dd = getvalidity[2]
        validity = f"{dd}-{mm}-{yy}"

        user_resp = f"""<b>
✧ ꜱᴛᴀʀᴛᴇʀ ᴘʟᴀɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ✧

ID : <code>{user_id}</code>
⟢ <b>ᴘʟᴀɴ :</b> Custom Plan
◈ <b>ᴘʀɪᴄᴇ :</b> $
⟢ <b>ᴘᴜʀᴄʜᴀꜱᴇ ᴅᴀᴛᴇ :</b> {today}
◈ <b>ᴇxᴘɪʀʏ :</b> {validity}
⟢ <b>ᴠᴀʟɪᴅɪᴛʏ :</b> {days} Days
Status : Paid ☑️
◈ <b>ᴘᴀʏᴍᴇɴᴛ :</b> {paymnt_method}.
⟢ <b>ʀᴇᴄᴇɪᴘᴛ :</b> MASTR-{receipt_id}

This is a receipt for your plan. Save it in a Secure Place. This will help you if anything goes wrong with your plan purchases.

Have a Good Day.
━━━━━━━━━━━━━━━━━━━━
⟢ @pipin_o
</b>"""
        try:
            await Client.send_message(user_id, user_resp)
        except:
            pass

        ad_resp = f"""<b>
Starter Plan ᴀᴄᴛɪᴠᴀᴛᴇᴅ ✓ 
━━━━━━━━━━━━━━━━━━━━
◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> <a href="tg://user?id={user_id}"> {user_id}</a> 
⟢ <b>ᴘʟᴀɴ :</b> Starter Plan For {days} Days 
◈ <b>ᴇxᴘɪʀʏ :</b> {validity} 

Status : Successful
</b>"""
        await message.reply_text(ad_resp, message.id)

    except:
        await error_log(traceback.format_exc())