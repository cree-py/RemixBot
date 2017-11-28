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
    em.description = "A bot under development by Antony, Sleedyak, Victini, Free TNT, and SharpBit. Feel free to drop into the server and help with development and for support [here](https://discord.gg/RzsYQ9f).\n\n"
    commands = sorted(bot.commands, key=lambda x: x.name)
    for command in commands:
        em.description += f'`{ctx.prefix}{command.name}`:\t{command.short_doc}.\n'
    await bot.get_user(ctx.message.author.id).send(embed=em)
    if ctx.message.channel.guild:
        await ctx.send(f"{ctx.message.author.mention}, I DMed you a list of commands.")
    else:
        pass


@bot.event
async def on_member_join(member):
    '''Welcome message'''
    server = bot.get_guild(384102150109659137)
    general_channel = bot.get_channel(384102150567100419)
    if member.guild.id != server:
        return

    await general_channel.send(f"{member.mention}, welcome to {server.name}! If you need help ping an online admin or creator.")


@bot.command()
async def ping(ctx):
    '''Pong! Get the bot's response time'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)


@bot.command()
async def source(self, ctx, *, command):
    '''See the source code for any command.'''
    if not dev_check(ctx.author.id):
        return

    source = str(inspect.getsource(bot.get_command(command).callback))
    fmt = '```py\n' + source.replace('`', '\u200b`') + '\n```'
    if len(fmt) > 2000:
        async with ctx.session.post("https://hastebin.com/documents", data=source) as resp:
            data = await resp.json()
        key = data['key']
        return await ctx.send(f'Command source: <https://hastebin.com/{key}.py>')
    else:
        return await ctx.send(fmt)


@bot.command(name='presence')
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
    """Suggest an idea, idea will be sent to developer server"""
    server = bot.get_channel(384111952798154752)
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = f"{ctx.message.author}"
    em.description = f"{idea}"
    em.set_footer(text=f"From {ctx.author.guild}", icon_url=f"{ctx.guild.icon_url}")
    await server.send(embed=em)
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
