import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *

@Client.on_message(filters.command("vbv", [".", "/"]))
async def stripe_auth_cmd(Client, message):
    try:
        user_id = message.from_user.id
        gateway = "3DS Lookup"
        approve = "𝗣𝗮𝘀𝘀𝗲𝗱 ✅"

        checkall = await check_all_thing(Client, message)
        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc == False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /vbv

Message: No CC Found in your input ❌

Usage: /vbv cc|month|year|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin = cc[:6]

        if bin.startswith('3'):
            unsupport_resp = f"""<b>
Unsupported card type.</b>"""
            await message.reply_text(unsupport_resp, message.id)
            return

        processing_msg = "Processing your request..."
        processing_reply = await message.reply_text(processing_msg, message.id)

        # Check vbvbin.txt file
        with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
            vbv_data = file.readlines()

        bin_found = False
        for line in vbv_data:
            if line.startswith(bin):
                bin_found = True
                bin_response = line.strip().split('|')[1]
                response_message = line.strip().split('|')[2]
                if "3D TRUE ❌" in bin_response:
                    approve = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
                break

        if not bin_found:
            approve = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
            bin_response = "Not Found"
            response_message = "Lookup Card Error"

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=100)
        getbin = await get_bin_details(cc)
        await session.aclose()

        brand = getbin[0]
        type = getbin[1]
        level = getbin[2]
        bank = getbin[3]
        country = getbin[4]
        flag = getbin[5]
        currency = getbin[6] if len(getbin) > 6 else "N/A"
        bin_code = bin
        proxy_status = "Live"

        finalresp = f"""
{approve}
━━━━━━━━━━━━━━━
[ﾒ] Card ➺ <code>{fullcc}</code>
[ﾒ] Gateway ➺ <i>{gateway}</i>
[ﾒ] Response ➺ ⤿ {response_message} ⤾
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] Bin ➺ {bin_code}
[ﾒ] Info ➺ {brand} - {type} - {level}
[ﾒ] Bank ➺ {bank}
[ﾒ] Country ➺ {country} - {flag} - {currency}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ﾒ] Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
━━━━━━━━━━━━━━━
[ﾒ] T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | P/x ➺ [{proxy_status}]
"""
        await Client.edit_message_text(message.chat.id, processing_reply.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception as e:
        import traceback
        error_text = "".join(traceback.format_exception(None, e, e.__traceback__))
        await message.reply_text(f"<b>⚠️ Error:</b>\n<code>{error_text}</code>")
