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
import random
from discord.ext import commands
import urbandictionary as ud
import json
import datetime
import pytz
import wikipedia


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

    @commands.command(aliases=['urban'])
    async def ud(self, ctx, *, query):
        '''Search terms with urbandictionary.com'''
        em = discord.Embed(title=f'{query}', color=0x00ff00)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_footer(text='Powered by urbandictionary.com')
        defs = ud.define(query)
        try:
            res = defs[0]
        except IndexError:
            em.description = 'No results.'
            return await ctx.send(embed=em)
        em.description = f'**Definition:** {res.definition}\n**Usage:** {res.example}\n**Votes:** {res.upvotes}:thumbsup:{res.downvotes}:thumbsdown:'
        await ctx.send(embed=em)

    @commands.command(aliases=['wikipedia'])
    async def wiki(self, ctx, *, query):
        '''Search up something on wikipedia'''
        em = discord.Embed(title=str(query), color=0x00ff00)
        em.set_footer(text='Powered by wikipedia.org')
        try:
            result = wikipedia.summary(query)
            em.description = result
            await ctx.send(embed=em)
        except wikipedia.exceptions.PageError as e:
            em.color = 0xff0000
            await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def isit(self, ctx):
        '''A command group to see the number of days until a holiday'''
        await ctx.send('`c.isit halloween` Find the number of days until this spooky holiday!\n`c.isit christmas` Are you naughty or nice?\n`c.isit newyear` When is next year coming already?')

    @isit.command()
    async def halloween(self, ctx):
        now = datetime.datetime.now()
        h = datetime.datetime(now.year, 10, 31)
        if now.month > 10:
            h = datetime.datetime(now.year + 1, 10, 31)
        until = h - now
        if now.month == 10 and now.day == 31:
            await ctx.send('It is Halloween! :jack_o_lantern: :ghost:')
        else:
            await ctx.send(f'No, there are {until.days + 1} more days until Halloween.')

    @isit.command()
    async def christmas(self, ctx):
        '''Is it Christmas?'''
        now = datetime.datetime.now()
        c = datetime.datetime(now.year, 12, 25)
        if now.month == 12 and now.day > 25:
            c = datetime.datetime((now.year + 1), 12, 25)
        until = c - now
        if now.month == 12 and now.day == 25:
            await ctx.send('Merry Christmas! :christmas_tree: :snowman2:')
        else:
            await ctx.send(f'No, there are {until.days + 1} more days until Christmas.')

    @isit.command()
    async def newyear(self, ctx):
        '''When is the new year?'''
        now = datetime.datetime.now()
        ny = datetime.datetime(now.year + 1, 1, 1)
        until = ny - now
        if now.month == 1 and now.day == 1:
            await ctx.send('It\'s New Years today! :tada:')
        else:
            await ctx.send(f'No, there are {until.days + 1} days left until New Year\'s.')

    @commands.group(invoke_without_command=True)
    async def math(self, ctx):
        '''A command group for math commands'''
        await ctx.send('Available commands:\n`add <a> <b>`\n`subtract <a> <b>`\n`multiply <a> <b>`\n`divide <a> <b>`\n`remainder <a> <b>`\n`power <a> <b>`\n`factorial <a>`')

    @math.command(aliases=['*', 'x'])
    async def multiply(self, ctx, a: int, b: int):
        '''Multiply two numbers'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}*{b}`\n✅ Solution: `{a * b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['/', '÷'])
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

    @math.command(aliases=['+'])
    async def add(self, ctx, a: int, b: int):
        '''Add a number to a number'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}+{b}`\n✅ Solution: `{a + b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['-'])
    async def subtract(self, ctx, a: int, b: int):
        '''Substract two numbers'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}-{b}`\n✅ Solution: `{a - b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['%'])
    async def remainder(self, ctx, a: int, b: int):
        '''Gets a remainder'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}%{b}`\n✅ Solution: `{a % b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['^', '**'])
    async def power(self, ctx, a: int, b: int):
        '''Raise A to the power of B'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        em.title = "Result"
        em.description = f'❓ Problem: `{a}^{b}`\n✅ Solution: `{a ** b}`'
        await ctx.send(embed=em)

    @math.command(aliases=['!'])
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
