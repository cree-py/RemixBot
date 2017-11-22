'''
MIT License

Copyright (c) 2017 Cree-Py

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
import os
import io
import traceback
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands
import json
bot = commands.Bot(command_prefix='c.')

directory = 'cogs.'
cogs = [x.replace('.py', '') for x in os.listdir('cogs') if x.endswith('.py')]

for cog in cogs:
    try:
        bot.load_extension(f'{directory}{cog}')
    except Exception as e:
        print(f'LoadError: {cog}\n'
              f'{type(e).__name__}: {e}')


bot.remove_command('help')


def dev_check(id):
    with open('data/devs.json') as f:
        devs = json.load(f)
    if id in devs:
        return True
    return False


def cleanup_code(content):
    '''Automatically removes code blocks from the code.'''
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')


@bot.event
async def on_ready():
    print("Bot Is Online.")
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | Beta 1.0.1", type=3), afk=True)


@bot.command()
async def help(ctx):
    '''Shows this message'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Help"
    em.description = "A bot under development by Antony, Sleedyak, Victini, Free TNT, and SharpBit. Feel free to drop into the server and help with development and for support [here](https://discord.gg/qv9UcBh)."
    em.add_field(name="Bot", value=f"`{ctx.prefix}eval` Evaluate python code. Developer Command.\n"
                                   f"`{ctx.prefix}help` Shows this message.\n"
                                   f"`{ctx.prefix}invite` Get the invite link for the bot!\n"
                                   f"`{ctx.prefix}ping` Pong! Check the bot's response time.\n"
                                   f"`{ctx.prefix}presence` Change the bot's presence. Developer Command.\n"
                                   f"`{ctx.prefix}restart` Restart the bot. Developer Command.\n"
                                   f"`{ctx.prefix}say` Say something as the bot.")
    em.add_field(name='BS Box Sim',
                 value=f"`{ctx.prefix}boxsim` Simulate a box opening in Brawl Stars.")
    em.add_field(name="Fun", value=f"`{ctx.prefix}dice` Roll a number of dice. Default = 1.\n"
                                   f"`{ctx.prefix}eightball` Ask the 8 ball a question.\n"
                                   f"`{ctx.prefix}flipcoin` Flip a two-sided coin.\n"
                                   f"`{ctx.prefix}lottery` Type 3 numbers between 0 and 5 and try your luck!\n"
                                   f"`{ctx.prefix}randomnumber` Get a random number between a minimum and maximum number.\n"
                                   f"`{ctx.prefix}randomquote` Get a random quote.")
    em.add_field(name="Info", value=f"`{ctx.prefix}serverinfo` See server info.\n"
                                    f"`{ctx.prefix}userinfo` Get user info for a user.")
    em.add_field(name="Mod", value=f"`{ctx.prefix}ban` Ban a user from the guild.\n"
                                   f"`{ctx.prefix}kick` Kick a user from the guild.\n"
                                   f"`{ctx.prefix}mute` Mute someone in a channel.\n"
                                   f"`{ctx.prefix}purge` Delete a number of messages from a guild.\n"
                                   f"`{ctx.prefix}unmute` Unmute someone in a channel where you previously muted them.\n"
                                   f"`{ctx.prefix}warn` Warn someone in a guild through DMs.")
    await bot.get_user(ctx.message.author.id).send(embed=em)
    if ctx.message.channel.guild:
        await ctx.send(f"{ctx.message.author.mention}, I DMed you a list of commands.")
    else:
        pass

@bot.event
async def on_member_join(ctx):
    member = ctx.author
    theserver = bot.get_channel(379363572876181518)
    await theserver.send(f"Welcome {member.mention} to {guild} if you need help ping an online admin or creator have fun")


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)


@bot.command(name='presence')
async def _presence(ctx, type=None, *, game=None):
    '''Change the bot's presence'''
    if not dev_check(ctx.author.id):
        return

    if type is None:
        await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')
    else:
        if type.lower() == 'stream':
            await bot.change_presence(game=discord.Game(name=game, type=1, url='https://www.twitch.tv/a'), status='online')
            await ctx.send(f'Set presence to. `Streaming {game}`')
        elif type.lower() == 'game':
            await bot.change_presence(game=discord.Game(name=game))
            await ctx.send(f'Set presence to `Playing {game}`')
        elif type.lower() == 'watch':
            await bot.change_presence(game=discord.Game(name=game, type=3), afk=True)
            await ctx.send(f'Set presence to `Watching {game}`')
        elif type.lower() == 'listen':
            await bot.change_presence(game=discord.Game(name=game, type=2), afk=True)
            await ctx.send(f'Set presence to `Listening to {game}`')
        elif type.lower() == 'clear':
            await bot.change_presence(game=None)
            await ctx.send('Cleared Presence')
        else:
            await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')


@bot.command(hidden=True, name='eval')
async def _eval(ctx, *, body: str):
    '''Evaluate python code'''

    if not dev_check(ctx.author.id):
        return

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
    '''Invite the bot to your server'''
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=66186303")


@bot.command()
async def say(ctx, *, message: str):
    '''Say something as the bot'''
    await ctx.message.delete()
    await ctx.send(message)


@bot.command()
async def restart(ctx):
    '''Restart the bot'''
    if not dev_check(ctx.author.id):
        return

    await ctx.send("Restarting....")
    await bot.logout()

if __name__ == "__main__":
    if not os.environ.get('TOKEN'):
        print("No token found REEEE!")
    bot.run(os.environ.get('TOKEN').strip('\"'))
