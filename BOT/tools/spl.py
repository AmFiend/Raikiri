from pyrogram import Client, filters
from pyrogram.types import Message
import os

@Client.on_message(filters.command("spl", prefixes=["/", "."]))
async def split_by_count(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❌ Please reply to a .txt file containing CCs.")

    try:
        count_per_file = int(message.text.split()[1])
        if count_per_file <= 0:
            return await message.reply("❌ Number must be greater than 0.")
    except:
        return await message.reply("❌ Usage: /spl 100 to split into files with 100 cards each.")

    msg = await message.reply("⏳ Downloading file...")
    file_path = await message.reply_to_message.download()
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    os.remove(file_path)

    total = len(lines)
    if count_per_file > total:
        return await msg.edit(f"❌ File only has {total} cards, cannot split by {count_per_file}.")

    chunks = [lines[i:i + count_per_file] for i in range(0, total, count_per_file)]
    for i, chunk in enumerate(chunks):
        fname = f"split_{i+1}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(chunk))
        await client.send_document(message.chat.id, fname, caption=f"🧾 File {i+1}/{len(chunks)} - {len(chunk)} cards")
        os.remove(fname)

    await msg.edit(f"✅ Done. Split into {len(chunks)} files of {count_per_file} cards each.")
