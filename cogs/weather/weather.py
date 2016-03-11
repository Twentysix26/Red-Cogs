import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import os
from .utils.dataIO import fileIO


class WeatherSearch:
	"""Search for weather in given location."""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/weather/settings.json", "load")

	@commands.command(no_pm=True, pass_context=False)
	async def temp(self, location):
		url = "http://api.wunderground.com/api/" + self.settings['api_key'] + "/conditions/q/" + location + ".json"
		async with aiohttp.get(url) as r:
		    data = await r.json()
		if "current_observation" in data:
			temperature = data["current_observation"].get("temperature_string", "No temperature found.")
			await self.bot.say("Current temperature in your location is: " + temperature +".")
		else:
			await self.bot.say("Please use your zip code or the format City,State(City,Country if outside of the US). \n****NOTE:**** Include the ',' after the state and do NOT put a space after the ','")

def check_folders():
	if not os.path.exists("data/weather"):
		print("Creating data/weather folder...")
		os.makedirs("data/weather")

def check_files():
	settings = {"api_key": "Get your API key from: www.wunderground.com/weather/api/"}
	
	f = "data/weather/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json")
		print("You must obtain an API key as noted in the newly created 'settings.json' file")
		fileIO(f, "save", settings)

def setup(bot):
	check_folders()
	check_files()
	n = WeatherSearch(bot)
	bot.add_cog(n)
