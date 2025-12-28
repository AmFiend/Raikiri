import json
import time
import threading
import asyncio
import httpx
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import*
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *
from TOOLS.getbin import *

async def mchkfunc(fullcc, user_id, session):
    retries = 3
    for attempt in range(retries):
        try:
            result = await create_cvv_charge(fullcc, session)
            # Directly use raw result from gateway, no parsing here
            status = result.get("status", "UNKNOWN")
            response = result.get("response", "Card Declined ❌")
            return result, status, response
        except Exception as e:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
                continue
            else:
                return {}, "Declined ❌", "Card Declined ❌"

@Client.on_message(filters.command("mst", [".", "/"]))
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stripe_mass_auth_cmd(Client, message))
    loop.close()

async def stripe_mass_auth_cmd(Client, message):
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
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  Stripe Sk Based 

- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 -{len(ccs)}
- 𝐂𝐡𝐞𝐜𝐤𝐞𝗱 - Checking CC For {first_name}

- 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
"""
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ Stripe Charge [/mstb]

Number Of CC Check : [{len(ccs)}]
</b>\n
"""
        amt = 0
        start = time.perf_counter()
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)

        works = [mchkfunc(i, user_id, session) for i in ccs]

        while works:
            batch = works[:worker_num]
            results = await asyncio.gather(*batch)
            for raw_result, status_text, response_text in results:
                fullcc = ccs[amt]
                amt += 1

                getbin = await get_bin_details(fullcc)
                brand = getbin[0] if len(getbin) > 0 else "Unknown"
                type_ = getbin[1] if len(getbin) > 1 else "Unknown"
                level = getbin[2] if len(getbin) > 2 else "Unknown"
                bank = getbin[3] if len(getbin) > 3 else "Unknown"
                country = getbin[4] if len(getbin) > 4 else "Unknown"
                flag = getbin[5] if len(getbin) > 5 else ""

                proxy_status = "Live ✨"
                gateway = "Stripe Charge Sk"
                bin6 = fullcc[:6]

                finalresp = f"""
{status_text}
━━━━━━━━━━━━━
[ϟ] 𝗖𝗖 - <code>{fullcc}</code>
[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response_text}
[ϟ] 𝗚𝗮𝘁𝗲  - {gateway}
━━━━━━━━━━━━━
[ϟ] B𝗶𝗻 : {bin6}
[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[ϟ] 𝗜𝘀𝘀𝘂𝗿 : {bank}
[ϟ] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
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
[ϟ] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[ϟ] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ϟ] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚━━━━━━「𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊」━━━━━━╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)
        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
