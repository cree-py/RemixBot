'''
MIT License

Copyright (c) 2017-2018 Cree-Py

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
from discord.ext.commands.cooldowns import BucketType
import random
import aiohttp
import json


class Misc:
    '''Miscellaneous and fun commands.'''

    def __init__(self, bot):
        self.bot = bot
        with open('./data/token.json') as f:
            config = json.load(f)
            self.dbltoken = config.get('DBLTOKEN')
        self.base_url = 'https://discordbots.org/api/bots/'

    async def upvoted(self, id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.base_url}{self.bot.user.id}/votes', headers={'Authorization': self.dbltoken}) as resp:
                data = await resp.json()
        for user in data:
            if id == int(user['id']):
                return True
        return False

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def say(self, ctx, *, message: str):
        '''Say something as the bot'''
        voted = await self.upvoted(ctx.author.id)
        if not voted:
            return await ctx.send('To use this command, you must upvote RemixBot on [DBL](https://discordbots.org/bot/384044025298026496)!')
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(message)

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str):
        '''Ask the 8 ball a question'''
        if not question.endswith('?'):
            return await ctx.send('Please ask a question.')

        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
                     "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
                     "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
                     "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
                     "Very doubtful"]

        num = random.randint(0, len(responses) - 1)
        if num < 10:
            em = discord.Embed(color=discord.Color.green())
        elif num < 15:
            em = discord.Embed(color=discord.Color(value=0xffff00))
        else:
            em = discord.Embed(color=discord.Color.red())

        response = responses[num]

        em.title = f"🎱{question}"
        em.description = response
        await ctx.send(embed=em)

    @commands.command(aliases=['coin'])
    async def flipcoin(self, ctx):
        '''Flips a coin'''
        choices = ['You got Heads', 'You got Tails']
        color = discord.Color.green()
        em = discord.Embed(color=color, title='Coinflip:', description=random.choice(choices))
        await ctx.send(embed=em)

    @commands.command()
    async def dice(self, ctx, number=1):
        '''Rolls a certain number of dice'''
        if number > 20:
            number = 20

        fmt = ''
        for i in range(1, number + 1):
            fmt += f'`Dice {i}: {random.randint(1, 6)}`\n'
            color = discord.Color.green()
        em = discord.Embed(color=color, title='Roll a certain number of dice', description=fmt)
        await ctx.send(embed=em)

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
        em = discord.Embed(color=discord.Color.green())
        em.title = f"XKCD Number {data['num']}- \"{data['title']}\""
        em.set_footer(text=f"Published on {data['month']}/{data['day']}/{data['year']}")
        em.set_image(url=data['img'])
        await ctx.send(embed=em)

    @commands.command(aliases=['number'])
    async def numberfact(self, ctx, number: int):
        '''Get a fact about a number.'''
        if not number:
            await ctx.send(f'Usage: `{ctx.prefix}numberfact <number>`')
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://numbersapi.com/{number}?json') as resp:
                    file = await resp.json()
                    fact = file['text']
                    await ctx.send(f"**Did you know?**\n*{fact}*")
        except KeyError:
            await ctx.send("No facts are available for that number.")

    @commands.command(aliases=['trump', 'trumpquote'])
    async def asktrump(self, ctx, *, question):
        '''Ask Donald Trump a question!'''
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q={question}') as resp:
                file = await resp.json()
        quote = file['message']
        em = discord.Embed(color=discord.Color.green())
        em.title = "What does Trump say?"
        em.description = quote
        em.set_footer(text="Made possible by whatdoestrumpthink.com", icon_url="http://www.stickpng.com/assets/images/5841c17aa6515b1e0ad75aa1.png")
        await ctx.send(embed=em)

    @commands.command(aliases=['joke'])
    async def badjoke(self, ctx):
        '''Get a bad joke.'''
        async with aiohttp.ClientSession() as session:
            async with session.get('https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke') as resp:
                data = await resp.json()
        em = discord.Embed(color=discord.Color.green())
        em.title = data['setup']
        em.description = data['punchline']
        await ctx.send(embed=em)

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
    bot.add_cog(Misc(bot))
