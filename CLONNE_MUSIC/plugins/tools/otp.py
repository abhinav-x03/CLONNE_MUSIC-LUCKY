from pyrogram import filters
from CLONNE_MUSIC import app
from CLONNE_MUSIC.plugins.tools.connect import login_sessions
from CLONNE_MUSIC.utils.database.clonedb import save_assistant

@app.on_message(filters.command("otp") & filters.private)
async def otp_verify(client, message):

    bot = await client.get_me()
    bot_id = bot.id

    if bot_id not in login_sessions:
        return await message.reply_text("Use /connect first ❌")

    data = login_sessions[bot_id]
    assistant = data["client"]
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]

    otp = "".join(message.command[1:])

    await assistant.sign_in(
        phone_number=phone,
        phone_code=otp,
        phone_code_hash=phone_code_hash
    )

    string_session = await assistant.export_session_string()

    await save_assistant(bot_id, string_session)

    await message.reply_text("Assistant Connected ✅")

    await assistant.disconnect()
    del login_sessions[bot_id]
