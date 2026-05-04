from FUNC.defs import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("buy", [".", "/"]))
async def cmd_buy(client, message):
    try:
        price_list = """<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴘʟᴀɴꜱ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>Starter</b> — Unlimited Credits + Premium Access For 1 Week at <b>$2.50</b>

◈ <b>Silver</b> — Unlimited Credits + Premium Access For 15 Days at <b>$3.50</b>

◈ <b>Gold</b> — Unlimited Credits + Premium Access For 1 Month at <b>$8</b>

◈ <b>Custom Plan</b> — You can buy any custom plan above 1 month...

<i>All plans are available for 7, 15, or 30 days. Once your plan expires, you will need to purchase a new one to continue using our services. All purchases are non-refundable, and you cannot transfer plans to another account.</i>
━━━━━━━━━━━━━━━━━━━━"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✧ ᴋɴᴏᴄᴋ ᴀᴅᴍɪɴ ✧",
                        url="https://t.me/pipin_o",
                    ),
                    InlineKeyboardButton(
                        text="◈ ᴘᴀʏᴍᴇɴᴛ ◈",
                        callback_data="show_payment_methods",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="✧ ᴇxɪᴛ ✧",
                        callback_data="close_message",
                    )
                ]
            ]
        )
        await message.reply_text(price_list, reply_markup=keyboard, disable_web_page_preview=True)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_callback_query(filters.regex("show_payment_methods"))
async def show_payment_methods(client, callback_query):
    try:
        payment_info = """<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴘᴀʏᴍᴇɴᴛ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>BINANCE ID/PAY</b> — <code>550157299</code>

◈ <b>USDT [TRC20]</b> — <code>TJdQfLWo6mCSa2XnvjAV72eTK4qeWNDdRw</code>

<i>After completing the payment, click Knock Admin, then send the transaction screenshot with your Telegram ID.</i>
━━━━━━━━━━━━━━━━━━━━"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◈ ᴘʟᴀɴ ʟɪꜱᴛ ◈",
                        callback_data="show_price_list",
                    ),
                    InlineKeyboardButton(
                        text="✧ ᴋɴᴏᴄᴋ ᴀᴅᴍɪɴ ✧",
                        url="https://t.me/pipin_o",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="✧ ᴇxɪᴛ ✧",
                        callback_data="close_message",
                    )
                ]
            ]
        )
        await callback_query.message.edit_text(payment_info, reply_markup=keyboard)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_callback_query(filters.regex("show_price_list"))
async def show_price_list(client, callback_query):
    try:
        price_list = """<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴘʟᴀɴꜱ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>Starter</b> — Unlimited Credits + Premium Access For 1 Week at <b>$2.50</b>

◈ <b>Silver</b> — Unlimited Credits + Premium Access For 15 Days at <b>$4.50</b>

◈ <b>Gold</b> — Unlimited Credits + Premium Access For 1 Month at <b>$8</b>

<i>All plans are available for 7, 15, or 30 days. Once your plan expires, you will need to purchase a new one to continue using our services. All purchases are non-refundable, and you cannot transfer plans to another account.</i>
━━━━━━━━━━━━━━━━━━━━"""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✧ ᴋɴᴏᴄᴋ ᴀᴅᴍɪɴ ✧",
                        url="https://t.me/pipin_o",
                    ),
                    InlineKeyboardButton(
                        text="◈ ᴘᴀʏᴍᴇɴᴛ ◈",
                        callback_data="show_payment_methods",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="✧ ᴇxɪᴛ ✧",
                        callback_data="close_message",
                    )
                ]
            ]
        )
        await callback_query.message.edit_text(price_list, reply_markup=keyboard)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_callback_query(filters.regex("close_message"))
async def close_message(client, callback_query):
    try:
        await callback_query.message.delete()
        await callback_query.message.reply_text("")

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
