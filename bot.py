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
import inspect
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import redirect_stdout
from discord.ext import commands
import json
import subprocess
import asyncio
from ext.utils import developer


def load_json(path, key):
    with open(f'./data/{path}') as f:
        config = json.load(f)
    return config.get(key)


mongo = AsyncIOMotorClient(load_json('auths.json', 'MONGODB'))


async def get_pre(bot, message):
    '''Gets the prefix for the guild'''
    if not message.guild:
        return '-'
    result = await bot.db.config.find_one({'_id': str(message.guild.id)})
    if not result:
        return '-'
    try:
        return result['prefix']
    except KeyError:
        return '-'


bot = commands.Bot(command_prefix=get_pre)
bot.db = mongo.RemixBot
dbltoken = load_json('token.json', 'DBLTOKEN')
path = 'cogs'
extensions = [x.replace('.py', '') for x in os.listdir('cogs') if x.endswith('.py')]


def load_extension(cog, path='cogs.'):
    members = inspect.getmembers(cog)
    for name, member in members:
        if name.startswith('on_'):
            bot.add_listener(member, name)
    try:
        bot.load_extension(f'{path}{cog}')
    except Exception as e:
        print(f'LoadError: {cog}\n{type(e).__name__}: {e}')


def load_extensions(cogs, path='cogs.'):
    for cog in cogs:
        members = inspect.getmembers(cog)
        for name, member in members:
            if name.startswith('on_'):
                bot.add_listener(member, name)
        try:
            bot.load_extension(f'{path}{cog}')
        except Exception as e:
            print(f'LoadError: {cog}\n{type(e).__name__}: {e}')


load_extensions(extensions)


bot.remove_command('help')
version = "v2.0.0"


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | -help | {version}", type=3), afk=True)

    url = f"https://discordbots.org/api/bots/{bot.user.id}/stats"
    headers = {
        'Authorization': dbltoken,
        'content-type': 'application/json'
    }
    payload = {
        'server_count': len(bot.guilds)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as dblpost:
            print(dblpost.status)

    bot._last_result = None
    bot.session = aiohttp.ClientSession()

    print('Bot is Online.')


@bot.event
async def on_message(message):
    channel = message.channel

    if message.content.lower() in ('whatistheprefix', 'what is the prefix'):
        result = await bot.db.config.find_one({'_id': str(message.guild.id)})
        if not result:
            prefix = '-'
        try:
            prefix = result['prefix']
        except KeyError:
            prefix = '-'
        await channel.send(f'The guild prefix is `{prefix}`')

    await bot.process_commands(message)


# Listener for :pushpin: command
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "\U0001f4cc":
        await user.send(f"Here's the message you pinned :pushpin: ```{reaction.message.author.name}: {reaction.message.content}```")


@bot.event
async def on_guild_join(g):
    success = False
    i = 0
    while not success:
        try:
            await g.channels[i].send(f"Hello! Thanks for inviting me to your server. To set a custom prefix, use `-prefix <prefix>`. For more help, use -help. If you want to suggest anything to be added into the bot use `-suggest <your suggestion>!`")
        except (discord.Forbidden, AttributeError):
            i += 1
        except IndexError:
            # if the server has no channels, doesn't let the bot talk, or all vc/categories
            pass
        else:
            success = True

    url = f"https://discordbots.org/api/bots/{bot.user.id}/stats"
    headers = {
        'Authorization': dbltoken,
        'content-type': 'application/json'
    }
    payload = {
        'server_count': len(bot.guilds)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as dblpost:
            print(dblpost.status)

    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | -help | {version}", type=3), afk=True)


@bot.event
async def on_guild_remove(g):
    url = f"https://discordbots.org/api/bots/{bot.user.id}/stats"
    headers = {
        'Authorization': dbltoken,
        'content-type': 'application/json'
    }
    payload = {
        'server_count': len(bot.guilds)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as dblpost:
            print(dblpost.status)

    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | -help | {version}", type=3), afk=True)


async def send_cmd_help(ctx):
    cmd = ctx.command
    em = discord.Embed(title=f'Usage: {ctx.prefix + cmd.signature}')
    em.color = discord.Color.green()
    em.description = cmd.help
    return em


@bot.event
async def on_command_error(ctx, error):

    send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

    if isinstance(error, commands.CommandNotFound):  # fails silently
        pass

    elif isinstance(error, send_help):
        _help = await send_cmd_help(ctx)
        await ctx.send(embed=_help)

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have the permissions to use this command.')
    # If any other error occurs, prints to console.


def format_command_help(ctx, cmd):
    color = discord.Color(value=0x00ff00)
    em = discord.Embed(color=color, description=cmd.help)

    if hasattr(cmd, 'invoke_without_command') and cmd.invoke_without_command:
        em.title = f'`Usage: {ctx.prefix}{cmd.signature}`'
    else:
        em.title = f'`{ctx.prefix}{cmd.signature}`'

    return em


@bot.command()
async def help(ctx, *, command: str=None):
    '''Shows this message'''

    await ctx.trigger_typing()

    if command is not None:
        cmd = bot.get_command(command)
        if cmd is not None:
            em = format_command_help(ctx, cmd)
        return await ctx.send(embed=em)

    signatures = []
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Help"
    em.description = "A bot created by the cree-py organization. Feel free to drop into the server and help with development and support [here](https://discord.gg/RzsYQ9f).\n\n"

    for cog in bot.cogs.values():
        cc = []
        for cmd in bot.commands:
            if not cmd.hidden:
                if cmd.instance is cog:
                    cc.append(cmd)
                    signatures.append(len(cmd.name) + len(ctx.prefix))
        max_length = max(signatures)
        abc = sorted(cc, key=lambda x: x.name)
        cmds = ''
        for c in abc:
            cmds += f'`{ctx.prefix + c.name:<{max_length}} '
            cmds += f'{c.short_doc:<{max_length}}`\n'
        em.add_field(name=type(cog).__name__.replace('_', ' '), value=cmds)
    none = ''
    nonec = []
    for c in bot.commands:
        if not c.hidden:
            if type(c.instance).__name__ == 'none':
                nonec.append(c)
                signatures.append(len(cmd.name) + len(ctx.prefix))
    abc = sorted(nonec, key=lambda x: x.name)
    for c in abc:
        none += f'`{ctx.prefix + c.name:<{max_length}} '
        none += f'{c.short_doc:<{max_length}}`\n'
    em.add_field(name='Bot', value=none)


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.latency * 1000:} s'


@bot.command(name='bot')
async def _bot(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Bot Info"
    em.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    em.description = "A multipurpose bot made by AntonyJoseph03, Free TNT, SharpBit, Sleedyak and Victini.\n[Support Server](https://discord.gg/RzsYQ9f)"
    em.add_field(name="Servers", value=len(bot.guilds))
    em.add_field(name="Online Users", value=str(len({m.id for m in bot.get_all_members() if m.status is not discord.Status.offline})))
    em.add_field(name='Total Users', value=len(bot.users))
    em.add_field(name='Channels', value=f"{sum(1 for g in bot.guilds for _ in g.channels)}")
    em.add_field(name="Library", value=f"discord.py")
    em.add_field(name="Bot Latency", value=f"{bot.ws.latency * 1000:.3f} ms")
    em.add_field(name="Invite", value=f"[Click Here](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=268905542)")
    em.add_field(name='GitHub', value='[Click here](https://github.com/cree-py/creepy.py)')
    em.add_field(name="Upvote this bot!", value=f"[Click here](https://discordbots.org/bot/{bot.user.id}) :reminder_ribbon:")

    em.set_footer(text="RemixBot | Powered by discord.py")


@bot.command(name='presence', hidden=True)
@developer()
async def _presence(ctx, type=None, *, game=None):
    '''Change the bot's presence'''

    if type is None:
        await ctx.send(f'Usage: `{ctx.prefix}presence [game/stream/watch/listen] [message]`')
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


@bot.command(hidden=True)
@developer()
async def reload(ctx, cog):
    """Reloads a cog"""
    if cog.lower() == 'all':
        for cog in extensions:
            try:
                bot.unload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.send(f"An error occured while reloading {cog}, error details: \n ```{e}```")
        load_extensions(extensions)
        return await ctx.send('All cogs updated successfully :white_check_mark:')
    try:
        bot.unload_extension(f"cogs.{cog}")
        await asyncio.sleep(1)
        bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"Reloaded the {cog} cog successfully :white_check_mark:")
    except Exception as e:
        await ctx.send(f"An error occured while reloading {cog}, error details: \n ```{e}```")


@bot.command(hidden=True)
@developer()
async def update(ctx):
    """Pulls from github and updates bot"""
    await ctx.send(f"```{subprocess.run('git pull',stdout=subprocess.PIPE).stdout.decode('utf-8')}```")
    for cog in extensions:
        bot.unload_extension(f'{path}{cog}')
        bot.load_extension(f'{path}{cog}')
    await ctx.send('All cogs reloaded :white_check_mark:')


@bot.command()
async def invite(ctx):
    '''Invite the bot to your server'''
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id=384044025298026496&scope=bot&permissions=268905542")


@bot.command(hidden=True)
@developer()
async def shutdown(ctx):
    '''Shut down the bot'''
    await ctx.send("Shutting down....")
    await bot.logout()


if __name__ == "main":
    print('Online.')
else:
    print('GET THE FUCK OUT CODING COPIER AND NOOB XDDDDDD')
