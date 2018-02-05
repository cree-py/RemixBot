'''
MIT License

Copyright (c) 2017-2018 Cree-Py

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
from ext import utils
from ext.paginator import PaginatorSession


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
with open('./data/auths.json') as f:
    bot.auth = json.load(f)

dbltoken = load_json('token.json', 'DBLTOKEN')
path = 'cogs.'
extensions = [x.replace('.py', '') for x in os.listdir('cogs.') if x.endswith('.py')]


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
    channel = bot.get_channel(410137178610335744)
    channel1 = message.channel
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Bot log"
    em.description = f"{message.author} wrote a message in {message.guild} in #{message.channel}"
    em.add_field(name="Message: ", value=message.content)
    await channel.send(embed=em)
    if message.content.lower() in ('whatistheprefix', 'what is the prefix'):
        result = await bot.db.config.find_one({'_id': str(message.guild.id)})
    if not result:
        prefix = '-'
    try:
        prefix = result['prefix']
    except KeyError:
        prefix = '-'
    await channel1.send(f'The guild prefix is `{prefix}`')
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
            await g.channels[i].send(f"Hello! Thanks for inviting me to your server. To set a custom prefix, use `-prefix <prefix>`. For more help, use `-help`.")
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

    elif isinstance(error, utils.DeveloperError):
        await ctx.send(error)
    # If any other error occurs, prints to console.


def format_command_help(ctx, cmd):
    '''Format help for a command'''
    color = discord.Color.green()
    em = discord.Embed(color=color, description=cmd.help)

    if hasattr(cmd, 'invoke_without_command') and cmd.invoke_without_command:
        em.title = f'`Usage: {ctx.prefix}{cmd.signature}`'
    else:
        em.title = f'`{ctx.prefix}{cmd.signature}`'

    return em


def format_cog_help(ctx, cog):
    '''Format help for a cog'''
    signatures = []
    color = discord.Color.green()
    em = discord.Embed(color=color, description=f'*{inspect.getdoc(cog)}*')
    em.title = type(cog).__name__.replace('_', ' ')
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
    em.add_field(name='Commands', value=cmds)

    return em


def format_bot_help(ctx):
    signatures = []
    fmt = ''
    commands = []
    for cmd in bot.commands:
        if not cmd.hidden:
            if type(cmd.instance).__name__ == 'NoneType':
                commands.append(cmd)
                signatures.append(len(cmd.name) + len(ctx.prefix))
    max_length = max(signatures)
    abc = sorted(commands, key=lambda x: x.name)
    for c in abc:
        fmt += f'`{ctx.prefix + c.name:<{max_length}} '
        fmt += f'{c.short_doc:<{max_length}}`\n'
    em = discord.Embed(title='Bot', color=discord.Color.green())
    em.description = '*Commands for the main bot.*'
    em.add_field(name='Commands', value=fmt)

    return em


@bot.command()
async def help(ctx, *, command: str=None):
    '''Shows this message'''

    if command is not None:
        aliases = {
            'clash of clans': 'Clash_of_Clans',
            'coc': 'Clash_of_Clans',
            'cr': 'Clash_Royale',
            'Clash Of Clans': 'Clash_of_Clans',
            'utils': 'Utility'
        }

        if command.lower() in aliases.keys():
            command = aliases[command]

        cog = bot.get_cog(command.replace(' ', '_').title())
        cmd = bot.get_command(command)
        if cog is not None:
            em = format_cog_help(ctx, cog)
        elif cmd is not None:
            em = format_command_help(ctx, cmd)
        else:
            await ctx.send('No commands found.')
        return await ctx.send(embed=em)

    pages = []
    for cog in bot.cogs.values():
        em = format_cog_help(ctx, cog)
        pages.append(em)
    em = format_bot_help(ctx)
    pages.append(em)

    p_session = PaginatorSession(ctx, footer=f'Type {ctx.prefix}help command for more info on a command.', pages=pages)
    await p_session.run()


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color.green())
    em.title = "Pong!"
    em.description = f'{bot.latency * 1000:.0f} ms'
    await ctx.send(embed=em)


@bot.command(name='bot')
async def _bot(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=discord.Color.green())
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
    await ctx.send(embed=em)


@bot.command(name='eval', hidden=True)
@utils.developer()
async def _eval(ctx, *, body):
    """Evaluates python code"""
    env = {
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        '_': bot._last_result,
        'source': inspect.getsource,
        'session': bot.session
    }

    env.update(globals())
    body = utils.cleanup_code(body)
    stdout = io.StringIO()
    err = out = None
    to_compile = f'async def func(): \n{textwrap.indent(body, "  ")}'
    try:
        exec(to_compile, env)
    except Exception as e:
        err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        return await ctx.message.add_reaction('\u2049')
    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:
                    out = await ctx.send(f'```py\n{value}\n```')
                except:
                    paginated_text = utils.paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')
        else:
            bot._last_result = ret
            try:
                out = await ctx.send(f'```py\n{value}{ret}\n```')
            except:
                paginated_text = utils.paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = await ctx.send(f'```py\n{page}\n```')
                        break
                    await ctx.send(f'```py\n{page}\n```')
    if out:
        await ctx.message.add_reaction('\u2705')  # tick
    elif err:
        await ctx.message.add_reaction('\u2049')  # x
    else:
        await ctx.message.add_reaction('\u2705')


@bot.command(hidden=True)
@utils.developer()
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
    if cog not in extensions:
        return await ctx.send(f'Cog {cog} does not exist.')
    try:
        bot.unload_extension(f"cogs.{cog}")
        await asyncio.sleep(1)
        load_extension(cog)
    except Exception as e:
        await ctx.send(f"An error occured while reloading {cog}, error details: \n ```{e}```")
    else:
        await ctx.send(f"Reloaded the {cog} cog successfully :white_check_mark:")


@bot.command(hidden=True)
@utils.developer()
async def update(ctx):
    """Pulls from github and updates bot"""
    await ctx.trigger_typing()
    await ctx.send(f"```{subprocess.run('git pull',stdout=subprocess.PIPE).stdout.decode('utf-8')}```")
    for cog in extensions:
        bot.unload_extension(f'{path}{cog}')
    for cog in extensions:
        members = inspect.getmembers(cog)
        for name, member in members:
            if name.startswith('on_'):
                bot.add_listener(member, name)
        try:
            bot.load_extension(f'{path}{cog}')
        except Exception as e:
            await ctx.send(f'LoadError: {cog}\n{type(e).__name__}: {e}')
    await ctx.send('All cogs reloaded :white_check_mark:')


@bot.command()
async def invite(ctx):
    '''Invite the bot to your server'''
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id=384044025298026496&scope=bot&permissions=268905542")


@bot.command(hidden=True)
@utils.developer()
async def shutdown(ctx):
    '''Shut down the bot'''
    await ctx.send("Shutting down....")
    await bot.logout()


if __name__ == "main":
    print('Online.')
else:
    print('GET THE FUCK OUT CODING COPIER AND NOOB XDDDDDD')

# if __name__ == '__main__':
#     bot.run(load_json('token.json', 'TOKEN'))
#     print('Bot is online.')
