import time
import asyncio
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import check_card, PROXY
from .response import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *

MAX_CARDS_LIMIT = 5

async def msp_chkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            result = await asyncio.to_thread(check_card, fullcc, "default", PROXY)
            parsed = await get_charge_resp(result, user_id, fullcc)
            status = parsed.get("status", "UNKNOWN")
            response = parsed.get("response", "UNKNOWN")
            return f"Card↯ <code>{fullcc}</code>\n<b>Status - {status}</b>\n<b>Result -⤿ {response} ⤾</b>\n\n"
        except Exception:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
            else:
                return f"<code>{fullcc}</code>\n<b>Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("msp", [".", "/"]) & filters.document)
async def msp_mass_check(Client, message):
    user_id = str(message.from_user.id)
    first_name = str(message.from_user.first_name)
    checkall = await check_all_thing(Client, message)
    if not checkall[0]:
        return
    role = checkall[1]

    if not message.document.file_name.endswith('.txt'):
        await message.reply("❌ Please send a TXT file with card data")
        return

    try:
        file_path = await Client.download_media(message)
    except Exception as e:
        await message.reply(f"❌ Failed to download file: {str(e)}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        ccs = [line.strip() for line in f if line.strip()]

    if len(ccs) > MAX_CARDS_LIMIT:
        await message.reply(f"⚠️ You sent {len(ccs)} cards but only the first {MAX_CARDS_LIMIT} will be processed.\n"
                            "To check more cards, please buy premium access.")
        ccs = ccs[:MAX_CARDS_LIMIT]

    resp = f"""
- Gateway -  Auto Shopify

- CC Amount - {len(ccs)}
- Checked - Checking CC For {first_name}

- Status - Processing...⌛️
    """
    nov = await message.reply(resp)

    text = f"""
<b>↯ Auto Shopify 💎 [/msp]

Number Of CC Check : [{len(ccs)}]
</b>\n
"""
    amt = 0
    start = time.perf_counter()
    worker_num = 5

    works = [msp_chkfunc(i, user_id) for i in ccs]

    while works:
        batch = works[:worker_num]
        results = await asyncio.gather(*batch)
        for result_text in results:
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
            gateway = "Auto Shopify 💎"
            bin6 = fullcc[:6]

            status_match = re.search(r"Status - ([^\n<]+)", result_text)
            response_match = re.search(r"Result -⤿ ([^\n<]+)", result_text)
            status_text = status_match.group(1) if status_match else "UNKNOWN"
            response_text = response_match.group(1) if response_match else "UNKNOWN"

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
        works = works[worker_num:]
        await asyncio.sleep(0.5)

    text += f"""
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=6622603977">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═══════⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊  」⟐═══════╝
"""
    await Client.edit_message_text(message.chat.id, nov.id, text)
