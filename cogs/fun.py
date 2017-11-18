import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def 8ball(self, ctx, question:String):
