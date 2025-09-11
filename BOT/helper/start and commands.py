import asyncio
import traceback
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode


# /start command
@Client.on_message(filters.command("start", [".", "/"]))
async def cmd_start(client, message):
    try:
        caption = f"""
<b>🌟 Hello <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b>

<b>Welcome aboard the 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑 🚀</b>

<b>I’m your go-to bot packed with tools, gates, and commands.</b>

<b>👇 Tap <i>Register</i> or <i>Commands</i> to explore.</b>
"""

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📌 Register", callback_data="register"),
                    InlineKeyboardButton("⚙ Commands", callback_data="cmds")
                ],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]
        )

        # Send video with welcome caption + buttons
        await message.reply_video(
            "menu.mp4",
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=buttons
        )

    except FileNotFoundError:
        await message.reply_text("⚠️ menu.mp4 file not found! Please upload it to the bot’s folder.")

    except Exception:
        await message.reply_text(
            f"⚠️ Error:\n<code>{traceback.format_exc()}</code>",
            parse_mode=ParseMode.HTML
        )


# Callback query handler
@Client.on_callback_query()
async def callback_handler(client, cq):
    user = cq.from_user
    data = cq.data

    try:
        # Default caption + buttons
        caption = ""
        buttons = InlineKeyboardMarkup([])

        # REGISTER
        if data == "register":
            caption = f"""
<b>✅ Registration Successful!</b>

👤 Name: {user.first_name}  
🆔 ID: {user.id}  
🎟 Role: Free  
💳 Credits: 50  
"""
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("⚙ Commands", callback_data="cmds")],
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="home"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )

        # COMMANDS MENU
        elif data == "cmds":
            caption = """
𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝘾𝙝𝙖𝙧𝙜𝙚 𝙈𝙖𝙨𝙩𝙚𝙧 -» >_

𝙏𝙤𝙩𝙖𝙡 -» <code>18</code>
𝙊𝙣 -» <code>12 ✅</code>
𝙊𝙛𝙛 -» <code>4 ❌</code>
𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» <code>2 ⚠️</code>

<code>𝙎𝙚𝙡𝙚𝙘𝙩 𝙩𝙝𝙚 𝙩𝙮𝙥𝙚 𝙤𝙛 𝙜𝙖𝙩𝙚 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙛𝙤𝙧 𝙮𝙤𝙪𝙧 𝙪𝙨𝙚!</code>
"""
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝘼𝙪𝙩𝙝", callback_data="AUTH"),
                        InlineKeyboardButton("𝘾𝙝𝙖𝙧𝙜𝙚𝙙", callback_data="CHARGE")
                    ],
                    [
                        InlineKeyboardButton("𝙏𝙤𝙤𝙡𝙨 🛠", callback_data="TOOLS"),
                        InlineKeyboardButton("🤝 HELPER", callback_data="HELPER")
                    ],
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="home"),
                        InlineKeyboardButton("❌ Close", callback_data="close")
                    ]
                ]
            )

        # AUTH
        elif data == "AUTH":
            caption = """ ... """  # keep your AUTH text
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # CHARGE
        elif data == "CHARGE":
            caption = """ ... """  # keep your CHARGE text
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # TOOLS (Page 1)
        elif data == "TOOLS":
            caption = """ ... """  # keep your TOOLS text
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("➡ Next", callback_data="TOOLS_PAGE2")],
                    [InlineKeyboardButton("⬅ Back", callback_data="cmds")]
                ]
            )

        # TOOLS (Page 2)
        elif data == "TOOLS_PAGE2":
            caption = """ ... """  # keep your TOOLS_PAGE2 text
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("⬅ Previous", callback_data="TOOLS")],
                    [InlineKeyboardButton("⬅ Back", callback_data="cmds")]
                ]
            )

        # HELPER (Page 1)
        elif data == "HELPER":
            caption = """ ... """  # keep your HELPER text
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("➡ Next", callback_data="HELPER_PAGE2")],
                    [InlineKeyboardButton("⬅ Back", callback_data="cmds")]
                ]
            )

        # HELPER (Page 2)
        elif data == "HELPER_PAGE2":
            caption = """ ... """  # keep your HELPER_PAGE2 text
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("⬅ Previous", callback_data="HELPER")],
                    [InlineKeyboardButton("⬅ Back", callback_data="cmds")]
                ]
            )

        # BACK TO HOME
        elif data == "home":
            caption = f""" ... """  # keep your HOME text
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📌 Register", callback_data="register"),
                        InlineKeyboardButton("⚙ Commands", callback_data="cmds")
                    ],
                    [InlineKeyboardButton("❌ Close", callback_data="close")]
                ]
            )

        # CLOSE
        elif data == "close":
            await cq.message.delete()
            return

        else:
            await cq.answer("❌ Unknown action", show_alert=True)
            return

        # ✅ Update the video caption only if it has changed
        if cq.message.caption != caption:
            await cq.message.edit_caption(
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=buttons
            )

    except Exception:
        await cq.message.reply_text(
            f"⚠️ Error:\n<code>{traceback.format_exc()}</code>",
            parse_mode=ParseMode.HTML
        )
        
