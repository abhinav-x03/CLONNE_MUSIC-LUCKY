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
