import discord
from discord.ext import commands
import random


class Brawl_Stars_Box_Simulator:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['open', 'box'])
    async def boxsim(self, ctx):
        '''Simulate a box opening in Brawl Stars'''
        common = ["Shelly", "El Primo", "Colt", "Nita", "Dynamike"]
        rare = ["Bull", "Brock", "Barley", "Jessie"]
        superrare = ["Poco", "Ricochet", "Bo"]
        epic = ["Pam", "Piper"]
        mythic = ["Mortis", "Tara"]
        legendary = ["Spike", "Crow"]

        num = random.randint(0, 100)
        if num < 35:
            result = "1 Elixir"
        elif num < 40:
            result = "2 Elixir"
        elif num < 44:
            result = "3 Elixir"
        elif num < 47:
            result = "5 Elixir"
        elif num < 49:
            result = "7 Elixir"
        elif num < 50:
            result = "10 Elixir"
        elif num < 85:
            rand = random.randint(0, 4)
            result = common[rand]
        elif num < 85:
            rand = random.randint(0, 3)
            result = rare[rand]
        elif num < 94:
            rand = random.randint(0, 2)
            result = superrare[rand]
        elif num < 97:
            rand = random.randint(0, 1)
            result = epic[rand]
        elif num < 99:
            rand = random.randint(0, 1)
            result = mythic[rand]
        else:
            rand = random.randint(0, 1)
            result = legendary[rand]

        await ctx.send("**Tap! Tap!**")
        await ctx.send(result)
        result = result.replace(" ", "-")
        if num >= 50:
            try:
                await ctx.send(file=discord.File(f'./data/img/{result.lower()}.png'))
            except Exception as e:
                print(e)


def setup(bot):
    bot.add_cog(Brawl_Stars_Box_Simulator(bot))
