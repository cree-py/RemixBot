import discord
from discord.ext import commands
import idioticapi
import os


class Canvas:
    '''Some fun canvas/images commands'''

    def __init__(self, bot):
        self.bot = bot
        # self.api = idioticapi.Client(token=bot.auth.get("idioticapi"), dev=True)
        self.api = idioticapi.Client(token=os.environ.get('idiotickey'), dev=True)

    def format_avatar(self, avatar_url):
        if avatar_url.endswith(".gif"):
            return avatar_url + "?size=2048"
        return avatar_url.replace("webp", "png")

    @commands.command()
    async def triggered(self, ctx, user: discord.Member=None):
        '''Somebody is triggered'''
        if user is None:
            user = ctx.author
        await ctx.send(file=discord.File(await self.api.triggered(self.format_avatar(user.avatar_url)), "triggered.gif"))

    @commands.command()
    async def blame(self, ctx, text):
        '''Blame someone'''
        await ctx.send(file=discord.File(await self.api.blame(text), "blame.png"))


def setup(bot):
    bot.add_cog(Canvas(bot))
