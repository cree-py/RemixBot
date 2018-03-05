import discord
from discord.ext import commands

class Canvas:
    '''Some fun canvas/images commands'''
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def triggered(self, ctx, user: discord.Member=None):
        '''Somebody is triggered'''
        if user is None:
            user = ctx.author
        av = user.avatar_url + "?size=2048" if user.avatar_url.endswith(".gif") else user.avatar_url.replace("webp","png")
        await ctx.send(file=discord.File(await self.bot.api.triggered(av), "triggered.gif"))
        
        
def setup(bot):
    bot.add_cog(Canvas(bot))
        