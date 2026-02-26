import asyncio, os, time, aiohttp
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from asyncio import sleep
from CLONNE_MUSIC import app
from pyrogram import filters, Client, enums
from pyrogram.enums import ParseMode
from pyrogram.types import *
from typing import Union, Optional
import random

random_photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

# --------------------------------------------------------------------------------- #

def get_font(font_size, font_path):
    return ImageFont.truetype(font_path, font_size)

# --------------------------------------------------------------------------------- #
# PERFECT TEMPLATE FIT VERSION
# --------------------------------------------------------------------------------- #

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None
):
    bg = Image.open(bg_path).convert("RGBA")

    # Your template EXACT circle position
    circle_size = 520  # perfect center fit
    circle_center_x = 1080
    circle_center_y = 540

    paste_x = circle_center_x - circle_size // 2
    paste_y = circle_center_y - circle_size // 2

    if profile_path:
        img = Image.open(profile_path).convert("RGBA")

        img = img.resize((circle_size, circle_size))

        mask = Image.new("L", (circle_size, circle_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, circle_size, circle_size), fill=255)

        circular_img = Image.new("RGBA", (circle_size, circle_size), (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)

        bg.paste(circular_img, (paste_x, paste_y), circular_img)

    # Draw user ID
    draw = ImageDraw.Draw(bg)
    draw.text(
        (180, 860),
        text=str(user_id).upper(),
        font=get_font(60, font_path),
        fill=(255, 0, 0),
    )

    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #

bg_path = "CLONNE_MUSIC/assets/userinfo.png"
font_path = "CLONNE_MUSIC/assets/hiroko.ttf"

# --------------------------------------------------------------------------------- #

INFO_TEXT = """**
❅─────✧❅✦❅✧─────❅
            ✦ ᴜsᴇʀ ɪɴғᴏ ✦

➻ ᴜsᴇʀ ɪᴅ ‣ **`{}`
**➻ ғɪʀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ʟᴀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ᴜsᴇʀɴᴀᴍᴇ ‣ **`{}`
**➻ ᴍᴇɴᴛɪᴏɴ ‣ **{}
**➻ ʟᴀsᴛ sᴇᴇɴ ‣ **{}
**➻ ᴅᴄ ɪᴅ ‣ **{}
**➻ ʙɪᴏ ‣ **`{}`

**❅─────✧❅✦❅✧─────❅**
"""

# --------------------------------------------------------------------------------- #

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "Recently."
        elif x == enums.UserStatus.LAST_WEEK:
            return "Last week."
        elif x == enums.UserStatus.LONG_AGO:
            return "Long time ago."
        elif x == enums.UserStatus.OFFLINE:
            return "Offline."
        elif x == enums.UserStatus.ONLINE:
            return "Online."
    except:
        return "**Something went wrong!**"

# --------------------------------------------------------------------------------- #

@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "%", ",", ".", "@", "#"]))
async def userinfo(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # If user gives ID: /info 12345
    if not message.reply_to_message and len(message.command) == 2:
        try:
            user_id = message.text.split(None, 1)[1]
            user_info = await app.get_chat(user_id)
            user = await app.get_users(user_id)
            status = await userstatus(user.id)

            id = user_info.id
            dc_id = user.dc_id
            first_name = user_info.first_name
            last_name = user_info.last_name if user_info.last_name else "No last name"
            username = user_info.username if user_info.username else "No Username"
            mention = user.mention
            bio = user_info.bio if user_info.bio else "No bio set"

            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                welcome_photo = await get_userinfo_img(bg_path, font_path, user.id, photo)
            else:
                welcome_photo = random.choice(random_photo)

            await app.send_photo(
                chat_id, 
                photo=welcome_photo, 
                caption=INFO_TEXT.format(id, first_name, last_name, username, mention, status, dc_id, bio),
                reply_to_message_id=message.id
            )

        except Exception as e:
            await message.reply_text(str(e))
            return

    # If user uses /info without reply
    elif not message.reply_to_message:
        try:
            user_info = await app.get_chat(user_id)
            user = await app.get_users(user_id)
            status = await userstatus(user.id)

            id = user_info.id
            dc_id = user.dc_id
            first_name = user_info.first_name
            last_name = user_info.last_name if user_info.last_name else "No last name"
            username = user_info.username if user_info.username else "No Username"
            mention = user.mention
            bio = user_info.bio if user_info.bio else "No bio set"

            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                welcome_photo = await get_userinfo_img(bg_path, font_path, user.id, photo)
            else:
                welcome_photo = random.choice(random_photo)

            await app.send_photo(
                chat_id,
                photo=welcome_photo,
                caption=INFO_TEXT.format(id, first_name, last_name, username, mention, status, dc_id, bio),
                reply_to_message_id=message.id
            )

        except Exception as e:
            await message.reply_text(str(e))
            return

    # If user replies to someone
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

        try:
            user_info = await app.get_chat(user_id)
            user = await app.get_users(user_id)
            status = await userstatus(user.id)

            id = user_info.id
            dc_id = user.dc_id
            first_name = user_info.first_name
            last_name = user_info.last_name if user_info.last_name else "No last name"
            username = user_info.username if user_info.username else "No Username"
            mention = user.mention
            bio = user_info.bio if user_info.bio else "No bio set"

            if user.photo:
                photo = await app.download_media(user.photo.big_file_id)
                welcome_photo = await get_userinfo_img(bg_path, font_path, user.id, photo)
            else:
                welcome_photo = random.choice(random_photo)

            await app.send_photo(
                chat_id,
                photo=welcome_photo,
                caption=INFO_TEXT.format(id, first_name, last_name, username, mention, status, dc_id, bio),
                reply_to_message_id=message.id
            )

        except Exception as e:
            await message.reply_text(str(e))
            return