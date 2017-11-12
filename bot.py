import discord
import os
import io
import sys
from discord.ext import commands

bot = commands.Bot(command_prefix='c.',description="A Bot Made By AntonyJosph Free TNT And Sleedyak Under Work",owner_id=311970805342928896,292690616285134850,316586772349976586)

@bot.event
async def on_ready():
    ctx.send("Bot Is Online")
    

if not os.environ.get('TOKEN'):
  print("no token found REEEE!")
bot.run(os.environ.get('TOKEN').strip('\"'))
