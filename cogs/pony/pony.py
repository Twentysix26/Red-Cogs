from discord.ext import commands
import aiohttp

# This cog is a modification of the gif and gifr section of the 'images' cog.
# Usage: [p]pony [text...] retrieves the first result from Derpibooru, filtered with tags
# Usage: [p]ponyr [text...] retreives a random result from Derpibooru, optionally filtered with tags

class Pony:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    async def pony(self, *text):
        """Retrieves the first result from Derpibooru"""
        if len(text) > 0:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "https://derpiboo.ru/search.json?q=" + msg
                    async with aiohttp.get(search) as r:
                        result = await r.json()
                    if result["search"] != []:
                        url = "http:" + result["search"][0]["image"]
                        await self.bot.say(url)
                    else:
                        await self.bot.say("Your search terms gave no results.")                         
                except:     
                    await self.bot.say("Error.")
            else:           
                await self.bot.say("Invalid search.")
        else:   
            await self.bot.say("pony [text]")
            
    @commands.command(no_pm=True)
    async def ponyr(self, *text):
        """Retrieves a random result from Derpibooru"""
        if len(text) > 0:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "https://derpiboo.ru/search.json?q=" + msg + "&random_image=y" 
                    async with aiohttp.get(search) as r:
                        result = await r.json()
                    if result["id"] != []:
                        imgid = str(result["id"])
                        async with aiohttp.get("https://derpiboo.ru/images/" + imgid + ".json") as r:
                            result = await r.json()
                        url = "http:" + result["image"]
                        await self.bot.say(url)
                    else:
                        await self.bot.say("Your search terms gave no results.")
                except:
                    await self.bot.say("Error.")
            else:
                await self.bot.say("Invalid search.")
        else:
            async with aiohttp.get("https://derpiboo.ru/search.json?q=*&random_image=y") as r:
                result = await r.json()
            imgid = str(result["id"])
            async with aiohttp.get("https://derpiboo.ru/images/" + imgid + ".json") as r:
                result = await r.json()
            url = result["image"]
            await self.bot.say("http:" + url )

def setup(bot):
    bot.add_cog(Pony(bot))
