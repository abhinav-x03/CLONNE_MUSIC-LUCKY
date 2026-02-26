from pyrogram import filters
from pyrogram.types import Message

from CLONNE_MUSIC import app
from CLONNE_MUSIC.core.call import LUCKY

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await LUCKY.stop_stream_force(message.chat.id)
