import discord
import os
import io
import sys
from discord.ext import commands

bot = commands.Bot(command_prefix='c.')
bot.remove_command('help')
developers = [
        311970805342928896,
        316586772349976586,
        292690616285134850
    ]

@bot.event
async def on_ready():
    ctx.send("Bot Is Online")
    await bot.change_presence(game=discord.Game(name="c.help"))
        
@bot.command()
async def help(ctx):
        await ctx.send("```A bot under development by Antony, Sleedyak and Free TNT. Feel free to drop into the server and help with development and for support at https://discord.gg/qv9UcBh.\n\n c.ping : Pong!```")

@bot.command()
async def ping(ctx):
    """Pong! check if bot working"""
    em = discord.Embed(color=2ecc71)
    em.title = "Pong!"
    em.description = "Bot is up and working."
    await ctx.send(embed=em)

if not os.environ.get('TOKEN'):
  print("no token found REEEE!")
bot.run(os.environ.get('TOKEN').strip('\"'))
