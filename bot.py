import discord
import os
import io
import sys
import traceback
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='c.')
bot.load_extension("cogs.mod")    
bot.remove_command('help')

developers = [
    311970805342928896,
    316586772349976586,
    292690616285134850,
    307133814834987008
]

def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')

@bot.event
async def on_ready():
   print("Bot Is Online")


@bot.command()
async def help(ctx):
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Help"
    em.description = "A bot under development by Antony, Sleedyak, Victini and Free TNT. Feel free to drop into the server and help with development and for support [here](https://discord.gg/qv9UcBh)"
    em.add_field(name="Ping", value="Pong!")
    em.add_field(name="Invite", value="Invite me to your server.")
    em.add_field(name="Kick", value="Kick someone from the server.")
    em.add_field(name="Ban", value="Ban someone from the server.")
    em.add_field(name="Mute", value="Mutes someone from a specified channel. Requires the ban members permission")
    em.add_field(name="Unmute",value="Unmute someone you previously muted. Requires the ban members permission")
    em.add_field(name="Say",value="Say something as the bot.") 
    em.add_field(name="Warn", value="Warn a user. Usage : c.warn @user reason here")
    em.add_field(name="Help", value="Shows this message.")
    await bot.get_user(ctx.message.author.id).send(embed=em)
    if ctx.message.channel.guild:
        await ctx.send("{}, I DMed you a list of commands.".format(ctx.message.author.mention))
    else:
        pass

@bot.command()
async def ping(ctx):
    """Pong! Check if bot is working"""
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)

@bot.command(name='presence')
async def set(ctx, Type=None,*,thing=None):
  if ctx.author.id not in developers:
      return

  if Type is None:
    await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')
  else:
    if Type.lower() == 'stream':
      await bot.change_presence(game=discord.Game(name=thing,type=1,url='https://www.twitch.tv/a'),status='online')
      await ctx.send(f'Set presence to. `Streaming {thing}`')
    elif Type.lower() == 'game':
      await bot.change_presence(game=discord.Game(name=thing))
      await ctx.send(f'Set presence to `Playing {thing}`')
    elif Type.lower() == 'watch':
      await bot.change_presence(game=discord.Game(name=thing, type=3), afk=True)
      await ctx.send(f'Set presence to `Watching {thing}`')
    elif Type.lower() == 'listen':
      await bot.change_presence(game=discord.Game(name=thing, type=2), afk=True)
      await ctx.send(f'Set presence to `Listening to {thing}`')
    elif Type.lower() == 'clear':
      await bot.change_presence(game=None)
      await ctx.send('Cleared Presence')
    else:
      await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')


@bot.command(pass_context=True, hidden=True, name='eval')
async def _eval(ctx, *, body: str):
    
        if ctx.author.id not in developers: return

        env = {
            'bot': bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
        }

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                await ctx.send(f'```py\n{value}{ret}\n```')


@bot.command()
async def invite(ctx):
    await ctx.send("Invite me to your server: https://discordapp.com/oauth2/authorize?client_id=364372021422981120&scope=bot&permissions=66186303")

@bot.command()
async def say(ctx, *, message:str):
    """Say something as the bot"""
    await ctx.send(message)

 
if not os.environ.get('TOKEN'):
  print("no token found REEEE!")
bot.run(os.environ.get('TOKEN').strip('\"'))
