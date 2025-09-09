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
<b>📜 Command Menu</b>

Choose a category:
- AUTH
- CHARGE
- TOOLS
- HELPER
"""
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔑 AUTH", callback_data="AUTH"),
                        InlineKeyboardButton("⚡ CHARGE", callback_data="CHARGE")
                    ],
                    [
                        InlineKeyboardButton("🛠 TOOLS", callback_data="TOOLS"),
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
            caption = """
<b>🔑 AUTH COMMANDS</b>

- /auth
- /vbv
- /b3
"""
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # CHARGE
        elif data == "CHARGE":
            caption = """
<b>⚡ CHARGE COMMANDS</b>

- /charge
- /fastcharge
"""
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # TOOLS
        elif data == "TOOLS":
            caption = """
<b>🛠 TOOLS</b>

- /bin
- /ccgen
- /sk
"""
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # HELPER
        elif data == "HELPER":
            caption = """
<b>🤝 HELPER COMMANDS</b>

- /help
- /about
"""
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅ Back", callback_data="cmds")]]
            )

        # BACK TO HOME
        elif data == "home":
            caption = f"""
<b>🌟 Hello <a href="tg://user?id={user.id}">{user.first_name}</a>!</b>

<b>Welcome back to 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑 🚀</b>

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

        # CLOSE
        elif data == "close":
            await cq.message.delete()
            return

        else:
            await cq.answer("❌ Unknown action", show_alert=True)
            return

        # ✅ Update the video caption only
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
        
