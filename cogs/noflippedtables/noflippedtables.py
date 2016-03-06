import discord
from discord.ext import commands
import asyncio
import os
from .utils.dataIO import fileIO
import re
from __main__ import send_cmd_help

class Untableflip:
	"""For the table sympathizers"""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/noflippedtables/settings.json", "load")

	@commands.group(pass_context=True)
	async def tableset(self, ctx):
		"""Got some nice settings for my UNflipped tables"""
		if ctx.invoked_subcommand is None:
			await send_cmd_help(ctx)
			msg = "```"
			for k, v in self.settings.items():
				msg += str(k) + ": " + str(v) + "\n"
			msg = "```"
			await self.bot.say(msg)

	@tableset.command(name="flipall")
	async def flipall(self):
		"""Enables/disables right all unflipped tables in a message"""
		self.settings["ALL_TABLES"] = not self.settings["ALL_TABLES"]
		if self.settings["ALL_TABLES"]:
			await self.bot.say("All tables will now be unflipped.")
		else:
			await self.bot.say("Now only one table unflipped per message.")
		fileIO("data/noflippedtables/settings.json", "save", self.settings)

	@tableset.command(name="flipbot")
	async def flipbot(self):
		"""Enables/disables allowing bot to flip tables"""
		self.settings["BOT_EXEMPT"] = not self.settings["BOT_EXEMPT"]
		if self.settings["BOT_EXEMPT"]:
			await self.bot.say("Bot is now allowed to leave its own tables flipped")
		else:
			await self.bot.say("Bot must now unflip tables that itself flips")
		fileIO("data/noflippedtables/settings.json", "save", self.settings)

	#so much fluff just for this OpieOP
	async def scrutinize_messages(self, message):
		if not self.settings["BOT_EXEMPT"] or message.author.id != self.bot.user.id:
			tables = ""
			for m in re.finditer('┻━*┻', message.content):
				tables += m.group().replace('┻','┬').replace('━','─') + " ノ( ゜-゜ノ)" + "\n"
				if not self.settings["ALL_TABLES"]:
					break
			if tables != "":
				await self.bot.send_message(message.channel, tables)

def check_folders():
	if not os.path.exists("data/noflippedtables"):
		print("Creating data/noflippedtables folder...")
		os.makedirs("data/noflippedtables")


def check_files():
	settings = {"ALL_TABLES" : True, "BOT_EXEMPT" : False}
	f = "data/noflippedtables/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json...")
		fileIO(f, "save", settings)

def setup(bot):
	check_folders()
	check_files()
	n = Untableflip(bot)
	bot.add_listener(n.scrutinize_messages, "on_message")
	bot.add_cog(n)
