import discord
from discord.ext import commands
from random import choice as rndchoice
from .utils.dataIO import fileIO
from .utils import checks
import os


class Slap:
    """Slap command."""

    def __init__(self, bot):
        self.bot = bot
        self.items = fileIO("data/slap/items.json", "load")

    def save_items(self):
        fileIO("data/slap/items.json", 'save', self.items)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def slap(self, ctx, *, user : discord.Member=None):
        """Slap a user"""
        if ctx.invoked_subcommand is None:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                await self.bot.say("Dont make me slap you instead " + user.name)
                return
            await self.bot.say("-slaps " + user.name + " with " +
                               (rndchoice(self.items) + "-"))

    @slap.command()
    async def add(self, item):
        """Adds an item"""
        self.items.append(item)
        self.save_items()
        await self.bot.say("Item added.")

    @slap.command()
    @checks.is_owner()
    async def remove(self, item):
        """Removes item"""
        if item in self.items:
            self.items.remove(item)
            self.save_items()
            await self.bot.say("item removed.")


def check_folders():
    if not os.path.exists("data/slap"):
        print("Creating data/slap folder...")
        os.makedirs("data/slap")


def check_files():
    f = "data/slap/items.json"
    if not fileIO(f, "check"):
        print("Creating empty items.json...")
        fileIO(f, "save", [])


def setup(bot):
    check_folders()
    check_files()
    n = Slap(bot)
    bot.add_cog(n)
