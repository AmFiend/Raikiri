
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.defs import *
from FUNC.usersdb_func import *
from pyrogram.errors import MessageNotModified
from datetime import date

async def safe_edit(client, chat_id, message_id, text, reply_markup=None):
    try:
        await client.edit_message_text(chat_id, message_id, text, reply_markup=reply_markup)
    except MessageNotModified:
        pass

async def animated_edit(client, chat_id, message_id, text, reply_markup=None, delay=0.02):
    current_text = ""
    for char in text:
        current_text += char
        try:
            await client.edit_message_text(chat_id, message_id, current_text, reply_markup=reply_markup)
        except MessageNotModified:
            pass
        await asyncio.sleep(delay)

@Client.on_message(filters.command("cmds", [".", "/"]))
async def cmd_scr(client, message):
    try:
        WELCOME_TEXT = f"""
<b>[ SYSTEM INITIALIZED ]</b>
<b>> USER_ID:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>
<b>> ACCESS_LEVEL:</b> GRANTED

<b>[ SPYDE_CHK MAINFRAME ]</b>
<b>> STATUS:</b> ONLINE
<b>> MODULES:</b> AUTH_GATES | CHARGE_GATES | TOOLS | UTILITIES

<b>[!] SELECT A NODE TO INTERFACE:</b>
        """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH / B3 / VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE PROTOCOLS", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("CYBER TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("SYSTEM HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("TERMINATE CONNECTION", callback_data="close")
            ]
        ]
        edit_msg = await message.reply_text("<b>[ SYSTEM INITIALIZING... ]</b>")
        await animated_edit(
            client,
            message.chat.id,
            edit_msg.id,
            WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS),
            delay=0.01
        )

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_command(client, message):
    try:
        WELCOME_TEXT = f"""
<b>[ SYSTEM INITIALIZED ]</b>
<b>> USER_ID:</b> <a href="tg://user?id={message.chat.id}">GUEST</a>
<b>> ACCESS_LEVEL:</b> GRANTED

<b>[ SPYDE_CHK MAINFRAME ]</b>
<b>> STATUS:</b> ONLINE
<b>> MODULES:</b> AUTH_GATES | CHARGE_GATES | TOOLS | UTILITIES

<b>[!] SELECT A NODE TO INTERFACE:</b>
        """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH / B3 / VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE PROTOCOLS", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("CYBER TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("SYSTEM HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("TERMINATE CONNECTION", callback_data="close")
            ]
        ]
        await animated_edit(client, message.chat.id, message.id, WELCOME_TEXT, InlineKeyboardMarkup(WELCOME_BUTTONS), delay=0.01)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

@Client.on_message(filters.command("start", [".", "/"]))
async def cmd_start(Client, message):
    try:
        # Frames of animation
        frames = [
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [0%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [10%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [25%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [40%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [55%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [70%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [85%]</b>",
            "<b>[ BOOT SEQUENCE INITIATED ]</b>\n<b>> SPYDE_CHK.OS LOADING... [99%]</b>",
            "<b>[ BOOT SEQUENCE COMPLETE ]</b>\n<b>> WELCOME TO SPYDE_CHK NETWORK.</b>",
        ]

        # Send first message
        edit = await message.reply_text(frames[0])
        await asyncio.sleep(0.2)

        # Loop through remaining frames
        for frame in frames[1:]:
            await safe_edit(Client, message.chat.id, edit.id, frame)
            await asyncio.sleep(0.2)

        final_text = f"""
<b>[ SPYDE_CHK NETWORK ]</b>
<b>> STATUS:</b> ONLINE
<b>> USER_ID:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>
<b>> ACCESS_LEVEL:</b> GRANTED

<b>[!] INITIATE PROTOCOL REGISTRATION OR ACCESS COMMAND INTERFACE.</b>
        """

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("REGISTER // NEW USER", callback_data="register"),
                InlineKeyboardButton("COMMANDS // ACCESS LOGS", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("TERMINATE SESSION", callback_data="close")
            ]
        ]

        await animated_edit(
            Client,
            message.chat.id,
            edit.id,
            final_text,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON),
            delay=0.01
        )

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

async def register_user(user_id, username, antispam_time, reg_at):
    info = {
        "id": f"{user_id}",
        "username": f"{username}",
        "user_proxy":f"N/A",
        "dcr": "N/A",
        "dpk": "N/A",
        "dsk": "N/A",
        "amt": "N/A",
        "status": "FREE",
        "plan": f"N/A",
        "expiry": "N/A",
        "credit": "100",
        "antispam_time": f"{antispam_time}",
        "totalkey": "0",
        "reg_at": f"{reg_at}",
    }
    usersdb.insert_one(info)


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("COMMANDS // ACCESS LOGS", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("TERMINATE SESSION", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
[ REGISTRATION PROTOCOL ]
> STATUS: SUCCESSFUL
> USER_ID: {message.from_user.id}
> USERNAME: {message.from_user.first_name}
> ACCESS_LEVEL: FREE TIER
> CREDITS_ALLOCATED: 50 UNITS

[!] BONUS: 50 CREDITS GRANTED FOR INITIAL REGISTRATION.
[!] REFER TO /howcrd FOR CREDIT SYSTEM DETAILS.

[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.
            </b>"""

        else:
            resp = f"""<b>
[ REGISTRATION PROTOCOL ]
> STATUS: ALREADY REGISTERED
> USER_ID: {message.from_user.id}

[!] MESSAGE: USER PROFILE DETECTED. NO FURTHER REGISTRATION REQUIRED.

[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.
            </b>"""

        await animated_edit(
            Client,
            message.chat.id,
            message.id,
            resp,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON),
            delay=0.01
        )

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

async def callback_register(Client, message):
    try:
        user_id = str(message.reply_to_message.from_user.id) if message.reply_to_message else str(message.from_user.id)
        username = str(message.reply_to_message.from_user.username) if message.reply_to_message else str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("COMMANDS // ACCESS LOGS", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("TERMINATE SESSION", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
[ REGISTRATION PROTOCOL ]
> STATUS: SUCCESSFUL
> USER_ID: {user_id}
> USERNAME: {username}
> ACCESS_LEVEL: FREE TIER
> CREDITS_ALLOCATED: 50 UNITS

[!] BONUS: 50 CREDITS GRANTED FOR INITIAL REGISTRATION.
[!] REFER TO /howcrd FOR CREDIT SYSTEM DETAILS.

[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.
            </b>"""

        else:
            resp = f"""<b>
[ REGISTRATION PROTOCOL ]
> STATUS: ALREADY REGISTERED
> USER_ID: {user_id}

[!] MESSAGE: USER PROFILE DETECTED. NO FURTHER REGISTRATION REQUIRED.

[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.
            </b>"""

        await animated_edit(
            Client,
            message.chat.id,
            message.id,
            resp,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON),
            delay=0.01
        )

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    if CallbackQuery.data == "cmds":
        await callback_command(Client, CallbackQuery.message)

    if CallbackQuery.data == "register":
        await callback_register(Client, CallbackQuery.message)

    if CallbackQuery.data == "HOME":
        WELCOME_TEXT = f"""
<b>[ SYSTEM STATUS: ONLINE ]</b>
<b>> USER_ID:</b> <a href="tg://user?id={CallbackQuery.from_user.id}">{CallbackQuery.from_user.first_name}</a>
<b>> ACCESS_LEVEL:</b> GRANTED

<b>[ SPYDE_CHK MAINFRAME ]</b>
<b>> CORE MODULES:</b> AUTH_GATES | CHARGE_GATES | TOOLS | UTILITIES

<b>[!] SELECT A NODE TO INTERFACE:</b>
        """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH / B3 / VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE PROTOCOLS", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("CYBER TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("SYSTEM HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("TERMINATE CONNECTION", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, WELCOME_TEXT, InlineKeyboardMarkup(WELCOME_BUTTONS), delay=0.01)

    if CallbackQuery.data == "close":
        await CallbackQuery.message.delete()
        await CallbackQuery.message.reply_text("<b>[ SESSION TERMINATED ] > ENJOY THE SILENCE.</b>")


    if CallbackQuery.data == "AUTH":
        AUTH_TEXT = f"""
<b>[ AUTHENTICATION GATES ]</b>
<b>> STATUS:</b> ACTIVE

<b>[!] SELECT AUTH PROTOCOL:</b>
> _Secure your access. Choose your weapon._
        """
        AUTH_BUTTONS = [
            [
                InlineKeyboardButton("STRIPE_AUTH", callback_data="Auth2"),
                InlineKeyboardButton("ADYEN_AUTH", callback_data="Adyen2"),
            ],
            [
                InlineKeyboardButton("BRAINTREE_B3", callback_data="BRAINTREEB3"),
                InlineKeyboardButton("BRAINTREE_VBV", callback_data="BRAINTREEVBV"),
            ],
            [
                InlineKeyboardButton("CLOVER_AUTH", callback_data="CLOVERAUTH"),
                InlineKeyboardButton("SQUARE_AUTH", callback_data="SQUAREAUTH"),
            ],
            [
                InlineKeyboardButton("// BACK //", callback_data="HOME"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTONS), delay=0.01)

    if CallbackQuery.data == "Auth2":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: STRIPE_AUTH ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Initiate secure transaction._
> `/str cc|mm|yy|cvv`
> `/mstr cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Unauthorized access will be logged._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "Adyen2":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: ADYEN_AUTH ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Process payment through Adyen network._
> `/ady cc|mm|yy|cvv`
> `/mady cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Data integrity is paramount._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "BRAINTREEB3":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: BRAINTREE_B3 ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Braintree B3 verification sequence._
> `/b3 cc|mm|yy|cvv`
> `/mb3 cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Ensure all parameters are valid._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "BRAINTREEVBV":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: BRAINTREE_VBV ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Braintree VBV security protocol._
> `/vbv cc|mm|yy|cvv`
> `/mvbv cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Strict adherence to protocol required._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "CLOVERAUTH":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: CLOVER_AUTH ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Clover payment gateway initiation._
> `/clv cc|mm|yy|cvv`
> `/mclv cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Monitor transaction logs closely._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "SQUAREAUTH":
        AUTH_TEXT = f"""
<b>[ PROTOCOL: SQUARE_AUTH ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Square payment system integration._
> `/sqr cc|mm|yy|cvv`
> `/msqr cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Verify all input data._
        """
        AUTH_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="AUTH"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, AUTH_TEXT, InlineKeyboardMarkup(AUTH_BUTTON), delay=0.01)

    if CallbackQuery.data == "CHARGE":
        CHARGE_TEXT = f"""
<b>[ CHARGE PROTOCOLS ]</b>
<b>> STATUS:</b> ACTIVE

<b>[!] SELECT CHARGE GATEWAY:</b>
> _Unleash the flow of digital currency._
        """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("SK_BASED", callback_data="SKBASED"),
                InlineKeyboardButton("BRAINTREE_CHARGE", callback_data="BRAINTREE"),
            ],
            [
                InlineKeyboardButton("STRIPE_API", callback_data="SITE"),
                InlineKeyboardButton("SHOPIFY_CHARGE", callback_data="SHOPIFY"),
            ],
            [
                InlineKeyboardButton("AUTHNET_CHARGE", callback_data="AUTHNET"),
                InlineKeyboardButton("PAYPAL_CHARGE", callback_data="PAYPAL"),
            ],
            [
                InlineKeyboardButton("// BACK //", callback_data="HOME"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTONS), delay=0.01)

    if CallbackQuery.data == "PAYPAL":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: PAYPAL ]</b>
<b>> STATUS:</b> <span style='color:red;'>INACTIVE</span>

<b>[ COMMAND SYNTAX ]</b>
> _PayPal integration modules._
> `/pp cc|mm|yy|cvv`
> `/mpp cc|mm|yy|cvv`
> `/py cc|mm|yy|cvv`
> `/mpy cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Module currently offline. Awaiting reactivation._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "SKBASED":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: SK_BASED ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _SK-based charge operations._
> `/svv cc|mm|yy|cvv`
> `/msvv cc|mm|yy|cvv`
> `/svvtxt [in reply to file]`
> `/ccn cc|mm|yy|cvv`
> `/mccn cc|mm|yy|cvv`
> `/ccntxt [in reply to file]`
> `/cvv cc|mm|yy|cvv`
> `/mcvv cc|mm|yy|cvv`
> `/cvvtxt [in reply to file]`

<b>[!] NOTE:</b> _Self SK functionality available via /selfcmd._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "SITE":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: STRIPE_API ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Direct Stripe API charge methods._
> `/sch cc|mm|yy|cvv`
> `/msch cc|mm|yy|cvv`
> `/st1 cc|mm|yy|cvv`
> `/mst1 cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Ensure API keys are valid._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "BRAINTREE":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: BRAINTREE ]</b>
<b>> STATUS:</b> <span style='color:red;'>INACTIVE</span>

<b>[ COMMAND SYNTAX ]</b>
> _Braintree charge operations._
> `/br cc|mm|yy|cvv`
> `/mbr cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Module currently offline. Awaiting reactivation._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "SHOPIFY":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: SHOPIFY ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Shopify e-commerce charge protocols._
> `/sh cc|mm|yy|cvv`
> `/msh cc|mm|yy|cvv`
> `/so cc|mm|yy|cvv`
> `/mso cc|mm|yy|cvv`
> `/sho cc|mm|yy|cvv`
> `/msho cc|mm|yy|cvv`
> `/sg cc|mm|yy|cvv`
> `/msg cc|mm|yy|cvv`

<b>[!] NOTE:</b> _Multiple Shopify gateways available._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "AUTHNET":
        CHARGE_TEXT = """
<b>[ CHARGE PROTOCOL: AUTHNET ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Authorize.Net transaction initiation._
> `/nt cc|mm|yy|cvv`

<b>[!] WARNING:</b> _Single transaction mode._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="CHARGE"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "TOOLS":
        TOOLS_TEXT = f"""
<b>[ CYBER TOOLS ]</b>
<b>> STATUS:</b> ACTIVE

<b>[!] SELECT TOOL MODULE:</b>
> _Sharpen your digital edge._
        """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("DATA_SCRAPPER", callback_data="SCRAPPER"),
                InlineKeyboardButton("SK_UTILITIES", callback_data="SKSTOOL"),
            ],
            [
                InlineKeyboardButton("GENERATOR_MODULES", callback_data="GENARATORTOOLS"),
                InlineKeyboardButton("BIN_ANALYTICS", callback_data="BINANDOTHERS"),
            ],
            [
                InlineKeyboardButton("// BACK //", callback_data="HOME"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, TOOLS_TEXT, InlineKeyboardMarkup(CHARGE_BUTTONS), delay=0.01)

    if CallbackQuery.data == "SKSTOOL":
        CHARGE_TEXT = """
<b>[ TOOL MODULE: SK_UTILITIES ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Stripe Key analysis and generation._
> `/sk sk_live_xxxxxx`
> `/pk sk_live_xxxxxx`
> `/skuser sk_live_xxxxxx`
> `/skinfo sk_live_xxxxxx`

<b>[!] NOTE:</b> _Single-use commands for key validation._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="TOOLS"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "SCRAPPER":
        CHARGE_TEXT = """
<b>[ TOOL MODULE: DATA_SCRAPPER ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Harvesting digital fragments._
> `/scr channel_username 100`
> `/scrbin 440393 channel_username 100`
> `/scrsk channel_username 100`

<b>[!] WARNING:</b> _Scraping limits apply (5K)._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="TOOLS"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "GENARATORTOOLS":
        CHARGE_TEXT = """
<b>[ TOOL MODULE: GENERATOR_MODULES ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Fabricating digital identities._
> `/gen 440393 500`
> `/fake us`

<b>[!] WARNING:</b> _Generation limits apply (10K)._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="TOOLS"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "BINANDOTHERS":
        CHARGE_TEXT = """
<b>[ TOOL MODULE: BIN_ANALYTICS ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Decoding financial identifiers._
> `/bin 440393`
> `/fl [in reply to text]`
> `/massbin 440393`

<b>[ ADDITIONAL UTILITIES ]</b>
> `/ip your_ip`
> `/url website_url`
> `/gpt Promote`

<b>[!] WARNING:</b> _Mass BIN limit (30). Gateway Hunter limit (20). GPT-4 access restricted._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="TOOLS"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)

    if CallbackQuery.data == "HELPER":
        HELPER_TEXT = f"""
<b>[ SYSTEM HELPER ]</b>
<b>> STATUS:</b> ACTIVE

<b>[!] SELECT ASSISTANCE PROTOCOL:</b>
> _Navigating the digital labyrinth._
        """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("INFO_MODULES", callback_data="INFO"),
            ],
            [
                InlineKeyboardButton("// BACK //", callback_data="HOME"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, HELPER_TEXT, InlineKeyboardMarkup(CHARGE_BUTTONS), delay=0.01)

    if CallbackQuery.data == "INFO":
        CHARGE_TEXT = """
<b>[ HELPER PROTOCOL: INFO_MODULES ]</b>
<b>> STATUS:</b> ACTIVE

<b>[ COMMAND SYNTAX ]</b>
> _Accessing system diagnostics and user data._
> `/start`
> `/register`
> `/id`
> `/info`
> `/credits`
> `/howcrd`
> `/howpm`
> `/buy`
> `/howgp`
> `/ping`

<b>[!] NOTE:</b> _Refer to specific commands for detailed information._
        """
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("// BACK //", callback_data="HELPER"),
                InlineKeyboardButton("// TERMINATE //", callback_data="close")
            ]
        ]
        await animated_edit(Client, CallbackQuery.message.chat.id, CallbackQuery.message.id, CHARGE_TEXT, InlineKeyboardMarkup(CHARGE_BUTTON), delay=0.01)
