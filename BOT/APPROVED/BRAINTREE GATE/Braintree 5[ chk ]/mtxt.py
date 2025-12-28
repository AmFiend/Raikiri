import json
import time
import threading
import asyncio
import httpx
import re
from pyrogram import Client, filters
from datetime import timedelta
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import get_charge_resp
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *
from TOOLS.getbin import *

async def mchkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            proxies = await get_proxy_format()
            session = httpx.AsyncClient(timeout=30, proxies=proxies, follow_redirects=True)

            payflow = PayflowAuth()
            raw_result, _ = payflow.main(fullcc)  # blocking synchronous call

            if isinstance(raw_result, list) and len(raw_result) > 0:
                raw_resp_str = raw_result[0]
            else:
                raw_resp_str = raw_result if isinstance(raw_result, str) else str(raw_result)

            getresp = await get_charge_resp(raw_resp_str, user_id, fullcc)

            print(f"[DEBUG mchkfunc] Card {fullcc} response: {getresp}")

            status = getresp.get("status", "Declined ❌")
            response = getresp.get("response", "Invalid response format")

            await session.aclose()

            return f"Card↯ <code>{fullcc}</code>\n<b>Status - {status}</b>\n<b>Result -⤿ {response} ⤾</b>\n\n"

        except Exception:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
            else:
                return f"<code>{fullcc}</code>\n<b>Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("mptxt", [".", "/"]))
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(payflow_mass_auth_cmd(Client, message))
    loop.close()

# No changes needed for imports, mchkfunc, multi, or bcall functions.
# They will work as-is.

# --- START OF MODIFIED FUNCTION ---
async def payflow_mass_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)

        # --- NEW LOGIC: Check if the command is a reply to a document ---
        if not message.reply_to_message or not message.reply_to_message.document:
            await message.reply_text(
                "❌ **Invalid Usage**\n\n"
                "Reply to a `.txt` file containing credit cards with the `/mptxt` command.\n"
                "Example:\n`/mpy` (as a reply to your cards.txt file)",
                quote=True
            )
            return

        # --- NEW LOGIC: Validate the file ---
        document = message.reply_to_message.document
        if not document.file_name.lower().endswith('.txt'):
            await message.reply_text("❌ The file must be a `.txt` file.", quote=True)
            return

        # --- MODIFIED LOGIC: Download and read CCs from the file ---
        await message.reply_text("📥 Downloading and processing file...", quote=True)
        
        # Download the file to a temporary location
        file_path = await Client.download_media(document, in_memory=True)
        
        # Decode and process the file content
        try:
            file_content = file_path.getvalue().decode('utf-8').splitlines()
        except UnicodeDecodeError:
            await message.reply_text("❌ Failed to read the file. Please ensure it's a UTF-8 encoded text file.", quote=True)
            return
        finally:
            # Clean up the in-memory file object
            file_path.close()

        # Filter out empty lines and strip whitespace
        ccs = [line.strip() for line in file_content if line.strip()]

        if not ccs:
            await message.reply_text("❌ No valid credit cards found in the file.", quote=True)
            return

        # --- NEW LOGIC: Limit the number of cards to 100 ---
        if len(ccs) > 100:
            ccs = ccs[:100]  # Take only the first 100 cards
            await message.reply_text(
                f"⚠️ **Limit Reached**: The file contains more than 100 cards. Only the first 100 will be checked.",
                quote=True
            )

        # --- The rest of the function remains largely the same ---
        checkall = await check_all_thing(Client, message)
        if checkall[0] == False:
            return
        
        role = checkall[1]

        resp = f"""
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - Payflow charged 
- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - Checking CC For {first_name}
- 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
"""
        nov = await message.reply_text(resp, quote=True)
        text = f"""
<b>↯ Payflow [/mptxt] Number Of CC Check : [{len(ccs)}] </b>\n
"""
        amt = 0
        start = time.perf_counter()
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])
        
        # We create a new list of tasks from the 'ccs' we just read from the file
        works = [mchkfunc(i, user_id) for i in ccs]
        
        while works:
            batch = works[:worker_num]
            results = await asyncio.gather(*batch)
            for result_text in results:
                # Ensure amt doesn't go out of bounds if ccs were sliced
                if amt >= len(ccs):
                    continue
                
                fullcc = ccs[amt]
                amt += 1
                getbin = await get_bin_details(fullcc)
                brand = getbin[0] if len(getbin) > 0 else "Unknown"
                type_ = getbin[1] if len(getbin) > 1 else "Unknown"
                level = getbin[2] if len(getbin) > 2 else "Unknown"
                bank = getbin[3] if len(getbin) > 3 else "Unknown"
                country = getbin[4] if len(getbin) > 4 else "Unknown"
                flag = getbin[5] if len(getbin) > 5 else ""
                currency = getbin[6] if len(getbin) > 6 else "Unknown"
                proxy_status = "Live ✨"
                gateway = "Payflow"
                bin6 = fullcc[:6]
                
                status_match = re.search(r"Status - ([^^\n<]+)", result_text)
                response_match = re.search(r"Result -⤿ (.+?) ⤾", result_text)
                status_text = status_match.group(1) if status_match else "UNKNOWN"
                response_text = response_match.group(1).strip() if response_match else "UNKNOWN"
                
                finalresp = f"""
{status_text}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {status_text}
[⟐] 𝗥𝗲𝘀𝘂𝗹𝘁 : {response_text}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
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
            works = works[worker_num:]
            await asyncio.sleep(0.5)

        text += f"""
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═══════⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊 」⟐═══════╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)
        
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- END OF MODIFIED FUNCTION ---
