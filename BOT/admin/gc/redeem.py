from .func import *
from pyrogram import Client, filters
from FUNC.usersdb_func import *

@Client.on_message(filters.command("redeem", [".", "/"]))
async def cmd_gc(Client, message):
    try:
        user_id = str(message.from_user.id)
        regdata = await getuserinfo(user_id)
        regdata = str(regdata)

        if regdata == "None":
            resp = f"""<b>
✦ ᴜɴʀᴇɢɪꜱᴛᴇʀᴇᴅ ✦

⟢ You Can't Use Me Unless You Register First .

↪ ᴛʏᴘᴇ /register ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ
</b>"""
            await message.reply_text(resp, message.id)
            return

        try:
            gc = message.text.split(" ")[1]
        except:
            resp = "<b>✦ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɢɪꜰᴛᴄᴏᴅᴇ ✗ ✦</b>"
            await message.reply_text(resp, message.id)
            return

        detail = await getgc(gc)
        if str(detail) == "None":
            resp = "<b>✦ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɢɪꜰᴛᴄᴏᴅᴇ ✗ ✦</b>"
            await message.reply_text(resp, message.id)
            return

        get_user_info = usersdb.find_one({"id": user_id})
        if "∞" in get_user_info["plan"]:
            resp = "<b>✦ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ ✦</b>"
            await message.reply_text(resp, message.id)
            return

        status = str(detail["status"])
        type_ = str(detail["type"])   # rename to avoid shadowing built-in type

        if status == "ACTIVE" and type_ == "PREMIUM":
            await onlycredits(user_id)
            await updategc(gc)
            resp = f"""<b>
Redeemed ✓
━━━━━━━━━━━━━━━━━━━━
◈ ◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}
◈ ◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ Congratz ! Your Provided Giftcode Successfully Redeemed to Your Acoount And You Got "100 Credits + Premium Subscription " .
</b>"""
            await message.reply_text(resp, message.id)

        elif status == "ACTIVE" and type_ == "PLAN1":
            await plan1gc(user_id)
            await updategc(gc)
            resp = f"""<b>
Redeemed ✓
━━━━━━━━━━━━━━━━━━━━
◈ ◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}
◈ ◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ Congratz ! Your Provided Giftcode Successfully Redeemed to Your Acoount And You Got "Starter Plan For 7 Days " .
</b>"""
            await message.reply_text(resp, message.id)

        elif status == "ACTIVE" and type_ == "PLAN2":
            await plan2gc(user_id)
            await updategc(gc)
            resp = f"""<b>
Redeemed ✓
━━━━━━━━━━━━━━━━━━━━
◈ ◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}
◈ ◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ Congratz ! Your Provided Giftcode Successfully Redeemed to Your Acoount And You Got "Silver Plan For 15 Days " .
</b>"""
            await message.reply_text(resp, message.id)

        elif status == "ACTIVE" and type_ == "PLAN3":
            await plan3gc(user_id)
            await updategc(gc)
            resp = f"""<b>
Redeemed ✓
━━━━━━━━━━━━━━━━━━━━
◈ ◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}
◈ ◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ Congratz ! Your Provided Giftcode Successfully Redeemed to Your Acoount And You Got "Gold Plan For 30 Days " .
</b>"""
            await message.reply_text(resp, message.id)

        # NEW: Handle variable‑day keys
        elif status == "ACTIVE" and type_ == "VARIABLE":
            days = detail.get("days", 7)   # fallback to 7 days if missing
            await variable_plan_gc(user_id, days)
            await updategc(gc)
            resp = f"""<b>
Redeemed ✓
━━━━━━━━━━━━━━━━━━━━
◈ ◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}
◈ ◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> {user_id}

⟢ Congratz ! Your Provided Giftcode Successfully Redeemed to Your Account And You Got "Premium Plan For {days} Days" .
</b>"""
            await message.reply_text(resp, message.id)

        elif status == "USED":
            resp = f"""<b>
✦ ᴀʟʀᴇᴀᴅʏ ʀᴇᴅᴇᴇᴍᴇᴅ ✦

◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}

⟢ This Giftcode is Already Redeemed by another users .
</b> """
            await message.reply_text(resp, message.id)

        else:
            resp = f"""<b>
✦ ɪɴᴠᴀʟɪᴅ ɢɪꜰᴛᴄᴏᴅᴇ ✦

◈ <b>ɢɪꜰᴛᴄᴏᴅᴇ :</b> {gc}

⟢ We can't find any giftcode like that . your provided giftcode is invalid .   
        </b>"""
            await message.reply_text(resp, message.id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
