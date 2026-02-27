from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.CLONNE_MUSIC

# Collections
clonebotdb = db.clonebots
cmode = db.cmode
assistant = db.assistant
authuser = db.authuser
blacklist = db.blacklist
sudoers = db.sudoers
langdb = db.lang
votedb = db.votes

# ===== CMODE =====
async def get_cmode(chat_id):
    data = cmode.find_one({"chat_id": chat_id})
    return data.get("mode") if data else None

async def set_cmode(chat_id, mode):
    cmode.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

# ===== AUTH USERS =====
async def get_authuser(chat_id):
    return authuser.find_one({"chat_id": chat_id})

async def add_authuser(chat_id, user_id):
    authuser.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )

# ===== BLACKLIST =====
async def blacklist_chat(chat_id):
    blacklist.update_one(
        {"chat_id": chat_id},
        {"$set": {"blocked": True}},
        upsert=True
    )

async def is_blacklisted(chat_id):
    return blacklist.find_one({"chat_id": chat_id})

# ===== SUDO =====
async def add_sudo(user_id):
    sudoers.update_one(
        {"user_id": user_id},
        {"$set": {"sudo": True}},
        upsert=True
    )

async def is_sudo(user_id):
    return sudoers.find_one({"user_id": user_id})
    
# ===== AUTH USERS =====
async def get_authuser(chat_id):
    return authuser.find_one({"chat_id": chat_id})

async def add_authuser(chat_id, user_id):
    authuser.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )
    # ===== LANGUAGE =====
async def get_lang(chat_id):
    data = langdb.find_one({"chat_id": chat_id})
    return data.get("lang") if data else "en"

async def set_lang(chat_id, lang):
    langdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"lang": lang}},
        upsert=True
    )

async def get_authuser_names(chat_id):
    data = authuser.find_one({"chat_id": chat_id})
    if not data:
        return []
    return data.get("names", [])

async def save_authuser_name(chat_id, name):
    authuser.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"names": name}},
        upsert=True
    )
    # ===== VOTES =====
async def get_upvote_count(chat_id):
    data = votedb.find_one({"chat_id": chat_id})
    return data.get("upvotes", 0) if data else 0

async def get_downvote_count(chat_id):
    data = votedb.find_one({"chat_id": chat_id})
    return data.get("downvotes", 0) if data else 0

async def add_upvote(chat_id):
    votedb.update_one(
        {"chat_id": chat_id},
        {"$inc": {"upvotes": 1}},
        upsert=True
    )

async def add_downvote(chat_id):
    votedb.update_one(
        {"chat_id": chat_id},
        {"$inc": {"downvotes": 1}},
        upsert=True
    )
