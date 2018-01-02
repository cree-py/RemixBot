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
import aiohttp


class Fun:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lotto'])
    async def lottery(self, ctx, *, guesses):
        '''Enter the lottery and see if you win!'''
        author = ctx.author
        numbers = []
        for x in range(3):
            numbers.append(random.randint(1, 5))

        split = guesses.split(' ')
        if len(split) != 3:
            return await ctx.send('Please separate your numbers with a space, and make sure your numbers are between 0 and 5.')

        string_numbers = [str(i) for i in numbers]
        if split[0] == string_numbers[0] and split[1] == string_numbers[1] and split[2] == string_numbers[2]:
            await ctx.send(f'{author.mention} You won! Congratulations on winning the lottery!')
        else:
            await ctx.send(f"{author.mention} Better luck next time... You were one of the 124/125 who lost the lottery...\nThe numbers were `{', '.join(string_numbers)}`")

    @commands.command(aliases=['cnjoke'])
    async def chucknorris(self, ctx):
        '''Facts about Chuck Norris.'''
        url = "http://api.icndb.com/jokes/random"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                await ctx.send(data['value']['joke'])

    @commands.command(aliases=['xkcd', 'comic'])
    async def randomcomic(self, ctx):
        '''Get a comic from xkcd.'''
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/info.0.json') as resp:
                data = await resp.json()
                currentcomic = data['num']
        rand = random.randint(0, currentcomic)  # max = current comic
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/{rand}/info.0.json') as resp:
                data = await resp.json()
                em = discord.Embed(color=discord.Color(value=0x00ff00))
                em.title = f"XKCD Number {data['num']}- \"{data['title']}\""
                em.set_footer(text=f"Published on {data['month']}/{data['day']}/{data['year']}")
                em.set_image(url=data['img'])
                await ctx.send(embed=em)

    @commands.command(aliases=['cat'])
    async def randomcat(self, ctx):
        '''Meow.'''
        async with aiohttp.ClientSession() as session:
            async with session.get('http://random.cat/meow') as resp:
                data = await resp.json()
                em = discord.Embed(color=discord.Color(value=0x00ff00))
                em.title = "Here's your cat!"
                em.set_footer(text="Powered by random.cat")
                em.set_image(url=data['file'])
                await ctx.send(embed=em)

    @commands.command(aliases=['number'])
    async def numberfact(self, ctx, *, number: int):
        '''Get a fact about a number. Usage: {p}numberfact <number>.'''
        if not number:
            await ctx.send(f'Usage: `{ctx.prefix}numberfact <number>`')
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://numbersapi.com/{number}?json') as resp:
                    file = await resp.json()
                    fact = file['text']
                    await ctx.send(f"**Did you know?**\n*{fact}*")
        except:
            await ctx.send("No facts are available for that number.")

    @commands.command()
    async def mathfact(self, ctx, number: int):
        '''Get a math fact about a number. Usage: {p}mathfact <number>.'''
        if not number:
            await ctx.send(f'Usage: `{ctx.prefix}mathfact <number>`')
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://numbersapi.com/{number}/math?json') as resp:
                    file = await resp.json()
                    fact = file['text']
                    await ctx.send(f"**Did you know?**\n*{fact}*")
        except:
            await ctx.send("No facts are available for that number.")

    @commands.command(aliases=['trump', 'trumpquote'])
    async def asktrump(self, ctx, question):
        '''Ask Donald Trump a question! Usage: {p}asktrump <yourquestion>'''
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q={question}') as resp:
                file = await resp.json()
                quote = file['message']
                em = discord.Embed(color=discord.Color(value=0x00ff00))
                em.title = "What does Trump say?"
                em.description = quote
                em.set_footer(text="Made possible by whatdoestrumpthink.com", icon_url="http://www.stickpng.com/assets/images/5841c17aa6515b1e0ad75aa1.png")
                await ctx.send(embed=em)

    @commands.command(aliases=['dog'])
    async def randomdog(self, ctx):
        '''Woof.'''
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as resp:
                file = await resp.json()
                img = file['message']
                em = discord.Embed(color=discord.Color(value=0x00ff00))
                em.title = "Here's your dog!"
                em.set_footer(text="Powered by dog.ceo")
                em.set_image(url=img)
                await ctx.send(embed=em)

    @commands.command(aliases=['joke'])
    async def badjoke(self, ctx):
        '''Get a bad joke.'''
        async with aiohttp.ClientSession() as session:
            async with session.get('https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke') as resp:
                data = await resp.json()
                em = discord.Embed(color=discord.Color(value=0x00ff00))
                em.title = data['setup']
                em.description = data['punchline']
                await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Fun(bot))
