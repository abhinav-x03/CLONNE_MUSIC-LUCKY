from pyrogram import Client, filters
from CLONNE_MUSIC import app
from config import API_ID, API_HASH

login_sessions = {}

@app.on_message(filters.command("connect") & filters.private)
async def connect_assistant(client, message):

    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/connect +91XXXXXXXXXX")

    phone = message.command[1]

    msg = await message.reply_text("📲 Sending OTP...")

    assistant = Client(
        name=f"assistant_login_{message.from_user.id}",
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="CLONNE_MUSIC Assistant",
        system_version="v2",
        app_version="Assistant Login"
    )

    await assistant.connect()

    try:
        sent_code = await assistant.send_code(phone)

        login_sessions[message.from_user.id] = {
            "client": assistant,
            "phone": phone,
            "phone_code_hash": sent_code.phone_code_hash
        }

        await msg.edit("✅ OTP Sent!\n\nSend OTP like:\n`/otp 1 2 3 4 5`")

    except Exception as e:
        await msg.edit(f"❌ Error:\n{e}")
