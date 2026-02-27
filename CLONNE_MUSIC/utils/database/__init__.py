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
