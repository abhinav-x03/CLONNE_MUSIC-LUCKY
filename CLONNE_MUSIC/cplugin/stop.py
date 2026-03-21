from pyrogram import filters, Client
from pyrogram.types import Message

from CLONNE_MUSIC import app
from CLONNE_MUSIC.core.call import LUCKY
from CLONNE_MUSIC.utils.database import set_loop
from CLONNE_MUSIC.utils.decorators import AdminRightsCheck
from CLONNE_MUSIC.utils.inline import close_markup
from CLONNE_MUSIC.cplugin.connect import get_clone_pytgcalls
from config import BANNED_USERS


@Client.on_message(
    filters.command(
        ["end", "stop", "cend", "cstop"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    bot = await cli.get_me()
    clone_ptc = get_clone_pytgcalls(bot.id)
    await LUCKY.stop_stream(chat_id, clone_pytgcalls=clone_ptc)
    await set_loop(chat_id, 0)
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention), reply_markup=close_markup(_)
    )
