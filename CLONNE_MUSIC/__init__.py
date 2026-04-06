from CLONNE_MUSIC.core.bot import LUCKY
from CLONNE_MUSIC.core.dir import dirr
from CLONNE_MUSIC.core.git import git
from CLONNE_MUSIC.core.userbot import Userbot
from CLONNE_MUSIC.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = LUCKY()
userbot = Userbot()
api = SafoneAPI()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "InflexOwnerBot"  # connect music api key "Dont change it"
