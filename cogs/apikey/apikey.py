from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from __main__ import settings as bot_settings
# Sys.
import discord
from discord.ext import commands
import asyncio
import json
import os

COGS = "cogs/"
DIR_DATA = "data/apikeys"
API_KEYS = DIR_DATA+"/api_keys.json"

class apikey:
    """API key installer"""

    def __init__(self, bot):
        self.bot = bot
        self.keys = fileIO(API_KEYS, "load")
        self.PREFIXES = bot_settings.prefixes

    @commands.command(pass_context=True, no_pm=False)
    async def apikey(self, ctx, cog, *key):
        """Store the API keys for you keys"""
        if key == ():
            await send_cmd_help(ctx)
            return
        else:
            if fileIO(COGS+cog+".py", "check"):
                self.keys["api_keys"][cog] = {"api_key": key[0]}
                fileIO(API_KEYS, "save", self.keys)
                await self.bot.say("`Api key stored, you may need to do a {}reload {}`".format(self.PREFIXES[0], cog))
            else:
                await self.bot.say("`That cog doesn't exist`")
                    
def check_folders():
    if not os.path.exists(DIR_DATA):
        print("Creating data/apikeys folder...")
        os.makedirs(DIR_DATA)

def check_files():
    keys = {"api_keys": {}}
    
    if not fileIO(API_KEYS, "check"):
        print("Creating api_keys.json")
        fileIO(API_KEYS, "save", keys)

def setup(bot):
    check_folders()
    check_files()
    n = apikey(bot)
    bot.add_cog(n)


