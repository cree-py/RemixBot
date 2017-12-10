import discord
import os
import io
import traceback
import textwrap
import inspect
import aiohttp
from contextlib import redirect_stdout
from discord.ext import commands
from dbl import DBLClient
import json


bot = commands.Bot(command_prefix='c.')
dbltoken = "token"
client = DBLClient(token=dbltoken)

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
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | Beta 1.4.0", type=3), afk=True)
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


@bot.event
async def on_member_join(m):
    with open('data/welcs.json') as f:
        welc = json.load(f)
        try:
            type = welc[str(m.guild.id)]['welctype']
        except KeyError:
            return
        if type is False:
            return
        channel = int(welc[str(m.guild.id)]['welcchannel'])
        msg = welc[str(m.guild.id)]['welc']
        await bot.get_channel(channel).send(msg.format(name=m, server=m.guild, mention=m.mention, member=m, membercount=len(m.guild.members)))


@bot.event
async def on_member_remove(m):
    with open('data/welcs.json') as f:
        leave = json.load(f)
        try:
            leave[str(m.guild.id)]['leavetype']
        except KeyError:
            return
        if type is False:
            return
        channel = int(leave[str(m.guild.id)]['leavechannel'])
        msg = leave[str(m.guild.id)]['leave']
        await bot.get_channel(channel).send(msg.format(name=m.name, server=m.guild, membercount=len(m.guild.members)))


@bot.event
async def on_guild_join(g):
    await g.send("Hello! Thanks for inviting me to your server. If you want to enable welcome messages use `c.welcome enable`. For more help, use `c.help`. If you want to suggest anything to be added into the bot use `c.suggest <your suggestion>!")


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
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=268905542")


@bot.command()
async def say(ctx, *, message: str):
    '''Say something as the bot'''
    await ctx.message.delete()
    await ctx.send(message)


@bot.command(hidden=True)
async def shutdown(ctx):
    '''Shut down the bot'''
    if not dev_check(ctx.author.id):
        return

    await ctx.send("Shutting down....")
    await bot.logout()


if __name__ == "__main__":
    if not os.environ.get('TOKEN'):
        print("No token found REEEE!")
    bot.run(os.environ.get('TOKEN').strip('\"'))
