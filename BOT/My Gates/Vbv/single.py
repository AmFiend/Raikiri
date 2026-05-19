import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

@Client.on_message(filters.command("vbv", [".", "/"]))
async def vbv_cmd(Client, message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        gateway = "3DS Lookup"

        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getmessage(message)
        if not getcc:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /vbv

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /vbv cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode="HTML")
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin_num = cc[:6]

        # Amex not supported
        if bin_num.startswith('3'):
            unsupport_resp = f"""❌ 𝗨𝗻𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝗖𝗮𝗿𝗱

{SYMBOL} 𝗖𝗮𝗿𝗱 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ American Express not supported

{SYMBOL} 𝗖𝗵𝗲𝗰ᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(unsupport_resp, quote=True, parse_mode="HTML")
            return

        processing_msg = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        processing_reply = await message.reply_text(processing_msg, quote=True, parse_mode="HTML")

        # Read VBV BIN file
        with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
            vbv_data = file.readlines()

        bin_found = False
        status = "𝗣𝗮𝘀𝘀𝗲𝗱 ✅"
        response_message = "3DS Passed"
        for line in vbv_data:
            if line.startswith(bin_num):
                bin_found = True
                bin_response = line.strip().split('|')[1]
                response_message = line.strip().split('|')[2]
                if "3D TRUE ❌" in bin_response:
                    status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
                break

        if not bin_found:
            status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
            response_message = "Lookup Card Error"

        start = time.perf_counter()
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        # Update progress dots
        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, processing_reply.id, secondresp, parse_mode="HTML")

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■■"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, processing_reply.id, thirdresp, parse_mode="HTML")

        finalresp = f"""{status}

{SYMBOL} 𝗖𝗮𝗿𝗱 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response_message}

{SYMBOL} 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} — {type_} — {level}
{SYMBOL} 𝗕𝗮𝗻𝗸: {bank}
{SYMBOL} 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time.perf_counter() - start:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""

        await Client.edit_message_text(message.chat.id, processing_reply.id, finalresp, disable_web_page_preview=True, parse_mode="HTML")
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        print(f"Error: {str(e)}")
