import discord
from discord.ext import commands
from .utils import checks

class SimplyGoogle:
    """A non sarcastic google command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def google(self, ctx, text):
        """I don't need to explain this"""
        uri = "https://www.google.com/search?q="
        quary =  str(ctx.message.content[len(ctx.prefix+ctx.command.name)+1:].replace(" ","+"))
        await self.bot.say(uri+quary)

def setup(bot):
    n = SimplyGoogle(bot)
    bot.add_cog(n)
