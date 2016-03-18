import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from random import choice as randchoice
import json
import aiohttp
import html
import random
import os

class Insult:

    """Airenkun's Insult Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.insults = fileIO("data/insult/insults.json","load")

    @commands.command(pass_context=True, no_pm=True)
    async def insult(self, ctx, user : discord.Member=None):
        """Insult the user"""

        msg = ' '
        if user != None:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = (" How original. No one else had thought of trying to get the bot to insult "
                        "itself. I applaud your creativity. Yawn. Perhaps this is why you don't have "
                        "friends. You don't add anything new to any conversation. You are more of a "
                        "bot than me, predictable answers, and absolutely dull to have an actual conversation with.")
                await self.bot.say(user.mention + msg)
            else:
                api = random.randint(0, 2)
                if api == 0:
                    msg = ' {}'.format(randchoice(self.insults))
                elif api == 1:
                    url = 'http://www.insultgenerator.org/'
                    async with aiohttp.get(url) as r:
                        insult = await r.text()
                    insult = html.unescape(insult.split('\n')[13][8:-6])
                    msg = ' {}'.format(insult)
                elif api == 2:
                    url = 'http://quandyfactory.com/insult/json'
                    async with aiohttp.get(url) as r:
                        insult = await r.json()
                    msg = ' {}'.format(insult['insult'])
                await self.bot.say(user.mention + msg)
        else:
            await self.bot.say(ctx.message.author.mention + msg + randchoice(self.insults))


def check_folders():
    folders = ("data", "data/insult/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    """Moves the file from cogs to the data directory. Important -> Also changes the name to insults.json"""
    insults = {"You ugly as hell damn. Probably why most of your friends are online right?"}

    if not os.path.isfile("data/insult/insults.json"):
        if os.path.isfile("cogs/put_in_cogs_folder.json"):
            print("moving default insults.json...")
            os.rename("cogs/put_in_cogs_folder.json", "data/insult/insults.json")
        else:
            print("creating default insults.json...")
            fileIO("data/insult/insults.json", "save", insults)


def setup(bot):
    check_folders()
    check_files()
    n = Insult(bot)
    bot.add_cog(n)
