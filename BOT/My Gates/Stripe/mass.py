import json
import time
import threading
import asyncio
import httpx
from pyrogram import Client, filters
from datetime import timedelta
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *

async def mchkfunc(fullcc, user_id):
    try:
        proxies = await get_proxy_format()
        session = httpx.AsyncClient(timeout=30)
        result = await create_cvv_charge(fullcc, session)
        getresp = await get_charge_resp(result, user_id, fullcc)
        response = getresp["response"]
        status = getresp["status"]
        await session.aclose()
        return f"[玄] 𝘾𝘾 -» <code>{fullcc}</code>\n[玄] 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status}\n[玄] 𝙍𝙚𝙨𝙪𝙡𝙩 -» {response}\n\n"

    except:
        import traceback
        await error_log(traceback.format_exc())
        return f"<code>{fullcc}</code>\n[玄] 𝙍𝙚𝙨𝙪𝙡𝙩 -» Declined ✗\n"

@Client.on_message(filters.command("mass", [".", "/"]))
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
        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if getcc[0] == False:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]
        resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴀʀɢᴇ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

[玄] 𝙂𝙖𝙩𝙚 -» ꜱᴛʀɪᴘᴇ ᴀᴜᴛʜ
[玄] 𝘾𝘾 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}
[玄] 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 -» {first_name}
[玄] 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...
━━━━━━━━━━━━━━━━━━━━"""
        nov = await message.reply_text(resp, message.id)

        text = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴀᴜᴛʜ</b> ✧
━━━━━━━━━━━━━━━━━━━━
"""
        amt = 0
        start = time.perf_counter()
        works = [mchkfunc(i, user_id) for i in ccs]
        worker_num = int(json.loads(
            open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])

        while works:
            a = works[:worker_num]
            a = await asyncio.gather(*a)
            for i in a:
                amt += 1
                text += i
                if amt % 5 == 0:
                    try:
                        await Client.edit_message_text(message.chat.id, nov.id, text)
                    except:
                        pass
            await asyncio.sleep(1)
            works = works[worker_num:]

        taken = str(timedelta(seconds=time.perf_counter() - start))
        hours, minutes, seconds = map(float, taken.split(":"))
        hour = int(hours)
        min = int(minutes)
        sec = int(seconds)

        text += f"""━━━━━━━━━━━━━━━━━━━━
[玄] 𝙏𝙞𝙢𝙚 -» {time.perf_counter() - start:0.2f}s
[玄] 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮 -» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ↯ {role}
[玄] 𝙊𝙬𝙣𝙚𝙧 -» @pipin_o
━━━━━━━━━━━━━━━━━━━━"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except:
        import traceback
        await error_log(traceback.format_exc())
