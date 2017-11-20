'''
MIT License

Copyright (c) 2017 Cree-Py

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import discord
from discord.ext import commands
import random


class Bsboxsim:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['open', 'box'])
    async def boxsim(self, ctx):
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

        await ctx.send("Tap! Tap!")
        await ctx.send(result)
        result = result.replace(" ", "-")
        try:
            # fixed back :/
            await ctx.send(file=discord.File(f'./data/brawlers/{result.lower()}.png'))
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Bsboxsim(bot))
