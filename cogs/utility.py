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

    @commands.command(aliases=['setwelcome', 'welcomemsg', 'joinmessage', 'welcomeset'], no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def welcome(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('data/welcs.json', 'r+') as f:
            welc = json.load(f)

        if type.lower() in ('n', 'no', 'disabled', 'disabled', 'off'):
            welc[ctx.message.guild.id]['type'] = False
            json.dump(welc, f, indent=4)
            return await ctx.send('Welcome messages disabled for this guild.')
        else:
            welc[ctx.message.guild.id]['type'] = True
            await ctx.send('Which channel do you want the welcome messages to be set to? Use a channel mention.')
            channel = await self.bot.wait_for('message', check=pred)
            id = channel.strip('<#').strip('>')
            welc[ctx.message.guild.id]['welcchannel'] = id
            await ctx.send('What do you want the message to be?')
            msg = await self.bot.wait_for('message', check=pred)
            welc[ctx.message.guild.id]['welc'] = msg
            json.dump(welc, f, indent=4)
            await ctx.send('Your welcome message has been successfully set.')

    @commands.command(aliases=['setleave', 'leavemsg', 'leavemessage', 'leaveset'], no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def leave(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('data/welcs.json', 'r+') as f:
            leave = json.load(f)

        if type.lower() in ('n', 'no', 'disabled', 'disabled', 'off'):
            leave[ctx.message.guild.id]['type'] = False
            json.dump(leave, f, indent=4)
        else:
            leave[ctx.message.guild.id]['type'] = True
            await ctx.send('Which channel do you want the leave messages to be set to? Use a channel mention.')
            channel = await self.bot.wait_for('message', check=pred)
            id = channel.strip('<#').strip('>')
            leave[ctx.message.guild.id]['leavechannel'] = id
            await ctx.send('What do you want the message to be?')
            msg = await self.bot.wait_for('message', check=pred)
            leave[ctx.message.guild.id]['leave'] = msg
            json.dump(leave, f, indent=4)
            await ctx.send('Your leave message has been successfully set.')

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
        """Get the current date for a time zone or UTC."""
        now = datetime.datetime.now(tz=pytz.UTC)
        if tz:
            try:
                now = now.astimezone(pytz.timezone(tz))
            except:
                em = discord.Embed(color=discord.Color(value=0xff0000))
                em.title = "Invalid timezone"
                em.description = 'Please take a look at the [list](https://github.com/cree-py/creepy.py/blob/master/data/timezones.json) of timezones.'
                return await ctx.send(embed=em)
        await ctx.send(f'The current date is {now:%A, %B %d, %Y}.')

    @commands.command()
    async def time(self, ctx, tz=None):
        """Get the current time for a timezone or UTC."""
        now = datetime.datetime.now(pytz.UTC)
        if tz:
            try:
                now = now.astimezone(pytz.timezone(tz))
            except:
                em = discord.Embed(color=discord.Color(value=0xff0000))
                em.title = "Invalid timezone"
                em.description = 'Please take a look at the [list](https://github.com/cree-py/creepy.py/blob/master/data/timezones.json) of timezones.'
                return await ctx.send(embed=em)
        await ctx.send(f'It is currently {now:%I:%M:%S %p}.')

    @commands.command()
    async def isitchristmas(self, ctx):
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
    async def isitnewyear(self, ctx):
        '''When is the new year?'''
        now = datetime.datetime.now()
        ny = datetime.datetime(now.year + 1, 1, 1)
        days_until = ny - now
        if now.month == 1 and now.day == 1:
            await ctx.send('It\'s New Years today!')
        else:
            await ctx.send(f'No, there are {days_until.days} days left until New Year\'s.')

    @commands.command()
    async def multiply(self, ctx, a: int, b: int):
        '''Multiply two numbers'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}*{b}`\n✅ Solution: `{a * b}`'
        await ctx.send(embed=em)

    @commands.command()
    async def divide(self, ctx, a: int, b: int):
        '''Divide a number by a number'''
        try:
            em = discord.Embed(color=discord.Color(value=0x00ff00))
            em.title = "Result"
            em.description = f'❓ Problem: `{a}/{b}`\n✅ Solution: `{a / b}`'
            await ctx.send(embed=em)
        except ZeroDivisionError:
            em = discord.Embed(color=discord.Color(value=0x00ff00))
            em.title = "Error"
            em.description = "You can't divide by zero"
            await ctx.send(embed=em)

    @commands.command()
    async def add(self, ctx, a: int, b: int):
        '''Add a number to a number'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}+{b}`\n✅ Solution: `{a + b}`'
        await ctx.send(embed=em)

    @commands.command()
    async def subtract(self, ctx, a: int, b: int):
        '''Substract two numbers'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}-{b}`\n✅ Solution: `{a - b}`'
        await ctx.send(embed=em)

    @commands.command()
    async def remainder(self, ctx, a: int, b: int):
        '''Gets a remainder'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}%{b}`\n✅ Solution: `{a % b}`'
        await ctx.send(embed=em)

    @commands.command()
    async def power(self, ctx, a: int, b: int):
        '''Raise A to the power of B'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}^{b}`\n✅ Solution: `{a ** b}`'
        await ctx.send(embed=em)

    @commands.command()
    async def factorial(self, ctx, a: int):
        '''Factorial something'''
        if a > 813:
            await ctx.send("That number is too high to fit within the message limit for discord.")
        else:
            em = discord.Embed(color=discord.Color(value=0x00ff00))
            em.title = "Result"
            result = 1
            problem = a
            while a > 0:
                result = result * a
                a = a - 1
            em.description = f'❓ Problem: `{problem}!`\n✅ Solution: `{result}`'
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Utility(bot))
