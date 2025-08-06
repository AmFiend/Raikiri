import json
from pyrogram import Client, filters
from FUNC.defs import *
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *
from FUNC.scraperfunc import *


with open("FILES/config.json", "r",encoding="utf-8") as f:
    DATA     = json.load(f)
    API_ID   = DATA["API_ID"]
    API_HASH = DATA["API_HASH"]

user = Client("Scrapper",
              api_id   = API_ID,
              api_hash = API_HASH )



@Client.on_message(filters.command("scr", [".", "/"]))
async def scrapper_cc(Client, message):
    try:
        checkall = await check_all_thing(Client , message)
        if checkall[0] == False:
            return

        role = checkall[1]
        try:
            channel_link = message.text.split(" ")[1]
            limit        = int(message.text.split(" ")[2])
        except:
            resp = f"""<b>
𝗪𝗿𝗼𝗻𝗴 𝗙𝗼𝗿𝗺𝗮𝘁 ❌

𝗨𝘀𝗮𝗴𝗲:
𝗙𝗼𝗿 𝗣𝘂𝗯𝗹𝗶𝗰 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr username 50</code>

𝗙𝗼𝗿 𝗣𝗿𝗶𝘃𝗮𝘁𝗲 𝗚𝗿𝗼𝘂𝗽 𝗦𝗰𝗿𝗮𝗽𝗽𝗶𝗻𝗴
<code>/scr https://t.me/+aGWRGz 50</code>
        """
      await message.reply_text(resp, message.id)
    else:
      #
      user_id = str(message.from_user.id)
      chat_type = str(message.chat.type)
      chat_id = str(message.chat.id)
      #PLAN CHECK

      regdata = fetchinfo(user_id)
      results = str(regdata)
      if results == 'None':
        resp = "𝗬𝗢𝗨 𝗔𝗥𝗘 𝗡𝗢𝗧 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗 𝗬𝗘𝗧 ⚠️. 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗙𝗜𝗥𝗦𝗧 𝗕𝗬 𝗨𝗦𝗜𝗡𝗚 /register 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘."
        await message.reply_text(resp, message.id)
      else:
        #HERE
        #PM AND AUTH CHECK
        pm = fetchinfo(user_id)
        status = pm[2]
        role = status
        GROUP = open("plugins/group.txt").read().splitlines()
        if chat_type == "ChatType.PRIVATE" and status == "FREE":
          resp = "𝗢𝗡𝗟𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗠𝗕𝗘𝗥𝗦 𝗔𝗥𝗘 𝗔𝗟𝗟𝗢𝗪𝗘𝗗 𝗧𝗢 𝗨𝗦𝗘 𝗕𝗢𝗧 𝗜𝗡 𝗣𝗘𝗥𝗦𝗢𝗡𝗔𝗟 ⚠️.𝗬𝗢𝗨 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗙𝗥𝗘𝗘𝗟𝗬 𝗕𝗢𝗧 𝗛𝗘𝗥𝗘 @livechargeapproved"
          await message.reply_text(resp, message.id)

        elif chat_type == "ChatType.GROUP" or chat_type == "ChatType.SUPERGROUP" and chat_id not in GROUP:
          resp = "𝗨𝗡𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗖𝗛𝗔𝗧 ❌. 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 @Nairobiangoon 𝗧𝗢 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘."
          await message.reply_text(resp, message.id)
        else:
          #CREDIT CHECK
          chk_credit = fetchinfo(user_id)
          credit = int(chk_credit[5])
          if credit < 3:
            resp = "𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗖𝗥𝗘𝗗𝗜𝗧 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ⚠️ . 𝗥𝗘𝗖𝗛𝗔𝗥𝗚𝗘 𝗖𝗥𝗘𝗗𝗜𝗧 𝗨𝗦𝗜𝗡𝗚 /buy 𝗢𝗥 𝗪𝗔𝗜𝗧 𝗙𝗢𝗥 𝗙𝗥𝗘𝗘 𝗖𝗥𝗘𝗗𝗜𝗧 𝗨𝗦𝗜𝗡𝗚 𝗚𝗜𝗙𝗧𝗖𝗢𝗗𝗘 ."
            await message.reply_text(resp, message.id)
          else:
            #ANTISPAM MODULE
            user_id = str(message.from_user.id)
            results = fetchinfo(user_id)
            status = results[2]
            try:
              limit = int(splitter[1])
            except:
              limit = 100
            if status == 'FREE' and limit > 5000:

              resp = f"""
𝗙𝗥𝗘𝗘 𝗨𝗦𝗘𝗥 𝗔𝗥𝗘 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗧𝗢 5000 𝗦𝗖𝗥𝗔𝗣𝗜𝗡𝗚 𝗟𝗜𝗠𝗜𝗧 ❌
                """
              await message.reply_text(resp, message.id)
            elif status == 'PREMIUM' and limit > 60000:

              resp = f"""
𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥 𝗔𝗥𝗘 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗧𝗢 𝟲𝟬𝟬𝟬0 𝗦𝗖𝗥𝗔𝗣𝗜𝗡𝗚 𝗟𝗜𝗠𝗜𝗧 ❌
                """
              await message.reply_text(resp, message.id)

            else:
              delete = await message.reply_text("𝗦𝗰𝗿𝗮𝗽𝗶𝗻𝗴 𝗪𝗮𝗶𝘁...", message.id)
              channel_link = splitter[0]
              if "https" in channel_link:
                try:
                  join = await user.join_chat(channel_link)
                  title = join.title
                  channel_id = join.id
                  amt_cc = 0
                  dublicate = 0
                  async for msg in user.get_chat_history(channel_id, limit):
                    all_history = str(msg.text)
                    if all_history == 'None':
                      all_history = "INVALID CC NUMBER BC"
                    else:
                      all_history = all_history
                    all_cards = all_history.split('\n')
                    cards = []
                    for x in all_cards:
                      car = getcards(x)
                      if car:
                        cards.append(car)
                      else:
                        continue
                    len_cards = len(cards)
                    if not len_cards:
                      resp = "𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗 𝗔𝗡𝗬 𝗩𝗔𝗟𝗜𝗗 𝗖𝗔𝗥𝗗"
                    for item in cards:
                      amt_cc += 1
                      cc = item[0]
                      mes = item[1]
                      ano = item[2]
                      cvv = item[3]
                      fullcc = f"{cc}|{mes}|{ano}|{cvv}"

                      file_name = f"{limit}x_CC_Scraped_By_@BarryxBot.txt"
                      with open(file_name, 'a') as f:
                        cclist = open(f"{file_name}").read().splitlines()
                        if fullcc in cclist:
                          dublicate += 1
                        else:
                          f.write(f"{fullcc}\n")

                  total_cc = amt_cc
                  cc_found = total_cc - dublicate
                  await bot.delete_messages(message.chat.id, delete.id)
                  caption = caption = f"""
[ϟ] 𝑪𝑪 𝑺𝒄𝒓𝒂𝒑𝒆𝒅 ✅
━━━━━━━━━━━━━━━━━━
[ϟ] Source: {title}
[ϟ] Requested: <code>{limit}</code>
[ϟ] Found: <code>{cc_found}</code>
[ϟ] Duplicates: <code>{dublicate}</code>
[ϟ] User: <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.first_name}</a> [{status}]
[ϟ] Bot By: <a href=\"tg://user?id=6440962840\">Nairobiangoon</a>
━━━━━━━━━━━━━━━━━━
"""
                  document = file_name
                  scr_done = await message.reply_document(
                    document=document,
                    caption=caption,
                    reply_to_message_id=message.id)
                  module_name = "credit"
                  deduct = credit - 1
                  value = deduct
                  updatedata(user_id, module_name, value)

                  if scr_done:
                    name = document
                    my_file = Path(name)
                    my_file.unlink(missing_ok=True)

                except Exception as e:
                  e = str(e)
                  fr_error = 'Telegram says: [400 USER_ALREADY_PARTICIPANT] - The user is already a participant of this chat (caused by "messages.ImportChatInvite")'
                  sec_error = 'Telegram says: [400 INVITE_HASH_EXPIRED] - The chat invite link is no longer valid (caused by "messages.ImportChatInvite")'
                  if e == fr_error:
                    chat_info = await user.get_chat(channel_link)
                    channel_id = chat_info.id
                    title = chat_info.title
                    try:
                      amt_cc = 0
                      dublicate = 0
                      async for msg in user.get_chat_history(
                          channel_id, limit):
                        all_history = str(msg.text)
                        if all_history == 'None':
                          all_history = "INVALID CC NUMBER BC"
                        else:
                          all_history = all_history
                        all_cards = all_history.split('\n')
                        cards = []
                        for x in all_cards:
                          car = getcards(x)
                          if car:
                            cards.append(car)
                          else:
                            continue
                        len_cards = len(cards)
                        if not len_cards:
                          resp = "𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗 𝗔𝗡𝗬 𝗩𝗔𝗟𝗜𝗗 𝗖𝗔𝗥𝗗"
                        for item in cards:
                          amt_cc += 1
                          cc = item[0]
                          mes = item[1]
                          ano = item[2]
                          cvv = item[3]
                          fullcc = f"{cc}|{mes}|{ano}|{cvv}"

                          file_name = f"{limit}x_CC_Scraped_By_@BarryxBot.txt"
                          with open(file_name, 'a') as f:
                            cclist = open(f"{file_name}").read().splitlines()
                            if fullcc in cclist:
                              dublicate += 1
                            else:
                              f.write(f"{fullcc}\n")

                      total_cc = amt_cc
                      cc_found = total_cc - dublicate
                      await bot.delete_messages(message.chat.id, delete.id)
                      caption = caption = f"""
[ϟ] 𝑪𝑪 𝑺𝒄𝒓𝒂𝒑𝒆𝒅 ✅
━━━━━━━━━━━━━━━━━━
[ϟ] Source: {title}
[ϟ] Requested: <code>{limit}</code>
[ϟ] Found: <code>{cc_found}</code>
[ϟ] Duplicates: <code>{dublicate}</code>
[ϟ] User: <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.first_name}</a> [{status}]
[ϟ] Bot By: <a href=\"tg://user?id=6440962840\">Nairobiangoon</a>
━━━━━━━━━━━━━━━━━━
"""
                      document = file_name
                      scr_done = await message.reply_document(
                        document=document,
                        caption=caption,
                        reply_to_message_id=message.id)
                      module_name = "credits"
                      deduct = credit - 1
                      value = deduct
                      updatedata(user_id, module_name, value)

                      if scr_done:
                        name = document
                        my_file = Path(name)
                        my_file.unlink(missing_ok=True)
                    except Exception as e:
                      await bot.delete_messages(message.chat.id, delete.id)
                      await message.reply_text(e, message.id)
                  elif e == sec_error:
                    resp = "𝗪𝗿𝗼𝗻𝗴 𝗜𝗻𝘃𝗶𝘁𝗲 𝗟𝗶𝗻𝗸 ❌"
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(resp, message.id)
                  else:
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(e, message.id)
              else:
                try:
                  amt_cc = 0
                  dublicate = 0
                  async for msg in user.get_chat_history(channel_link, limit):
                    all_history = str(msg.text)
                    if all_history == 'None':
                      all_history = "INVALID CC NUMBER BC"
                    else:
                      all_history = all_history
                    all_cards = all_history.split('\n')
                    cards = []
                    for x in all_cards:
                      car = getcards(x)
                      if car:
                        cards.append(car)
                      else:
                        continue
                    len_cards = len(cards)
                    if not len_cards:
                      resp = "𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗 𝗔𝗡𝗬 𝗩𝗔𝗟𝗜𝗗 𝗖𝗔𝗥𝗗"
                    for item in cards:
                      amt_cc += 1
                      cc = item[0]
                      mes = item[1]
                      ano = item[2]
                      cvv = item[3]
                      fullcc = f"{cc}|{mes}|{ano}|{cvv}"

                      file_name = f"{limit}x_CC_Scraped_By_@BarryxBot.txt"
                      with open(file_name, 'a') as f:
                        cclist = open(f"{file_name}").read().splitlines()
                        if fullcc in cclist:
                          dublicate += 1
                        else:
                          f.write(f"{fullcc}\n")

                  chat_info = await user.get_chat(channel_link)
                  title = chat_info.title
                  total_cc = amt_cc
                  cc_found = total_cc - dublicate
                  await bot.delete_messages(message.chat.id, delete.id)
                  caption = caption = f"""
[ϟ] 𝑪𝑪 𝑺𝒄𝒓𝒂𝒑𝒆𝒅 ✅
━━━━━━━━━━━━━━━━━━
[ϟ] Source: {title}
[ϟ] Requested: <code>{limit}</code>
[ϟ] Found: <code>{cc_found}</code>
[ϟ] Duplicates: <code>{dublicate}</code>
[ϟ] User: <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.first_name}</a> [{status}]
[ϟ] Bot By: <a href=\"tg://user?id=644096284\">Nairobiangoon</a>
━━━━━━━━━━━━━━━━━━
"""
                  document = file_name
                  scr_done = await message.reply_document(
                    document=document,
                    caption=caption,
                    reply_to_message_id=message.id)
                  module_name = "credits"
                  deduct = credit - 1
                  value = deduct
                  updatedata(user_id, module_name, value)

                  if scr_done:
                    name = document
                    my_file = Path(name)
                    my_file.unlink(missing_ok=True)

                except Exception as e:
                  e = str(e)
                  first_error = "Error : local variable 'file_name' referenced before assignment"
                  sec_error = 'Telegram says: [400 USERNAME_NOT_OCCUPIED] - The username is not occupied by anyone (caused by "contacts.ResolveUsername")'
                  third_error = "local variable 'file_name' referenced before assignment"
                  fourth_error = 'Telegram says: [400 USERNAME_INVALID] - The username is invalid (caused by "contacts.ResolveUsername")'
                  if e == first_error:
                    resp = "No CC Found"
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(text=resp,
                                             reply_to_message_id=message.id)
                  elif e == sec_error:
                    resp = "𝗪𝗿𝗼𝗻𝗴 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 ❌"
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(text=resp,
                                             reply_to_message_id=message.id)
                  elif e == third_error:
                    resp = "𝗡𝗼 𝗖𝗖 𝗙𝗼𝘂𝗻𝗱 ❌"
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(text=resp,
                                             reply_to_message_id=message.id)
                  elif e == fourth_error:
                    resp = "𝗪𝗿𝗼𝗻𝗴 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 ❌"
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(text=resp,
                                             reply_to_message_id=message.id)
                  else:
                    await bot.delete_messages(message.chat.id, delete.id)
                    await message.reply_text(text=e,
                                             reply_to_message_id=message.id)
          
