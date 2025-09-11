import httpx
import os
import threading
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.usersdb_func import *
from FUNC.cc_gen import *
from TOOLS.check_all_func import *

# Regen button
buttons = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔄 Regen", callback_data="regen")]]
)

# Helper to format cards
def generate_code_blocks(all_cards):
    code_blocks = ""
    cards = all_cards.split('\n')
    for card in cards:
        code_blocks += f"<code>{card}</code>\n"
    return code_blocks

# Command handler with threading
@Client.on_message(filters.command("gen", [".", "/"]))
def multi(client, message):
    t1 = threading.Thread(target=bcall, args=(client, message))
    t1.start()

def bcall(client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gen_cmd(client, message))
    loop.close()

# Main generation function
async def gen_cmd(client, message, edit_msg=None, from_regen=False):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        # Parse BIN and optional Exp/CVV
        if not from_regen:
            try:
                ccsdata = message.text.split()[1]
                cc_parts = ccsdata.split("|")
                cc = cc_parts[0]
                mes = cc_parts[1] if len(cc_parts) > 1 else None
                ano = cc_parts[2] if len(cc_parts) > 2 else None
                cvv = cc_parts[3] if len(cc_parts) > 3 else None
            except IndexError:
                await message.reply_text(
                    """Wrong Format ❌

Usage:
Only Bin
/gen 447697

With Expiration
/gen 447697|12
/gen 447697|12|23

With CVV
/gen 447697|12|23|000

With Custom Amount
/gen 546775 100
"""
                )
                return
            try:
                amount = int(message.text.split()[2])
            except (IndexError, ValueError):
                amount = 10
        else:
            # Regen: get BIN from message text
            orig_text = message.text
            try:
                first_line = orig_text.split("\n")[1]
                cc = first_line.split("<code>")[1].split("</code>")[0]
            except Exception:
                cc = "400000"
            mes, ano, cvv = None, None, None
            amount = 10

        delete = await message.reply_text("<b>Generating...</b>")
        start = time.perf_counter()

        getbin = await get_bin_details(cc[:6])
        if not getbin:
            await delete.delete()
            return
        brand, type_, level, bank, country, flag, currency = getbin

        # Generate cards
        all_cards = await luhn_card_genarator(cc, mes, ano, cvv, amount)
        if not all_cards:
            await delete.delete()
            return

        # Smooth display for small amounts
        if amount <= 10:
            msg_text = (
                f"- 𝐂𝐂 𝐆𝐞𝐧𝐚𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲\n"
                f"- 𝐁𝐢𝐧 - <code>{cc}</code>\n"
                f"- 𝐀𝐦𝐨𝐮𝐧𝐭 - {amount}\n\n"
            )
            if edit_msg:
                msg = edit_msg
                await msg.edit_text(msg_text + "<b>Generating cards...</b>", reply_markup=buttons)
            else:
                msg = await message.reply_text(msg_text + "<b>Generating cards...</b>", reply_markup=buttons)

            # Fast smooth effect: all cards appear in ~1 second
            cards_text = "\n".join([f"<code>{card}</code>" for card in all_cards.split("\n")])
            smooth_text = msg_text + cards_text + "\n<b>Done!</b>"
            await asyncio.sleep(0.05)
            await msg.edit_text(smooth_text, reply_markup=buttons)

            # Append BIN info
            final_text = smooth_text + (
                f"- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}\n"
                f"- 𝐁𝐚𝐧𝐤 - {bank} 🏛\n"
                f"- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag}\n\n"
                f"- 𝐓𝐢𝐦𝐞: - {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n"
                f"- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]"
            )
            await msg.edit_text(final_text, reply_markup=buttons)

        else:
            # File output for larger amounts
            filename = f"downloads/{amount}x_CC_Generated_By_{user_id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(all_cards)

            caption = f"""
- 𝐁𝐢𝐧: <code>{cc}</code> 
- 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}

- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}
- 𝐁𝐚𝐧𝐤 - {bank} 🏛  
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag} - {currency}

- 𝐓𝐢𝐦𝐞 - {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - <a href="tg://user?id={message.from_user.id}"> {message.from_user.first_name}</a> ⤿ {role} ⤾
"""
            if edit_msg:
                await edit_msg.delete()
            else:
                await client.delete_messages(message.chat.id, delete.id)
            await message.reply_document(document=filename, caption=caption, reply_markup=buttons)
            os.remove(filename)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# Regen button handler
@Client.on_callback_query(filters.regex("regen"))
async def regen_handler(client, cq):
    # Always generate fresh random cards using the original BIN
    await gen_cmd(client, cq.message, edit_msg=cq.message, from_regen=True)
    
