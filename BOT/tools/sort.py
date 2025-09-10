import re
import io
import os
from pyrogram import Client, filters

# Validate credit card using Luhn algorithm
def is_valid_luhn(card_number):
    digits = [int(d) for d in card_number[::-1]]
    return sum(d if i % 2 == 0 else sum(divmod(d * 2, 10)) for i, d in enumerate(digits)) % 10 == 0

# Smart card extractor
def extract_cards(text):
    lines = text.splitlines()
    cards = []
    temp = {}

    for line in lines:
        clean = line.strip().lower()

        # Match full CC|MM|YY|CVV with separators
        match = re.findall(r'(\d{13,16})\D+(\d{1,2})\D+(\d{2,4})\D+(\d{3,4})', clean)
        if match:
            for cc, mm, yy, cvv in match:
                if is_valid_luhn(cc):
                    cards.append(f"{cc}|{mm.zfill(2)}|{yy[-2:]}|{cvv}")
            continue

        # Match labeled one-line
        labeled = re.search(r'nr[^\d]*(\d{13,16}).*exp[^\d]*(\d{1,2})[\/\-](\d{2,4}).*cvv[^\d]*(\d{3,4})', clean)
        if labeled:
            cc, mm, yy, cvv = labeled.groups()
            if is_valid_luhn(cc):
                cards.append(f"{cc}|{mm.zfill(2)}|{yy[-2:]}|{cvv}")
            continue

        # Field-by-field build
        if 'nr' in clean or 'card' in clean or 'number' in clean:
            cc = re.findall(r'\d{13,16}', clean)
            if cc and is_valid_luhn(cc[0]):
                temp['cc'] = cc[0]
        elif 'exp' in clean or 'expire' in clean or 'valid' in clean:
            exp = re.findall(r'(\d{1,2})[\/\-](\d{2,4})', clean)
            if exp:
                temp['mm'], temp['yy'] = exp[0]
        elif 'cvv' in clean or 'cvc' in clean or 'sec' in clean or 'code' in clean:
            cvv = re.findall(r'\d{3,4}', clean)
            if cvv:
                temp['cvv'] = cvv[0]

        # If full set is ready
        if all(k in temp for k in ['cc', 'mm', 'yy', 'cvv']):
            cards.append(f"{temp['cc']}|{temp['mm'].zfill(2)}|{temp['yy'][-2:]}|{temp['cvv']}")
            temp = {}

    return sorted(set(cards))

# Pyrogram /sort command
@Client.on_message(filters.command("sort", [".", "/"]))
async def smart_sort(client, message):
    try:
        input_text = None

        if message.reply_to_message:
            if message.reply_to_message.document:
                file = await message.reply_to_message.download()
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    input_text = f.read()
                os.remove(file)
            else:
                input_text = message.reply_to_message.text
        else:
            input_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""

        if not input_text:
            return await message.reply("❌ No input found.")

        cards = extract_cards(input_text)

        if cards:
            result = "\n".join(cards)
            if len(cards) >= 32:
                file = io.BytesIO(result.encode())
                file.name = "sorted_cards.txt"
                await message.reply_document(file, caption=f"✅ Extracted {len(cards)} cards.")
            else:
                await message.reply_text(f"<code>{result}</code>", quote=True)
        else:
            await message.reply("❌ No valid cards found in input.")

    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{str(e)}</code>")
