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
from contextlib import redirect_stdout
from discord.ext import commands
import json


bot = commands.Bot(command_prefix='c.')
dbltoken = "token"
directory = 'cogs'
cogs = [x.replace('.y', '') for x in os.listdir('cogs') if x.endswith('.y')]


for cog in cogs:
    members = inspect.getmembers(cog)
    for name, member in members:
        if name.startswith('on'):
            bot.add_listener(member, name)
    try:
        bot.load_cog(f'path{cog}')
    except Exception as e:
        print(f'LoadError: {cog}\n'
              f'{type(e).__name__}: {e}')


bot.remove_command('help')
version = "Beta 1.5.0"


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
async def onready():
    print("Bot Is Online.")
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | {version}", type=3), afk=True)
    bot._last_result = None
    bot.session = aiohttp.ClientSession()


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
            await g.channels[i].send("Hello! Thanks for inviting me to your server. If you want to enable welcome messages use `c.welcome enable`. For more help, use c.help. If you want to suggest anything to be added into the bot use `c.suggest <your suggestion>!`")
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
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | {version}", type=3), afk=True)


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
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | {version}", type=3), afk=True)


@bot.command()
async def help(ctx):
    '''Shows this message'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Help"
    em.description = "A bot under development by Antony, Sleedyak, Victini, Free TNT, and SharpBit. Feel free to drop into the server and help with development and for support [here](https://discord.gg/RzsYQ9f).\n\n"
    for cog in bot.cogs.values():
        cc = []
        for cmd in bot.commands:
            if not cmd.hidden:
                if cmd.instance is cog:
                    cc.append(cmd)
        abc = sorted(cc, key=lambda x: x.name)
        cmds = ''
        for c in abc:
            cmds += f'`{ctx.prefix}{c.name}:\t{c.short_doc}`\n'
        em.add_field(name=type(cog).__name__.replace('_', ' '), value=cmds)
    none = ''
    nonec = []
    for c in bot.commands:
        if not c.hidden:
            if type(c.instance).__name__ == 'NoneType':
                nonec.append(c)
    abc = sorted(nonec, key=lambda x: x.name)
    for c in abc:
        none += f'`{ctx.prefix}{c.name}:\t{c.short_doc}`\n'
    em.add_field(name='Bot', value=none)
    await bot.get_user(ctx.message.author.id).send(embed=em)
    if ctx.message.channel.guild:
        await ctx.send(f"{ctx.message.author.mention}, I DMed you a list of commands.")


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)


@bot.command(aliases=['bot', 'about'])
async def info(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Bot Info"
    em.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    em.description = "A multipurpose bot made by AntonyJoseph03, Free TNT, SharpBit, Sleedyak and Victini.\nNote: The GitHub repo is currently private because of recent plagiarism cases.\n[Support Server](https://discord.gg/RzsYQ9f)"
    em.add_field(name="Servers", value=len(bot.guilds))
    em.add_field(name="Total Users", value=f'{len({m.id for m in bot.get_all_members() if m.status is not discord.Status.offline})}/{len(bot.users)} online')
    em.add_field(name='Channels', value=f"{sum(1 for g in bot.guilds for _ in g.channels)}")
    em.add_field(name="Library", value=f"discord.py")
    em.add_field(name="Bot Latency", value=f"{bot.ws.latency * 1000:.3f} ms")
    em.add_field(name="Invite", value=f"[Click Here](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=268905542)")
    em.add_field(name="Upvote this bot!", value=f"https://discordbots.org/bot/{bot.user.id} :reminder_ribbon:", inline=False)

    em.set_footer(text="CreeperBot | Powered by discord.py")
    await ctx.send(embed=em)


@bot.command(name='presence', hidden=True)
async def _presence(ctx, type=None, *, game=None):
    '''Change the bot's presence'''
    if not dev_check(ctx.author.id):
        return

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


@bot.command()
async def suggest(ctx, *, idea: str):
    """Suggest an idea. The idea will be sent to developer server"""
    suggest = bot.get_channel(384111952798154752)
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = f"{ctx.author} | User ID: {ctx.author.id}"
    em.description = idea
    em.set_footer(text=f"From {ctx.author.guild} | Server ID: {ctx.author.guild.id}", icon_url=ctx.guild.icon_url)
    await suggest.send(embed=em)
    await ctx.send("Your idea has been successfully sent to support server. Thank you!")


@bot.command(name='eval')
async def _eval(ctx, *, body):
    """Evaluates python code"""
    if not dev_check(ctx.author.id):
        return await ctx.send("You cannot use this because you are not a developer.")
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

    body = cleanup_code(body)
    stdout = io.StringIO()
    err = out = None

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

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
                    paginated_text = paginate(value)
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
                paginated_text = paginate(f"{value}{ret}")
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


@bot.command()
async def invite(ctx):
    '''Invite the bot to your server'''
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id=384044025298026496&scope=bot&permissions=268905542")


@bot.command()
async def say(ctx, *, message: str):
    '''Say something as the bot'''
    await ctx.message.delete()
    await ctx.send(message)


@bot.command(hidden=True)
async def shutdown(ctx):
    '''Shut down the bot'''
    if not dev_check(ctx.author.id):
        return await ctx.send("You can't use this command because you are not a CreeperBot developer!")

    await ctx.send("Shutting down....")
    await bot.logout()


if __name__ == "main":
    print('Online.')
else:
    print('GET THE FUCK OUT CODING COPIER AND NOOB XDDDDDD')
