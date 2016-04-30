import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import os
import time
import aiohttp
import urllib
import asyncio
from copy import deepcopy
import random

# Check if BeautifulSoup4 is installed
try:
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False

# Check if Dota2py is installed
try:
	from dota2py import api
	dotaAvailable = True
except:
	dotaAvailable = False

# Check if tabulate is installed
try:
	from tabulate import tabulate
	tabulateAvailable = True
except:
	tabulateAvailable = False

class Dota:
	"""Dota 2 Red Cog"""

	def __init__(self, bot):
		self.bot = bot
		self.dota_settings = fileIO("data/dota/settings.json", "load")

		# Check for key either in settings or in ENV
		if "key" in self.dota_settings.keys() and self.dota_settings["key"] != "":

			# If exists in setting and is set
			api.set_api_key(self.dota_settings["key"])
			self.key = True

		elif os.environ.get("DOTA2_API_KEY") is not None:

			# If exists in env vars and is set
			api.set_api_key(os.environ.get("DOTA2_API_KEY"))
			self.key = True

		else:
			self.key = False


	@commands.group(pass_context = True)
	async def dota(self, ctx):
		"""Returns various data for dota players"""

		if ctx.invoked_subcommand is None:
			await self.bot.say("Type help dota for info.")

	@dota.command(name = 'setkey', pass_context = True)
	async def setkey(self, ctx, key):
		"""Sets the Dota 2 Wep API key (PM ONLY)"""

		# Perform the PM check
		if ctx.message.channel.is_private:

			self.dota_settings["key"] = key.strip()
			fileIO("data/dota/settings.json", "save", self.dota_settings)

			# Set the client's API key
			api.set_api_key(self.dota_settings["key"])

			# Change the current key status
			self.key = True

			await self.bot.say("Key saved and applied")
		else:
			await self.bot.say("Please run this command in PM")

	@dota.command(name = 'online', pass_context = True)
	async def online(self, ctx):
		"""Returns current amount of players"""

		# Build an url
		url = "https://steamdb.info/app/570/graphs/"

		async with aiohttp.get(url) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser") 

		# Parse the data and send it
		try:
			online = soupObject.find(class_='home-stats').find('li').find('strong').get_text() 
			await self.bot.say(online + ' players are playing this game at the moment')
		except:
			await self.bot.say("Couldn't load amount of players. No one is playing this game anymore or there's an error.")

	@dota.command(name = 'hero', pass_context = True)
	async def hero(self, ctx, *, hero):
		"""Shows some info about hero"""

		# Get and parse the required hero
		reqHero = urllib.parse.quote(hero.lower())

		# Moved hero table builder to separate function for a more clean code
		# TODO: Probably should make it a more "global" function and pass down the ctx into it
		async def buildHeroInfo(payload):
			herojson = payload

			if herojson["Range"] == 128:
				herotype = "Melee"
			else:
				herotype = "Ranged"

			# Generate the needed table
			table = [
				[
					"HP",
					herojson["HP"],
					"%.2f" % (float(herojson["StrGain"]) * 19)
				],
				[
					"MP",
					herojson["Mana"],
					"%.2f" % (float(herojson["IntGain"]) * 19)
				],
				[
					"AGI",
					herojson["BaseAgi"],
					herojson["AgiGain"]
				],
				[
					"STR",
					herojson["BaseStr"],
					herojson["StrGain"]
				],
				[
					"INT",
					herojson["BaseInt"],
					herojson["IntGain"]
				],
				[
					"Damage",
					"53~61",
					""
				],
				[
					"Armor",
					herojson["Armor"],
					"%.2f" % (float(herojson["AgiGain"]) * 0.14)
				],
				[
					"Movespeed",
					herojson["Movespeed"],
					herojson["AgiGain"]
				]
			]

			table[1 + herojson["PrimaryStat"]][0] = "[" + table[1 + herojson["PrimaryStat"]][0] + "]"

			# Compose the final message
			message = "";
			message += "**"  + hero.title() + "** (" + herotype + ")\n"
			message += "This hero's stats:\n\n"
			message += "```"
			message += tabulate(table, headers=["Stat","Value","Gain/lvl"], tablefmt="fancy_grid")
			message += "```\n"

			# Legs are fun
			if (herojson["Legs"] > 0):
				message += "Also you might consider buying " + str(herojson["Legs"]) + " boots, because this hero, apparently, has " + str(herojson["Legs"]) + " legs! ;)"
			else:
				message += "Talking about boots... this hero seems to have no legs, so you might consider playing without any ;)"

			await self.bot.say(message)
		
		# Get the proper hero name
		url =  "http://api.herostats.io/heroes/" + reqHero

		try:

			# Get the info
			async with aiohttp.get(url) as r:
				data = await r.json()
			if "error" not in data.keys():

				# Build the data into a nice table and send
				await buildHeroInfo(data)
			else:
				await self.bot.say(data["error"])
		except:

			# Nothing can be done
			await self.bot.say('Dota API is offline')

	@dota.command(name = 'build', pass_context = True)
	async def build(self, ctx, *, hero):
		"""Gets most popular skillbuild for a hero"""

		# Build an url
		url = "http://www.dotabuff.com/heroes/" + hero.lower().replace(" ", "-")

		async with aiohttp.get(url, headers = {"User-Agent": "Red-DiscordBot"}) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser") 

		# "build" will contain a final table
		# "headers" will contain table headers with lvl numbers
		build = []
		headers = ""

		try:
			skillSoup = soupObject.find(class_='skill-choices')

			# Generate skill tree
			for skill in enumerate(skillSoup.find_all(class_='skill')):

				# Get skill names for the first row
				build.append([skill[1].find(class_='line').find(class_='icon').find('img').get('alt')])

				# Generate build order
				for entry in enumerate(skill[1].find(class_='line').find_all(class_='entry')):
					if "choice" in entry[1].get("class"):
						build[skill[0]].append("X")
					else:
						build[skill[0]].append(" ")

			# Get a part of the table
			def getPartialTable(table, start, end):
				tables = []
				for row in enumerate(table):
					if start == 0:
						result = []
					else:
						result = [table[row[0]][0]]
					result[1:] = row[1][start:end]
					tables.append(result)
				return tables

			# Generate 2 messages (for a splitted table)
			# TODO: Convert into one "for" cycle
			message = "The most popular build **at the moment**, according to Dotabuff:\n\n"
			message += "```"
			headers = ["Skill/Lvl"]
			headers[len(headers):] = range(1,7)
			message += tabulate(getPartialTable(build,0,7), headers=headers, tablefmt="fancy_grid")
			message += "```\n"

			message += "```"
			headers = ["Skill/Lvl"]
			headers[len(headers):] = range(7,14)
			message += tabulate(getPartialTable(build,7,13), headers=headers, tablefmt="fancy_grid")
			message += "```\n"

			# Send first part
			await self.bot.say(message)

			message = "```"
			headers = ["Skill/Lvl"]
			headers[len(headers):] = range(14,21)
			message += tabulate(getPartialTable(build,13,19), headers=headers, tablefmt="fancy_grid")
			message += "```\n"

			# Send second part
			await self.bot.say(message)
		except:

			# Nothing can be done
			await self.bot.say("Error parsing Dotabuff, maybe try again later")

	@dota.command(name = 'items', pass_context = True)
	async def items(self, ctx, *, hero):
		"""Gets the most popular items for a hero"""

		# Build an url
		url = "http://www.dotabuff.com/heroes/" + hero.lower().replace(" ", "-")
		
		async with aiohttp.get(url, headers = {"User-Agent": "Red-DiscordBot"}) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser") 

		# Get the needed data fron the page
		# TODO: Add try-except block
		items = soupObject.find_all("section")[3].find("tbody").find_all("tr")

		# "build" will contain a final table
		build = []

		# Generate the buld from data
		for item in items:
			build.append(
				[
					item.find_all("td")[1].find("a").get_text(),
					item.find_all("td")[2].get_text(),
					item.find_all("td")[4].get_text()
				]
			)

		# Compose the message
		message = "The most popular items **at the moment**, according to Dotabuff:\n\n```"
		message += tabulate(build, headers=["Item", "Matches", "Winrate"], tablefmt="fancy_grid")
		message += "```"

		await self.bot.say(message)

	@dota.command(name = 'recent', pass_context = True)
	async def recent(self, ctx, player):
		"""Gets the link to player's latest match"""

		# Check it there is an api key set
		if not self.key:
			await self.bot.say("Please set the dota 2 api key using [p]dota setkey command")
			raise RuntimeError("Please set the dota 2 api key using [p]dota setkey command")

		# Required to check if user provided the ID or not
		def is_number(s):
			try:
				int(s)
				return True
			except ValueError:
				return False

		# Check if user provided the ID
		if is_number(player.strip()):

			# if he did - assign as-is
			account_id = player.strip()
		else:
			# if he did not - get the id from the vanity name
			account_id = api.get_steam_id(player)["response"]

			# Check if the result was correcct
			if (int(account_id["success"]) > 1):
				await self.bot.say("Player not found :(")
			else:
				account_id = account_id["steamid"]
		
		try:
			# Get the data from Dota API
			matches = api.get_match_history(account_id=account_id)["result"]["matches"]
			match = api.get_match_details(matches[0]["match_id"])
			heroes = api.get_heroes()

			# Operation was a success
			dotaServes = True
		except:

			# Well... if anything fails...
			dotaServes = False
			print('Dota servers SO BROKEN!')
		
		# Proceed to data parsing
		if dotaServes:

			# Create a proper heroes list
			heroes = heroes["result"]["heroes"]
			def build_dict(seq, key):
				return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
			heroes = build_dict(heroes, "id")

			# Reassign match info for ease of use
			match = match["result"]

			# Construct message
			message = "Showing the most recent match for **" + player + "** (match id: **" + str(match["match_id"]) + "**)\n"
			if "radiant_win" in match:
				message += "**RADIANT WON**"
			else:
				message += "**DIRE WON**"

			m, s = divmod(match["duration"], 60)
			h, m = divmod(m, 60)

			message += " [" + "%d:%02d:%02d" % (h, m, s) + "]\n"

			# Create a list of played heroes
			played_heroes = []
			for player in enumerate(match["players"]):
				played_heroes.append(heroes[player[1]["hero_id"]]["localized_name"])

			# "table" will be used to store the finalized match data
			table = []

			# Form Radiant team
			for i in range(0,5):
				table.append([
						played_heroes[i],
						str(match["players"][i]["kills"]) + "/" + str(match["players"][i]["deaths"]) + "/" + str(match["players"][i]["assists"]),
						played_heroes[5+i],
						str(match["players"][5+i]["kills"]) + "/" + str(match["players"][5+i]["deaths"]) + "/" + str(match["players"][5+i]["assists"])
					])

			# Compose message
			message += "\n```"
			message += tabulate(table, headers=["Radiant Team", "K/D/A", "Dire Team", "K/D/A"], tablefmt="fancy_grid")
			message += "```"
			message += "\nDotabuff match link: http://www.dotabuff.com/matches/" + str(match["match_id"])

			await self.bot.say(message)
		else:
			await self.bot.say('Oops.. Something is wrong with Dota2 servers, try again later!')

def check_folders():
	if not os.path.exists("data/dota"):
		print("Creating data/dota folder...")
		os.makedirs("data/dota")

def check_files():
	f = "data/dota/settings.json"
	if not fileIO(f, "check"):
		print("Creating empty settings.json...")
		fileIO(f, "save", {})

def setup(bot):
	if soupAvailable is False:
		raise RuntimeError("You don't have BeautifulSoup installed, run\n```pip3 install bs4```And try again")
		return
	if dotaAvailable is False:
		raise RuntimeError("You don't have dota2py installed, run\n```pip3 install dota2py```And try again")
		return
	if tabulateAvailable is False:
		raise RuntimeError("You don't have tabulate installed, run\n```pip3 install tabulate```And try again")
		return
	check_folders()
	check_files()
	bot.add_cog(Dota(bot))
