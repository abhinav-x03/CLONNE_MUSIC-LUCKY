import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from CLONNE_MUSIC import YouTube, app
from CLONNE_MUSIC.misc import SUDOERS
from CLONNE_MUSIC.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from CLONNE_MUSIC.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string
from CLONNE_MUSIC.utils.assistant_loader import load_assistant
links = {}


def UserbotWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} is under maintenance, visit [support chat]({SUPPORT_CHAT}) for knowing the reason.",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except:
            pass

        chat_id = message.chat.id

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                try:
                    get = await app.get_chat_member(chat_id, userbot.id)
                except ChatAdminRequired:
                    return await message.reply_text(
                        "➥ 𝗣𝐥𝐞𝐚𝐬𝐞  𝗠𝐚𝐤𝐞  𝗠𝐞  𝗔𝐝𝐦𝐢𝐧  𝗔𝐧𝐝  𝗠𝐮𝐬𝐭  𝗚𝐢𝐯𝐞  𝗜𝐧𝐯𝐢𝐭𝐞  𝗨𝐬𝐞𝐫𝐬  𝗣𝐨𝐰𝐞𝐫  𝗙𝐨𝐫  𝗜𝐧𝐯𝐢𝐭𝐞  𝗠𝐲 𝗔𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭  𝗜𝐧  𝗧𝐡𝐢𝐬  𝗖𝐡𝐚𝐭."
                    )
                if (
                    get.status == ChatMemberStatus.BANNED
                    or get.status == ChatMemberStatus.RESTRICTED
                ):
                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention, userbot.id, userbot.name, userbot.username
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="๏ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ ๏",
                                        callback_data=f"unban_assistant",
                                    )
                                ]
                            ]
                        ),
                    )
            except UserNotParticipant:
                if message.chat.username:
                    invitelink = message.chat.username
                    await userbot.join_chat(invitelink)
                else:
                    if chat_id in links:
                        invitelink = links[chat_id]
                        try:
                            await userbot.resolve_peer(invitelink)
                        except:
                            pass
                    else:
                        try:
                            invitelink = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await message.reply_text(
                                "➥ 𝗣𝐥𝐞𝐚𝐬𝐞  𝗠𝐚𝐤𝐞  𝗠𝐞  𝗔𝐝𝐦𝐢𝐧 𝗔𝐧𝐝 𝗠𝐮𝐬𝐭  𝗚𝐢𝐯𝐞  𝗜𝐧𝐯𝐢𝐭𝐞  𝗨𝐬𝐞𝐫𝐬  𝗣𝐨𝐰𝐞𝐫  𝗙𝐨𝐫  𝗜𝐧𝐯𝐢𝐭𝐞  𝗠𝐲 𝗔𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐭  𝗜𝐧  𝗧𝐡𝐢𝐬  𝗖𝐡𝐚𝐭."
                            )
                        except Exception as e:
                            return await message.reply_text(
                                f"{app.mention} 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗝𝗼𝗶𝗻𝗲𝗱 𝗧𝗵𝗶𝘀 𝗚𝗿𝗼𝘂𝗽✅\n\n𝗜𝗱:- {userbot.mention}.."
                            )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                myu = await message.reply_text("𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗝𝗼𝗶𝗻𝗶𝗻𝗴 𝗧𝗵𝗶𝘀 𝗖𝗵𝗮𝘁..")
                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                    await myu.delete()
                    await message.reply_text(
                        f"{app.mention} 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗝𝗼𝗶𝗻𝗲𝗱 𝗧𝗵𝗶𝘀 𝗚𝗿𝗼𝘂𝗽✅\n\n𝗜𝗱:- **@{userbot.username}**"
                    )
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, userbot.id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    await asyncio.sleep(3)
                    await myu.delete()
                    await message.reply_text(
                        f"{app.mention} 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗝𝗼𝗶𝗻𝗲𝗱 𝗧𝗵𝗶𝘀 𝗚𝗿𝗼𝘂𝗽✅\n\n𝗜𝗱:- **@{userbot.username}**"
                    )
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        f"{app.mention} 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗝𝗼𝗶𝗻𝗲𝗱 𝗧𝗵𝗶𝘀 𝗚𝗿𝗼𝘂𝗽✅\n\n𝗜𝗱:- **@{userbot.username}**"
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except:
                    pass

        return await command(client, message, _, chat_id)

    return wrapper
