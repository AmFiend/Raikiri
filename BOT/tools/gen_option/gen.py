import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.cc_gen import luhn_card_genarator, get_bin_info

import re

buttons = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚-𝙂𝙚𝙣 🔄", callback_data="regen")],
        [InlineKeyboardButton("𝙀𝙭𝙞𝙩 ⚠", callback_data="exit")],
    ]
)

def generate_code_blocks(all_cards):
    return "\n".join([f"<code>{c}</code>" for c in all_cards.splitlines()])


@Client.on_message(filters.command("gen", [".", "/"]))
async def gen_cmd(client, message):
    try:
        ccsdata = message.text.split()[1]
        cc_parts = ccsdata.split("|")
        cc = cc_parts[0]
        mes = cc_parts[1] if len(cc_parts) > 1 else "rnd"
        ano = cc_parts[2] if len(cc_parts) > 2 else "rnd"
        cvv = cc_parts[3] if len(cc_parts) > 3 else "rnd"
    except IndexError:
        return await message.reply_text(
            "Wrong Format ❌\nUsage: /gen 515462xxxx|11|2030|000"
        )

    await message.reply_text("Generating...", quote=True)
    
    all_cards = await luhn_card_genarator(cc, mes, ano, cvv, 10)
    brand, type_, level, bank, country, flag, currency = await get_bin_info(cc[:6])
    code_blocks = generate_code_blocks(all_cards)

    response_text = (
        f"- 𝐂𝐂 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲\n"
        f"- 𝐁𝐢𝐧 - <code>{cc}</code>\n"
        f"{code_blocks}"
        f"- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}\n"
        f"- 𝐁𝐚𝐧𝐤 - {bank} 🏛\n"
        f"- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag}\n"
    )

    await message.reply_text(response_text, parse_mode="HTML", reply_markup=buttons)


@Client.on_callback_query(filters.regex("regen"))
async def regen_call(client, callback_query):
    text_bk = callback_query.message.text
    bin_search = re.search(r"𝘽𝙞𝙣 -» <code>(\d+)", text_bk)
    bin_number = bin_search.group(1) if bin_search else "401658"

    all_cards = await luhn_card_genarator(bin_number, "rnd", "rnd", "rnd", 10)
    brand, type_, level, bank, country, flag, currency = await get_bin_info(bin_number)
    code_blocks = generate_code_blocks(all_cards)

    response_text = (
        f"- 𝐂𝐂 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲\n"
        f"- 𝐁𝐢𝐧 - <code>{bin_number}</code>\n"
        f"{code_blocks}"
        f"- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}\n"
        f"- 𝐁𝐚𝐧𝐤 - {bank} 🏛\n"
        f"- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag}\n"
    )

    await callback_query.edit_message_text(response_text, parse_mode="HTML", reply_markup=buttons)
        
