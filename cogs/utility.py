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
import os
import io
import traceback
import textwrap
import aiohttp
import inspect
import random
from contextlib import redirect_stdout
from discord.ext import commands
import json
import datetime
import pytz


def dev_check(id):
    with open('data/devs.json') as f:
        devs = json.load(f)
    if id in devs:
        return True
    return False


def cleanup_code(content):
    '''Automatically removes code blocks from the code.'''
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')


def random_color():
    color = ('#%06x' % random.randint(8, 0xFFFFFF))
    color = int(color[1:], 16)
    color = discord.Color(value=color)
    return color


class Utility:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embedsay(self, ctx, *, body: str):
        '''Send a simple embed'''
        em = discord.Embed(description=body, color=random_color())
        await ctx.send(embed=em)

    @commands.command()
    async def tinyurl(self, ctx, *, link: str):
        '''Makes a link shorter using the tinyurl api'''
        await ctx.message.delete()
        url = 'http://tinyurl.com/api-create.php?url=' + link
        async with self.bot.session.get(url) as resp:
            new = await resp.text()
        emb = discord.Embed(color=random_color())
        emb.add_field(name="Original Link", value=link, inline=False)
        emb.add_field(name="Shortened Link", value=new, inline=False)
        emb.set_footer(text='Powered by tinyurl.com',
                       icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
        await ctx.send(embed=emb)

    @commands.command()
    async def hastebin(self, ctx, *, code):
        '''Hastebin-ify your code!'''
        async with self.bot.post("https://hastebin.com/documents", data=code) as resp:
            data = await resp.json()
            key = data['key']
        await ctx.message.edit(content=f"Hastebin-ified! <https://hastebin.com/{key}.py>")

    @commands.command()
    async def date(self, ctx, tz=None):
        """Get the current UTC date."""
        now = datetime.datetime.now(tz=pytz.UTC)
        if tz:
            try:
                now = now.astimezone(pytz.timezone(tz))
            except:
                return await ctx.send('Please take a look at the [list](https://github.com/cree-py/creepy.py/blob/master/data/timezones.json) of timezones.')
        await ctx.send(f'The current date is {now:%A, %B %d, %Y}.')

    @commands.command()
    async def time(self, ctx, tz=None):
        """Get the current time."""
        now = datetime.datetime.now(pytz.UTC)
        if tz:
            try:
                now = now.astimezone(pytz.timezone(tz))
            except:
                return await ctx.send('Please take a look at the [list](https://github.com/cree-py/creepy.py/blob/master/data/timezones.json) of timezones.')
        await ctx.send(f'It is currently {now:%I:%M:%S %p}.')

    @commands.command()
    async def isitchristmas(self, ctx, tz=None):
        '''Is it Christmas?'''
        now = datetime.datetime.now()
        c = datetime.datetime(now.year, 12, 25)
        if now.month == 12 and now.day > 25:
            c = datetime.datetime((now.year + 1), 12, 25)
        days_until = c - now
        if days_until.days == 0:
            await ctx.send('Merry Christmas!')
        else:
            await ctx.send(f'No, there are {days_until.days} more days until Christmas.')

    @commands.command()
    async def multiply(self, ctx, a: int, b: int):
        '''Multiply two numbers'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}*{b}`\n✅ Solution: `{a * b}`'
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Utility(bot))
