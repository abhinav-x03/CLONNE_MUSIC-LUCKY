import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
    SessionPasswordNeeded,
)

from config import API_ID, API_HASH, OWNER_ID
from CLONNE_MUSIC.utils.database import clonebotdb
from CLONNE_MUSIC.utils.database.clonedb import (
    get_owner_id_from_db,
    get_clone_string,
    set_clone_string,
    remove_clone_string,
)
from CLONNE_MUSIC.utils.decorators.language import language

# Global dict to hold running assistant (userbot) clients for each cloned bot.
# Keyed by bot_id -> pyrogram.Client instance
clone_assistants = {}


async def start_clone_assistant(bot_id, string_session):
    """Start a userbot client for a cloned bot using its string session.
    Returns the started Client or None on failure."""
    if bot_id in clone_assistants:
        # Already running, stop old one first
        try:
            await clone_assistants[bot_id].stop()
        except Exception:
            pass

    try:
        userbot = Client(
            f"clone_assistant_{bot_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=str(string_session),
            no_updates=True,
            in_memory=True,
        )
        await userbot.start()
        me = await userbot.get_me()
        userbot.id = me.id
        userbot.name = me.mention
        userbot.username = me.username
        clone_assistants[bot_id] = userbot
        logging.info(
            f"Clone assistant started for bot {bot_id}: @{me.username} (ID: {me.id})"
        )
        return userbot
    except Exception as e:
        logging.exception(f"Failed to start clone assistant for bot {bot_id}: {e}")
        return None


async def stop_clone_assistant(bot_id):
    """Stop a running clone assistant."""
    if bot_id in clone_assistants:
        try:
            await clone_assistants[bot_id].stop()
        except Exception:
            pass
        del clone_assistants[bot_id]


def get_clone_assistant(bot_id):
    """Get the running assistant client for a cloned bot, or None."""
    return clone_assistants.get(bot_id)


# ---- /setstring command ----

@Client.on_message(filters.command(["setstring", "setassistant"]) & filters.private)
@language
async def set_string_cmd(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(
            "**You are not the owner of this bot.**\n\n"
            "Only the bot owner can set the string session."
        )

    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage:** `/setstring <pyrogram_string_session>`\n\n"
            "**Example:**\n"
            "`/setstring BQA...your_string_session...`\n\n"
            "This sets an assistant (userbot) for your cloned bot "
            "so it can join voice chats.\n\n"
            "**Generate one at:** @StringSessionGen_bot or similar bots.\n\n"
            "**To remove:** `/setstring remove`"
        )

    session_value = message.text.split(None, 1)[1].strip()

    # Handle removal
    if session_value.lower() in ("remove", "delete", "clear"):
        await stop_clone_assistant(bot_id)
        remove_clone_string(bot_id)
        return await message.reply_text(
            "**Assistant removed successfully.**\n"
            "The bot will now use the main assistant for voice chats."
        )

    mi = await message.reply_text("**Validating string session...**")

    # Try to start the userbot to validate
    userbot = await start_clone_assistant(bot_id, session_value)
    if userbot is None:
        return await mi.edit_text(
            "**Invalid string session!**\n\n"
            "Could not start the assistant with the provided session.\n"
            "Please check the string session and try again."
        )

    # Save to DB
    set_clone_string(bot_id, session_value)

    me = await userbot.get_me()
    await mi.edit_text(
        f"**Assistant set successfully!**\n\n"
        f"**Assistant:** {me.mention}\n"
        f"**Username:** @{me.username}\n"
        f"**ID:** `{me.id}`\n\n"
        f"Now use `/connect` in a group to connect the assistant."
    )

    # Delete the message with the string session for security
    try:
        await message.delete()
    except Exception:
        pass


# ---- /connect command ----

@Client.on_message(filters.command(["connect", "joinvc"]) & filters.group)
@language
async def connect_cmd(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        # Also allow group admins
        try:
            member = await client.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if member.status not in ("administrator", "creator"):
                return await message.reply_text(
                    "**Only the bot owner or group admins can use this command.**"
                )
        except Exception:
            return await message.reply_text(
                "**Only the bot owner or group admins can use this command.**"
            )

    # Check if the bot has a string session set
    string_session = get_clone_string(bot_id)
    if not string_session:
        return await message.reply_text(
            "**No assistant configured!**\n\n"
            "The bot owner must first set a string session using:\n"
            "`/setstring <pyrogram_string_session>` (in PM)\n\n"
            "This allows the bot to have its own assistant for voice chats."
        )

    # Get or start the assistant
    userbot = get_clone_assistant(bot_id)
    if userbot is None:
        mi = await message.reply_text("**Starting assistant...**")
        userbot = await start_clone_assistant(bot_id, string_session)
        if userbot is None:
            return await mi.edit_text(
                "**Failed to start assistant!**\n\n"
                "The string session may be expired. "
                "Ask the bot owner to set a new one with `/setstring`."
            )
    else:
        mi = await message.reply_text("**Connecting assistant...**")

    chat_id = message.chat.id

    # Try to join the group
    try:
        # Check if already a member
        try:
            member = await client.get_chat_member(chat_id, userbot.id)
            if member.status not in ("banned", "restricted", "left"):
                return await mi.edit_text(
                    f"**Assistant already connected!**\n\n"
                    f"**Assistant:** @{userbot.username}\n"
                    f"The assistant is already in this group."
                )
        except UserNotParticipant:
            pass
        except Exception:
            pass

        # Join using chat username or invite link
        if message.chat.username:
            try:
                await userbot.join_chat(message.chat.username)
            except UserAlreadyParticipant:
                return await mi.edit_text(
                    f"**Assistant already connected!**\n\n"
                    f"**Assistant:** @{userbot.username}"
                )
        else:
            try:
                invite_link = await client.export_chat_invite_link(chat_id)
                await userbot.join_chat(invite_link)
            except ChatAdminRequired:
                return await mi.edit_text(
                    "**I need 'Invite Users via Link' admin permission "
                    "to invite the assistant to this group.**"
                )
            except InviteRequestSent:
                return await mi.edit_text(
                    "**Join request sent!**\n\n"
                    "Please approve the assistant's join request in the group."
                )
            except UserAlreadyParticipant:
                return await mi.edit_text(
                    f"**Assistant already connected!**\n\n"
                    f"**Assistant:** @{userbot.username}"
                )

        await mi.edit_text(
            f"**Assistant connected successfully!**\n\n"
            f"**Assistant:** @{userbot.username}\n"
            f"The assistant has joined this group and is ready for voice chats."
        )

    except Exception as e:
        logging.exception(f"Failed to connect assistant to group {chat_id}: {e}")
        await mi.edit_text(
            f"**Failed to connect assistant!**\n\n"
            f"Error: `{e}`"
        )


# ---- /disconnect command ----

@Client.on_message(filters.command(["disconnect", "leavevc"]) & filters.group)
@language
async def disconnect_cmd(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        try:
            member = await client.get_chat_member(
                message.chat.id, message.from_user.id
            )
            if member.status not in ("administrator", "creator"):
                return await message.reply_text(
                    "**Only the bot owner or group admins can use this command.**"
                )
        except Exception:
            return await message.reply_text(
                "**Only the bot owner or group admins can use this command.**"
            )

    userbot = get_clone_assistant(bot_id)
    if userbot is None:
        return await message.reply_text("**No assistant is currently connected.**")

    try:
        await userbot.leave_chat(message.chat.id)
        await message.reply_text("**Assistant disconnected from this group.**")
    except Exception as e:
        await message.reply_text(f"**Failed to disconnect:** `{e}`")


# ---- /assistant command (check status) ----

@Client.on_message(filters.command(["assistant", "myassistant"]))
@language
async def check_assistant_cmd(client: Client, message: Message, _):
    bot = await client.get_me()
    bot_id = bot.id

    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(
            "**Only the bot owner can check assistant status.**"
        )

    string_session = get_clone_string(bot_id)
    userbot = get_clone_assistant(bot_id)

    if not string_session:
        return await message.reply_text(
            "**No assistant configured.**\n\n"
            "Use `/setstring <pyrogram_string_session>` in PM to set one."
        )

    if userbot:
        me = await userbot.get_me()
        status = "Running"
        info = (
            f"**Assistant:** {me.mention}\n"
            f"**Username:** @{me.username}\n"
            f"**ID:** `{me.id}`"
        )
    else:
        status = "Not Running"
        info = "Assistant has a string session but is not started."

    await message.reply_text(
        f"**Assistant Status:** {status}\n\n{info}"
    )
