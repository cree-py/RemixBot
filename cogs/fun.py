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

    @commands.command(aliases=['randnum', 'randomnum', 'randnumber'])
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
        if number > 20:
            number = 20
            
        fmt = ''
        for i in range(1, number + 1):
            fmt += f'`Dice {i}: {random.randint(1, 6)}`\n'
            color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color,
                           title='Roll a certain number of dice', description=fmt)
        await ctx.send(embed=em)

    @commands.command(aliases = ['randquote', 'quote'])
    async def randomquote(self, ctx):
        num = random.randint(0, 12)
        quotes = ["*You can do anything, but not everything.*\n—David Allen",
                  "*Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.*\n—Antoine de Saint-Exupéry",
                  "*You miss 100 percent of the shots you never take.*\n—Wayne Gretzky",
                  "*Courage is not the absence of fear, but rather the judgement that something else is more important than fear.*\n—Ambrose Redmoon",
                  "*You must be the change you wish to see in the world.*\n—Gandhi",
                  "*To the man who only has a hammer, everything he encounters begins to look like a nail.*\n—Abraham Maslow",
                  "*We are what we repeatedly do; excellence, then, is not an act but a habit.*\n—Aristotle",
                  "*A wise man gets more use from his enemies than a fool from his friends.*\n—Baltasar Gracian",
                  "*Do not seek to follow in the footsteps of the men of old; seek what they sought.*\n—Basho",
                  "*Everyone is a genius at least once a year. The real geniuses simply have their bright ideas closer together.*\n—Georg Christoph Lichtenberg",
                  "*The real voyage of discovery consists not in seeking new lands but seeing with new eyes.*\n—Marcel Proust",
                  "*Even if you’re on the right track, you’ll get run over if you just sit there.*\n—Will Rogers",
                  "*People often say that motivation doesn’t last. Well, neither does bathing – that’s why we recommend it daily.*\n—Zig Ziglar"]
        quote = quotes[num]
        await ctx.send(quote)
        
    
def setup(bot):
    bot.add_cog(Fun(bot))
