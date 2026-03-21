import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

from config import API_ID, API_HASH, OWNER_ID
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded

from CLONNE_MUSIC.utils.database.clonedb import (
    get_owner_id_from_db,
    get_clone_string,
    set_clone_string,
    remove_clone_string,
)

from CLONNE_MUSIC.utils.decorators.language import language

# bot_id -> {"userbot": Client, "pytgcalls": PyTgCalls}
clone_assistants = {}


async def start_clone_assistant(bot_id, string_session):
    """Start a clone assistant with both Pyrogram client and PyTgCalls."""

    if bot_id in clone_assistants:
        try:
            old = clone_assistants[bot_id]
            if old.get("pytgcalls"):
                await old["pytgcalls"].stop()
            if old.get("userbot"):
                await old["userbot"].stop()
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

        # Create PyTgCalls instance for voice chat support
        pytgcalls = PyTgCalls(userbot, cache_duration=150)
        await pytgcalls.start()

        # Register stream end and leave event handlers
        _register_clone_handlers(bot_id, pytgcalls)

        clone_assistants[bot_id] = {
            "userbot": userbot,
            "pytgcalls": pytgcalls,
        }

        return userbot

    except Exception as e:
        logging.exception(e)
        return None


def _register_clone_handlers(bot_id, pytgcalls):
    """Register stream end/leave/kicked handlers on a clone's PyTgCalls."""
    from CLONNE_MUSIC.core.call import LUCKY

    @pytgcalls.on_kicked()
    @pytgcalls.on_closed_voice_chat()
    @pytgcalls.on_left()
    async def clone_stream_services_handler(_, chat_id: int):
        try:
            await LUCKY.stop_stream(chat_id, clone_pytgcalls=pytgcalls)
        except:
            pass

    @pytgcalls.on_stream_end()
    async def clone_stream_end_handler(client, update: Update):
        if not isinstance(update, StreamAudioEnded):
            return
        await LUCKY.change_stream(client, update.chat_id)


async def stop_clone_assistant(bot_id):
    """Stop and clean up a clone assistant."""

    if bot_id in clone_assistants:
        data = clone_assistants[bot_id]
        try:
            if data.get("pytgcalls"):
                await data["pytgcalls"].stop()
        except:
            pass
        try:
            if data.get("userbot"):
                await data["userbot"].stop()
        except:
            pass

        del clone_assistants[bot_id]


def get_clone_assistant(bot_id):
    """Get the clone assistant's Pyrogram Client."""
    data = clone_assistants.get(bot_id)
    if data:
        return data.get("userbot")
    return None


def get_clone_pytgcalls(bot_id):
    """Get the clone assistant's PyTgCalls instance for voice chat ops."""
    data = clone_assistants.get(bot_id)
    if data:
        return data.get("pytgcalls")
    return None


# ---------------- CONNECT LOGIN (Pyrogram v2) ---------------- #

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

    # Pyrogram v2 session generation
    temp_client = Client(
        f"connect_{message.from_user.id}",
        api_id=int(api_id),
        api_hash=api_hash,
        in_memory=True,
    )

    await temp_client.connect()

    try:
        code = await temp_client.send_code(phone)
    except Exception as e:
        await temp_client.disconnect()
        return await message.reply_text(f"Failed to send code: {e}")

    await message.reply("Send OTP Code (with spaces between digits, e.g. `1 2 3 4 5`)")

    otp = await client.listen(message.from_user.id)

    otp_text = otp.text.replace(" ", "")

    try:
        await temp_client.sign_in(phone, code.phone_code_hash, otp_text)

    except SessionPasswordNeeded:

        await message.reply("Send 2FA Password")

        pwd = await client.listen(message.from_user.id)

        try:
            await temp_client.check_password(pwd.text)
        except Exception as e:
            await temp_client.disconnect()
            return await message.reply_text(f"2FA failed: {e}")

    except Exception as e:
        await temp_client.disconnect()
        return await message.reply_text(f"Sign in failed: {e}")

    session_string = await temp_client.export_session_string()

    await temp_client.disconnect()

    # Auto-set the string session for this clone bot
    set_clone_string(bot_id, session_string)

    mi = await message.reply_text("Starting assistant with generated session...")

    userbot = await start_clone_assistant(bot_id, session_string)

    if userbot is None:
        return await mi.edit_text(
            "**Login Successful but assistant failed to start.**\n\n"
            f"Session saved. Try `/setstring {session_string}` later."
        )

    me = await userbot.get_me()

    await mi.edit_text(
        f"**Login Successful - Assistant Connected**\n\n"
        f"User: {me.mention}\n"
        f"Username: @{me.username}\n"
        f"ID: `{me.id}`\n\n"
        f"Your assistant can now join voice chats to play music!"
    )


# ---------------- SETSTRING (Pyrogram v2 string session) ---------------- #

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
            "**Usage:**\n\n"
            "`/setstring PYROGRAM_V2_STRING_SESSION`\n\n"
            "Generate one using /connect or an external tool."
        )

    string_session = message.text.split(None, 1)[1]

    mi = await message.reply_text("Starting assistant...")

    userbot = await start_clone_assistant(bot_id, string_session)

    if userbot is None:
        return await mi.edit_text("Invalid string session or failed to start.")

    set_clone_string(bot_id, string_session)

    me = await userbot.get_me()

    await mi.edit_text(
        f"**Assistant Connected**\n\n"
        f"User: {me.mention}\n"
        f"Username: @{me.username}\n"
        f"ID: `{me.id}`\n\n"
        f"Your assistant can now join voice chats to play music!"
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

    await message.reply("Assistant removed and disconnected.")


# ---------------- ASSISTANT STATUS ---------------- #

@Client.on_message(filters.command(["assistant", "myassistant"]))
@language
async def assistant_status(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)

    if message.from_user.id not in [OWNER_ID, C_OWNER]:
        return

    string_session = get_clone_string(bot_id)

    userbot = get_clone_assistant(bot_id)
    pytgcalls = get_clone_pytgcalls(bot_id)

    if not string_session:
        return await message.reply_text(
            "No assistant set.\n\n"
            "Use /connect to login or /setstring to set a Pyrogram v2 session."
        )

    if userbot:

        me = await userbot.get_me()

        vc_status = "Active" if pytgcalls else "Not available"

        await message.reply_text(
            f"**Assistant Running**\n\n"
            f"User: {me.mention}\n"
            f"Username: @{me.username}\n"
            f"ID: `{me.id}`\n"
            f"Voice Chat: {vc_status}"
        )

    else:

        await message.reply_text(
            "Assistant string exists but not started.\n"
            "Use /setstring to restart it."
        )
