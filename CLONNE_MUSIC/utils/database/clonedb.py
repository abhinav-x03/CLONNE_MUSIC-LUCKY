from CLONNE_MUSIC.utils.database import clonebotdb


async def add_clone(user_id, bot_token, bot_id):
    clonebotdb.insert_one({
        "user_id": user_id,
        "bot_token": bot_token,
        "bot_id": bot_id
    })


async def has_user_cloned_any_bot(user_id):
    data = clonebotdb.find_one({"user_id": user_id})
    return True if data else False


async def get_user_clones(user_id):
    return clonebotdb.find({"user_id": user_id})


async def remove_clone(bot_id):
    clonebotdb.delete_one({"bot_id": bot_id})


def get_owner_id_from_db(bot_id):
    data = clonebotdb.find_one({"bot_id": bot_id})
    if data:
        return data.get("user_id")
    return None


async def get_cloned_support_chat(bot_id):
    data = clonebotdb.find_one({"bot_id": bot_id})
    if data:
        return data.get("support", "")
    return ""


async def get_cloned_support_channel(bot_id):
    data = clonebotdb.find_one({"bot_id": bot_id})
    if data:
        return data.get("channel", "")
    return ""


def check_bot_premium(bot_id):
    data = clonebotdb.find_one({"bot_id": bot_id})
    if data:
        return data.get("premium", None)
    return None


def set_clone_string(bot_id, string_session):
    """Save a Pyrogram string session for a cloned bot's assistant."""
    clonebotdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"string_session": string_session}},
    )


def get_clone_string(bot_id):
    """Retrieve the stored string session for a cloned bot."""
    data = clonebotdb.find_one({"bot_id": bot_id})
    if data:
        return data.get("string_session", None)
    return None


def remove_clone_string(bot_id):
    """Remove the string session for a cloned bot."""
    clonebotdb.update_one(
        {"bot_id": bot_id},
        {"$unset": {"string_session": ""}},
    )
