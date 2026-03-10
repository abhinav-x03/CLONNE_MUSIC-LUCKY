import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

from config import API_ID, API_HASH, OWNER_ID
from pyrogram.sessions import StringSession

from CLONNE_MUSIC.utils.database.clonedb import (
    get_owner_id_from_db,
    get_clone_string,
    set_clone_string,
    remove_clone_string,
)

from CLONNE_MUSIC.utils.decorators.language import language

clone_assistants = {}


async def start_clone_assistant(bot_id, string_session):

    if bot_id in clone_assistants:
        try:
            await clone_assistants[bot_id].stop()
        except:
            pass

    try:
        userbot = Client(
            f"clone_assistant_{bot_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=str(string_session),
            in_memory=True,
        )

        await userbot.start()

        me = await userbot.get_me()

        userbot.id = me.id
        userbot.username = me.username
        userbot.name = me.mention

        clone_assistants[bot_id] = userbot

        return userbot

    except Exception as e:
        logging.exception(e)
        return None


async def stop_clone_assistant(bot_id):

    if bot_id in clone_assistants:
        try:
            await clone_assistants[bot_id].stop()
        except:
            pass

        del clone_assistants[bot_id]


def get_clone_assistant(bot_id):
    return clone_assistants.get(bot_id)


# ---------------- CONNECT LOGIN ---------------- #

@Client.on_message(filters.command("connect") & filters.private)
@language
async def connect_login(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)

    if message.from_user.id not in [OWNER_ID, C_OWNER]:
        return await message.reply_text("Only bot owner can login assistant.")

    await message.reply_text(
        "**Send Details Like This:**\n\n"
        "`API_ID API_HASH PHONE_NUMBER`\n\n"
        "Example:\n"
        "`123456 abcdef123456 +911234567890`"
    )

    data = await client.listen(message.from_user.id)

    try:
        api_id, api_hash, phone = data.text.split()
    except:
        return await message.reply_text("Invalid format.")

    string = StringSession()

    app = Client(
        string,
        api_id=int(api_id),
        api_hash=api_hash,
        in_memory=True,
    )

    await app.connect()

    code = await app.send_code(phone)

    await message.reply("Send OTP Code")

    otp = await client.listen(message.from_user.id)

    try:
        await app.sign_in(phone, code.phone_code_hash, otp.text)

    except SessionPasswordNeeded:

        await message.reply("Send 2FA Password")

        pwd = await client.listen(message.from_user.id)

        await app.check_password(pwd.text)

    session_string = await app.export_session_string()

    await app.disconnect()

    await message.reply_text(
        f"**Login Successful**\n\n"
        f"`{session_string}`"
    )


# ---------------- SETSTRING ---------------- #

@Client.on_message(filters.command(["setstring", "setassistant"]) & filters.private)
@language
async def set_string_cmd(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)

    if message.from_user.id not in [OWNER_ID, C_OWNER]:
        return await message.reply_text("Only bot owner can set assistant.")

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n\n/setstring STRING_SESSION"
        )

    string_session = message.text.split(None, 1)[1]

    mi = await message.reply_text("Starting assistant...")

    userbot = await start_clone_assistant(bot_id, string_session)

    if userbot is None:
        return await mi.edit_text("Invalid string session.")

    set_clone_string(bot_id, string_session)

    me = await userbot.get_me()

    await mi.edit_text(
        f"Assistant Connected\n\n"
        f"User: {me.mention}\n"
        f"Username: @{me.username}\n"
        f"ID: `{me.id}`"
    )

    try:
        await message.delete()
    except:
        pass


# ---------------- REMOVE ASSISTANT ---------------- #

@Client.on_message(filters.command("removeassistant") & filters.private)
async def remove_assistant(client, message):

    bot = await client.get_me()
    bot_id = bot.id

    await stop_clone_assistant(bot_id)

    remove_clone_string(bot_id)

    await message.reply("Assistant removed.")


# ---------------- ASSISTANT STATUS ---------------- #

@Client.on_message(filters.command(["assistant","myassistant"]))
@language
async def assistant_status(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)

    if message.from_user.id not in [OWNER_ID, C_OWNER]:
        return

    string_session = get_clone_string(bot_id)

    userbot = get_clone_assistant(bot_id)

    if not string_session:
        return await message.reply_text("No assistant set.")

    if userbot:

        me = await userbot.get_me()

        await message.reply_text(
            f"Assistant Running\n\n"
            f"{me.mention}\n"
            f"@{me.username}\n"
            f"`{me.id}`"
        )

    else:

        await message.reply_text(
            "Assistant string exists but not started."
)
