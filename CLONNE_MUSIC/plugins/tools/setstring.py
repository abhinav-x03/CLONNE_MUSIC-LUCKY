from pyrogram import filters
from CLONNE_MUSIC import app
from CLONNE_MUSIC.utils.database.clonedb import save_assistant

@app.on_message(filters.command("setstring") & filters.private)
async def set_string(client, message):

    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/setstring SESSION")

    string = message.text.split(None, 1)[1]

    await save_assistant(message.from_user.id, string)

    await message.reply_text(
        "✅ Assistant String Saved!\nOnly 1 Assistant Allowed."
    )
