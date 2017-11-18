import discord
import random
from discord.ext import commands


class Fun:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str):
        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
                     "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
                     "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
                     "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
                     "Very doubtful"]

        num = random.randint(0, 19)
        if num < 10:
            em = discord.Embed(color=discord.Color(value=0x00ff00))
        elif num < 15:
            em = discord.Embed(color=discord.Color(value=0xffff00))
        else:
            em = discord.Embed(color=discord.Color(value=0xff0000))

        response = responses[num]

        em.title = "🎱" + question
        em.description = response
        await ctx.send(embed=em)

    @commands.command()
    async def randomnumber(self, ctx):
        await ctx.send('Your random number is: {random.randint(101)}')

    @commands.command(aliases=['coin'])
    async def flipcoin(self, ctx):
        '''Flips a coin'''
        choices = ['You got Heads', 'You got Tails']
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color,
                           title='Coinflip:', description=random.choice(choices))
        await ctx.send(embed=em)

    @commands.command()
    async def dice(self, ctx, number=1):
        '''Rolls a certain number of dice'''
        fmt = ''
        for i in range(1, number + 1):
            fmt += f'`Dice {i}: {random.randint(1, 6)}`\n'
            color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color,
                           title='Roll a certain number of dice', description=fmt)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Fun(bot))
