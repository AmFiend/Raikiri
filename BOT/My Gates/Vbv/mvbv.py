import json
import time
import asyncio
import httpx
from pyrogram import Client, filters
from datetime import timedelta
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

async def check_vbv_bin(fullcc, bin_status):
    """Check a single card against VBV BIN list"""
    try:
        bin_number = fullcc.split('|')[0][:6]
        if bin_number.startswith("3"):
            return "Declined ❌", "Unsupported card type (Amex)"
        elif bin_number in bin_status:
            status = bin_status[bin_number]["status"]
            response = bin_status[bin_number]["response"]
            # Convert status to our unified style
            if "3D TRUE ❌" in status or "Rejected" in status:
                return "Rejected ❌", response
            else:
                return "Passed ✅", response
        else:
            return "Declined ❌", "Lookup Card Error (BIN not found)"
    except Exception as e:
        return "Error", str(e)[:50]

@Client.on_message(filters.command("mvbv", [".", "/"]))
async def stripe_mass_auth_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)

        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getcc_for_mass(message, role)
        if not getcc[0]:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]
        total_cards = len(ccs)
        max_allowed = 25
        if total_cards > max_allowed:
            await message.reply_text(f"✦ ᴍᴀx {max_allowed} ᴄᴄ ᴀʟʟᴏᴡᴇᴅ. ʏᴏᴜ ᴘʀᴏᴠɪᴅᴇᴅ {total_cards} ✦", message.id)
            return

        # Load VBV BIN data
        with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
            vbv_data = file.readlines()

        bin_status = {}
        for cc in ccs:
            bin_num = cc.split('|')[0][:6]
            if bin_num in bin_status:
                continue
            found = False
            for line in vbv_data:
                if line.startswith(bin_num):
                    found = True
                    parts = line.strip().split('|')
                    bin_status[bin_num] = {
                        "status": parts[1],
                        "response": parts[2]
                    }
                    break
            if not found:
                bin_status[bin_num] = {
                    "status": "Error",
                    "response": "Lookup Card Error"
                }

        # Progress variables
        processed = 0
        passed_count = 0
        rejected_count = 0
        start_time = time.perf_counter()
        approved_cards = []   # store details for passed cards
        rejected_summary = [] # store full cc for rejected/error

        # Initial progress message
        progress_text = f"""VBV 3DS Lookup
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Passed ✅: 0
Rejected ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""

        progress_msg = await message.reply(progress_text, quote=True, parse_mode="HTML")

        # Sequential processing (one by one)
        for idx, fullcc in enumerate(ccs, 1):
            processed = idx
            remaining = total_cards - processed

            status, response = await check_vbv_bin(fullcc, bin_status)

            # Get BIN details for display
            cc_num = fullcc.split('|')[0]
            getbin = await get_bin_details(cc_num)
            brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

            if "Passed" in status or "✅" in status:
                passed_count += 1
                response_status = "PASSED ✅"
                approved_cards.append({
                    "fullcc": fullcc,
                    "response": response,
                    "brand": f"{brand} — {type_} — {level}",
                    "bank": bank,
                    "country": country,
                    "flag": flag,
                    "time": time.perf_counter() - start_time
                })
            else:
                rejected_count += 1
                response_status = "REJECTED ❌"
                rejected_summary.append(fullcc)

            # Update progress message
            try:
                await client.edit_message_text(
                    message.chat.id,
                    progress_msg.id,
                    f"""VBV 3DS Lookup
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Passed ✅: {passed_count}
Rejected ❌: {rejected_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""",
                    parse_mode="HTML"
                )
            except:
                pass

            await asyncio.sleep(0.3)  # small delay for smoothness

        # Delete progress message
        await progress_msg.delete()

        elapsed_time = round(time.perf_counter() - start_time, 2)

        # Send each passed card as separate message (full details)
        for card in approved_cards:
            approved_msg = f"""Passed ✅

{SYMBOL} 𝗖𝗮𝗿𝗱 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ 3DS Lookup
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {card['brand']}
{SYMBOL} 𝗕𝗮𝗻ᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(approved_msg, quote=True, parse_mode="HTML")
            await asyncio.sleep(0.5)

        # Send rejected summary
        if rejected_count > 0:
            rejected_summary_text = f"""❌ 𝗥ᴇᴊᴇᴄᴛᴇᴅ / 𝗘ʀʀᴏʀ 𝗖ᴀʀᴅs ({rejected_count})

━━━━━━━━━━━━━━━━━━━━
"""
            # Show first 15 rejected cards
            for card in rejected_summary[:15]:
                rejected_summary_text += f"{SYMBOL} {card} → Rejected\n"
            if rejected_count > 15:
                rejected_summary_text += f"\n... and {rejected_count - 15} more rejected cards"
            rejected_summary_text += f"""
━━━━━━━━━━━━━━━━━━━━
✅ Passed: {passed_count}
❌ Rejected: {rejected_count}
📊 Total: {total_cards}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(rejected_summary_text, quote=True, parse_mode="HTML")
        else:
            # All passed
            await message.reply_text(
                f"""✅ 𝗔𝗹𝗹 𝗖𝗮𝗿𝗱𝘀 𝗣𝗮𝘀𝘀𝗲𝗱

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
✅ All Passed: {passed_count}
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
