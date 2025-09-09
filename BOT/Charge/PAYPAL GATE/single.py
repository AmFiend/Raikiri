import httpx
import re
import time
import asyncio
import random
import string
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import *
from .gate import create_paypal_charge
from faker import Faker


@Client.on_message(filters.command("", [".", "/"]))
async def paypal_check_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)

        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if not getcc:
            await message.reply_text(
                "<b>Gate Name: PayPal Auth ✅\nCMD: /pp\n\nMessage: No CC Found in your input ❌\nUsage: /pp cc|mes|ano|cvv</b>"
            )
            return

        cc, mes, ano, cvv = getcc
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = "PayPal [1$]✅"

        # Progress messages
        progress_msg = await message.reply_text(
            f"""↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□"""
        )
        await asyncio.sleep(0.5)
        await progress_msg.edit_text(
            f"""↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□"""
        )
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)

        result = await create_paypal_charge(fullcc, session)
        bin_data = await get_bin_details(cc)
        getresp = await get_charge_resp(result, user_id, fullcc)
        status = getresp["status"]
        response = getresp["response"]

        # Third progress
        await progress_msg.edit_text(
            f"""↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■"""
        )
        await asyncio.sleep(0.5)

        brand, type_, level, bank, country, flag, currency = bin_data
        proxy_status = result.get("proxy", "N/A") if isinstance(result, dict) else "N/A"

        finalresp = f"""
{status}
━━━━━━━━━━━━━
[ϟ] 𝗖𝗖 - <code>{fullcc}</code>
[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response}
[ϟ] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[ϟ] 𝗕𝗶𝗻 : {brand}
[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[ϟ] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[ϟ] 𝗧𝘆𝗽𝗲 : {type_}
━━━━━━━━━━━━━
[ϟ] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[ϟ] 𝗖𝗵𝗲𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ϟ] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝
"""
        await progress_msg.edit_text(finalresp)

        if status.strip().lower() in ["approved ✅", "𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"]:
            await sendcc(finalresp, session)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        await message.reply_text("❌ An unexpected error occurred.\nCheck logs.")
        await error_log(tb)
    finally:
        try:
            await session.aclose()
        except:
            pass
