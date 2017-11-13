import discord
import os
import io
import sys
import traceback
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands

bot = commands.Bot(command_prefix='c.')
bot.remove_command('help')
    
developers = [
    311970805342928896,
    316586772349976586,
    292690616285134850
]

def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')

@bot.event
async def on_ready():
   ctx.send("Bot Is Online")


@bot.command()
async def help(ctx):
    em = discord.Embed(color=discord.Color(value=2ecc71))
    em.title = "Help"
    em.description = "A bot under development by Antony, Sleedyak and Free TNT. Feel free to drop into the server and help with development and for support at [here](https://discord.gg/qv9UcBh) \n"
    em.add_field(name="Ping", value="Pong! check if bot is working")
    em.add_field(name="Invite", value="Invite me to your server")
    await ctx.send(embed=em)

@bot.command()
async def ping(ctx):
    """Pong! Check if bot is working"""
    em = discord.Embed()
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)

@bot.command(name='presence')
async def set(ctx, Type=None,*,thing=None):
  if ctx.author.id not in developers:
      return

  if Type is None:
    await ctx.send('Usage: `.presence [game/stream] [message]`')
  else:
    if Type.lower() == 'stream':
      await bot.change_presence(game=discord.Game(name=thing,type=1,url='https://www.twitch.tv/a'),status='online')
      await ctx.send(f'Set presence to. `Streaming {thing}`')
    elif Type.lower() == 'game':
      await bot.change_presence(game=discord.Game(name=thing))
      await ctx.send(f'Set presence to `Playing {thing}`')
    elif Type.lower() == 'clear':
      await bot.change_presence(game=None)
      await ctx.send('Cleared Presence')
    else:
      await ctx.send('Usage: `.presence [game/stream] [message]`')

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



 
if not os.environ.get('TOKEN'):
  print("no token found REEEE!")
bot.run(os.environ.get('TOKEN').strip('\"'))
