import re
import logging
import asyncio
import importlib
from sys import argv
from pyrogram import idle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import (
    AccessTokenExpired,
    AccessTokenInvalid,
)
from CLONNE_MUSIC.utils.database import get_assistant
from config import API_ID, API_HASH
from CLONNE_MUSIC import app
from config import OWNER_ID
from CLONNE_MUSIC.misc import SUDOERS
from CLONNE_MUSIC.utils.database import get_assistant, clonebotdb
from CLONNE_MUSIC.utils.database.clonedb import has_user_cloned_any_bot
from config import LOGGER_ID, CLONE_LOGGER
import requests
import aiohttp
from CLONNE_MUSIC.utils.decorators.language import language
import pyrogram.errors

from CLONNE_MUSIC.utils.database.clonedb import get_owner_id_from_db, get_clone_string
from CLONNE_MUSIC.cplugin.connect import start_clone_assistant
from config import SUPPORT_CHAT, OWNER_ID, BOT_USERNAME, SUPPORT_CHANNEL

from datetime import datetime
CLONES = set()

C_BOT_DESC = f"Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\nVɪsɪᴛ: @{BOT_USERNAME} ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n - Uᴘᴅᴀᴛᴇ: [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({SUPPORT_CHAT})\n - Sᴜᴘᴘᴏʀᴛ: [ᴄʟɪᴄᴋ ʜᴇʀᴇ]({SUPPORT_CHANNEL})]"

C_BOT_COMMANDS = [
                {"command": "/start", "description": "sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ"},
                {"command": "/help", "description": "ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs."},
                {"command": "/play", "description": "sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."},
                {"command": "/pause", "description": "ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/resume", "description": "ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."},
                {"command": "/skip", "description": "ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."},
                {"command": "/end", "description": "ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/ping", "description": "ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."},
                {"command": "/id", "description": "ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ɪᴅ. ɪғ ᴜsᴇᴅ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ɢᴇᴛs ᴛʜᴀᴛ ᴜsᴇʀ's ɪᴅ."}

            ]


@app.on_message(filters.command("clone"))
@language
async def clone_txt(client, message, _):
    userbot = await get_assistant(message.chat.id)

    userid = message.from_user.id
    has_already_cbot = await has_user_cloned_any_bot(userid)

    if has_already_cbot:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_H_0"])
    else:
        pass
    

    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text(_["C_B_H_2"])
        try:
            ai = Client(
                f"clone_new_{message.from_user.id}",
                API_ID,
                API_HASH,
                bot_token=bot_token,
                plugins=dict(root="CLONNE_MUSIC.cplugin"),
                in_memory=True,
            )
            await ai.start()
            bot = await ai.get_me()
            bot_users = await ai.get_users(bot.username)
            bot_id = bot_users.id
            c_b_owner_fname = message.from_user.first_name
            c_bot_owner = message.from_user.id

        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text(_["C_B_H_3"])
            return

        await mi.edit_text(_["C_B_H_5"])
        try:

            await app.send_message(
                CLONE_LOGGER, f"**#NewClonedBot**\n\n**Bᴏᴛ:- {bot.mention}**\n**Usᴇʀɴᴀᴍᴇ:** @{bot.username}\n**Bᴏᴛ ID :** `{bot_id}`\n\n**Oᴡɴᴇʀ : ** [{c_b_owner_fname}](tg://user?id={c_bot_owner})"
            )
            await userbot.send_message(bot.username, "/start")

            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": message.from_user.id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
                "channel": "AbhinavXupdate",
                "support": "Abhinav_Chatgroup",
                "premium" : False,
                "Date" : False,
            }
            clonebotdb.insert_one(details)
            CLONES.add(bot.id)

            def set_bot_commands():
                url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
                
                params = {"commands": C_BOT_COMMANDS}
                response = requests.post(url, json=params)
                print(response.json())

            set_bot_commands()

            def set_bot_desc():
                url = f"https://api.telegram.org/bot{bot_token}/setMyDescription"
                params = {"description": C_BOT_DESC}
                response = requests.post(url, data=params)
                if response.status_code == 200:
                    logging.info(f"Successfully updated Description for bot: {bot_token}")
                else:
                    logging.error(f"Failed to update Description: {response.text}")

            set_bot_desc()

            await mi.edit_text(_["C_B_H_6"].format(bot.username))
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>ᴇʀʀᴏʀ:</b>\n\n<code>{e}</code>\n\n**ᴋɪɴᴅʟʏ ғᴏᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ [sᴜᴘᴘᴏʀᴛ]({SUPPORT_CHAT}) ᴛᴏ ɢᴇᴛ ᴀssɪsᴛᴀɴᴄᴇ**"
            )
    else:
        await message.reply_text(_["C_B_H_1"])


@app.on_message(
    filters.command(
        [
            "delbot",
            "rmbot",
            "delcloned",
            "delclone",
            "deleteclone",
            "removeclone",
            "cancelclone",
        ]
    )
)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            await message.reply_text(_["C_B_H_8"])
            return

        query_value = " ".join(message.command[1:])
        if query_value.startswith("@"):
            query_value = query_value[1:]
        await message.reply_text(_["C_B_H_9"])

        cloned_bot = clonebotdb.find_one({"$or": [{"token": query_value}, {"username": query_value}]})
        
        if cloned_bot:

            bot_info = f"**Bot ID**: `{cloned_bot['bot_id']}`\n" \
           f"**Bᴏᴛ Nᴀᴍᴇ**: {cloned_bot['name']}\n" \
           f"**Usᴇʀɴᴀᴍᴇ**: @{cloned_bot['username']}\n" \
           f"**Tᴏᴋᴇɴ**: `{cloned_bot['token']}`\n" \
           f"**Oᴡɴᴇʀ**: `{cloned_bot['user_id']}`\n"

            C_OWNER = get_owner_id_from_db(cloned_bot['bot_id'])
            OWNERS = [OWNER_ID, C_OWNER]

            if message.from_user.id not in OWNERS:
                return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

            clonebotdb.delete_one({"_id": cloned_bot["_id"]})
            CLONES.remove(cloned_bot["bot_id"])

            await message.reply_text(_["C_B_H_10"])
            await app.send_message(
                CLONE_LOGGER, bot_info
            )
        else:
            await message.reply_text(_["C_B_H_11"])
    except Exception as e:
        await message.reply_text(_["C_B_H_12"])
        await app.send_message(
                CLONE_LOGGER, bot_info
            )
        logging.exception(e)


async def _validate_token(session, bot_token):
    """Validate a bot token using aiohttp (non-blocking)."""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            return resp.status == 200
    except Exception:
        return False


async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots........")
        bots = list(clonebotdb.find())
        if not bots:
            logging.info("No cloned bots found in database.")
            return

        botNumber = 1
        failed = 0

        async with aiohttp.ClientSession() as session:
            for bot in bots:
                bot_token = bot.get("token")
                bot_username = bot.get("username", "unknown")
                bot_id = bot.get("bot_id", "unknown")

                if not bot_token:
                    logging.error(f"No token found for bot: {bot_username}, skipping")
                    failed += 1
                    continue

                try:
                    # Validate token without blocking the event loop
                    is_valid = await _validate_token(session, bot_token)
                    if not is_valid:
                        logging.error(
                            f"Invalid or expired token for bot: {bot_username} (ID: {bot_id}), removing from DB"
                        )
                        clonebotdb.delete_one({"token": bot_token})
                        failed += 1
                        continue

                    # Use bot_id or sanitized name for session to avoid
                    # filesystem issues with ':' in bot tokens, and use
                    # in_memory to prevent stale session file conflicts
                    # after a kill -9 restart.
                    session_name = f"clone_{bot_id}"
                    ai = Client(
                        session_name,
                        API_ID,
                        API_HASH,
                        bot_token=bot_token,
                        plugins=dict(root="CLONNE_MUSIC.cplugin"),
                        in_memory=True,
                    )
                    await ai.start()
                    bot_info = await ai.get_me()
                    if bot_info.id not in CLONES:
                        CLONES.add(bot_info.id)

                    logging.info(
                        f"Started cloned bot #{botNumber}: @{bot_info.username} (ID: {bot_info.id})"
                    )
                    botNumber += 1

                    # Start the clone's own assistant if a string session exists
                    clone_string = get_clone_string(bot_info.id)
                    if clone_string:
                        try:
                            await start_clone_assistant(bot_info.id, clone_string)
                        except Exception as e:
                            logging.error(
                                f"Failed to start assistant for clone @{bot_info.username}: {e}"
                            )

                    # Short delay to avoid Telegram flood limits
                    await asyncio.sleep(2)

                except (AccessTokenExpired, AccessTokenInvalid):
                    logging.error(
                        f"Token expired/invalid for bot: {bot_username}, removing from DB"
                    )
                    clonebotdb.delete_one({"token": bot_token})
                    failed += 1
                except Exception as e:
                    logging.exception(
                        f"Failed to restart cloned bot: {bot_username} - {e}"
                    )
                    failed += 1
                    continue

        started = botNumber - 1
        logging.info(
            f"Clone restart complete - Started: {started}, Failed: {failed}, Total: {len(bots)}"
        )
        try:
            await app.send_message(
                CLONE_LOGGER,
                f"All Cloned Bots Restart Complete!\n\nStarted: {started}\nFailed: {failed}\nTotal: {len(bots)}",
            )
        except Exception as e:
            logging.error(f"Failed to send restart summary to CLONE_LOGGER: {e}")
    except Exception as e:
        logging.exception("Error while restarting bots.")

# Zeo
@app.on_message(filters.command("delallclone") & filters.user(OWNER_ID))
@language
async def delete_all_cloned_bots(client, message, _):
    try:
        await message.reply_text(_["C_B_H_14"])

        clonebotdb.delete_many({})

        CLONES.clear()

        await message.reply_text(_["C_B_H_15"])
    except Exception as e:
        await message.reply_text("An error occurred while deleting all cloned bots.")
        logging.exception(e)


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    try:
        user_id = message.from_user.id
        cloned_bots = list(clonebotdb.find({"user_id": user_id}))
        
        if not cloned_bots:
            await message.reply_text(_["C_B_H_16"])
            return
        
        total_clones = len(cloned_bots)
        text = f"**Yᴏᴜʀ Cʟᴏɴᴇᴅ Bᴏᴛs: {total_clones}**\n\n"
        
        for bot in cloned_bots:
            text += f"**Bᴏᴛ Nᴀᴍᴇs:** {bot['name']}\n"
            text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n\n"
        
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while fetching your cloned bots.")



@app.on_message(filters.command("cloned") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text(_["C_B_H_13"])
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"

        chunk_size = 10
        chunks = [cloned_bots[i:i + chunk_size] for i in range(0, len(cloned_bots), chunk_size)]

        for chunk in chunks:
            chunk_text = text
            for bot in chunk:
                try:
                    owner = await client.get_users(bot['user_id'])
                    owner_name = owner.first_name
                    owner_profile_link = f"tg://user?id={bot['user_id']}"
                except pyrogram.errors.PeerIdInvalid:
                    owner_name = "Unknown User"
                    owner_profile_link = "#"
                except Exception as e:
                    logging.error(f"Error fetching user {bot['user_id']}: {e}")
                    owner_name = "Unknown User"
                    owner_profile_link = "#"

                chunk_text += f"**Bᴏᴛ ID:** `{bot.get('bot_id', 'Unknown')}`\n"
                chunk_text += f"**Bᴏᴛ Nᴀᴍᴇ:** {bot.get('name', 'Unknown')}\n"
                chunk_text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot.get('username', 'Unknown')}\n"
                chunk_text += f"**Oᴡɴᴇʀ:** [{owner_name}]({owner_profile_link})\n\n"

            await message.reply_text(chunk_text)

    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")



#total clone
@app.on_message(filters.command("totalbots") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"         

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")
