from discord.ext import commands
import aiohttp
try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

# This cog searches http://www.hearthpwn.com/ for images of Hearthstone cards
# Requires BeautifulSoup4. Use "pip3 install beautifulsoup4" if it is not already installed
# Use [p]card [name] to search for regular cards
# Use [p]cardg [name] to search for golden cards

class Hearthstone:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def card(self, *text):
        """Retrieves card art from a hearthpwn search"""
        if len(text) > 0:
            card = '+'.join([str(x) for x in text]) # convert the text list into a string joined by + characters for use in a web address
            url = "http://www.hearthpwn.com/cards?filter-name="+card #build the web adress
            async with aiohttp.get(url) as response:
                soupObject = BeautifulSoup(await response.text(), "html.parser") # get the web page and create a BeautifulSoup4 object
            try:
                img = soupObject.find("img")["src"] #find the first image tag and return the source attribute
            except:
                await self.bot.say("`Could not find that card, check your spelling or try another card.`") # if no image tag was found there were no results

            await self.bot.say(img) # post the link to the card image
        else:
            await self.bot.say("```card [name]\n\nSearches http://www.hearthpwn.com/\nReturns first available card that matches the search text.\nUse \"cardg\" to get gold cards.```")

    @commands.command()
    async def cardg(self, *text):
        """Retrieves golden card art from a hearthpwn search"""
        if len(text) > 0:
            card = '+'.join([str(x) for x in text])
            url = "http://www.hearthpwn.com/cards?filter-name="+card
            async with aiohttp.get(url) as response:
                soupObject = BeautifulSoup(await response.text(), "html.parser")
            try:
                img = soupObject.find("img")["data-gifurl"] #find the first image tag and return the data-gifurl attribute
            except:
                await self.bot.say("`Could not find that card, check your spelling or try another card.`")
            await self.bot.say(img)
        else:
            await self.bot.say("```cardg [name]\n\nSearches http://www.hearthpwn.com/\nReturns first available gold card that matches the search text.\nUse \"card\" to get regular cards.```")

def setup(bot):
    if soupAvailable:
        bot.add_cog(Hearthstone(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
