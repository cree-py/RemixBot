import discord
import os
import io
import traceback
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='c.')

# Somebody fix this monstrosity pls

try:
    bot.load_extension("cogs.mod")
except:
    pass

try:
    bot.load_extension("cogs.info")
except:
    pass

try:
    bot.load_extension("cogs.fun")
except:
    pass

bot.remove_command('help')

developers = [
    311970805342928896,
    316586772349976586,
    292690616285134850,
    307133814834987008,
    281821029490229251
]


def cleanup_code(content):
    '''Automatically removes code blocks from the code.'''
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')


@bot.event
async def on_ready():
    print("Bot Is Online.")
    await bot.change_presence(game=discord.Game(name=f"{len(bot.guilds)} servers | c.help | Alpha 0.3.1", type=3), afk=True)


@bot.command(name='help')
async def new_help_command(ctx, *commands: str):
    '''Shows this message'''
    destination = ctx.message.author if bot.pm_help else ctx.message.channel

    def repl(obj):
        return bot._mentions_transforms.get(obj.group(0), '')

    # help by itself just lists our own commands.
    if len(commands) == 0:
        pages = await bot.formatter.format_help_for(ctx, bot)
    elif len(commands) == 1:
        # try to see if it is a cog name
        name = bot._mention_pattern.sub(repl, commands[0])
        command = None
        if name in bot.cogs:
            command = bot.cogs[name]
        else:
            command = bot.all_commands.get(name)
            if command is None:
                await destination.send(bot.command_not_found.format(name))
                return

        pages = await bot.formatter.format_help_for(ctx, command)
    else:
        name = bot._mention_pattern.sub(repl, commands[0])
        command = bot.all_commands.get(name)
        if command is None:
            await destination.send(bot.command_not_found.format(name))
            return

        for key in commands[1:]:
            try:
                key = bot._mention_pattern.sub(repl, key)
                command = command.all_commands.get(key)
                if command is None:
                    await destination.send(bot.command_not_found.format(key))
                    return
            except AttributeError:
                await destination.send(bot.command_has_no_subcommands.format(command, key))
                return

    pages = await bot.formatter.format_help_for(ctx, command)

    if bot.pm_help is None:
        characters = sum(map(lambda l: len(l), pages))
        # modify destination based on length of pages.
        if characters > 1000:
            destination = ctx.message.author

    color = discord.Color(value=0x00ff00)
    for embed in pages:
        em = discord.Embed(title='Command Help', color=color)  # create embed object
        embed = embed.strip('```')  # remove the codeblock
        em.description = embed  # set the string from default help message as the description
        await ctx.send(embed=em)  # sends the embed


@bot.command()
async def ping(ctx):
    '''Pong! Check if bot is working'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)


@bot.command(name='presence')
async def _presence(ctx, Type=None, *, thing=None):
    if ctx.author.id not in developers:
        return

    if Type is None:
        await ctx.send('Usage: `.presence [game/stream/watch/listen] [message]`')
    else:
        if Type.lower() == 'stream':
            await bot.change_presence(game=discord.Game(name=thing, type=1, url='https://www.twitch.tv/a'), status='online')
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


@bot.command(hidden=True, name='eval')
async def _eval(ctx, *, body: str):

    if ctx.author.id not in developers:
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
    await ctx.send(f"Invite me to your server: https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=66186303")


@bot.command()
async def say(ctx, *, message: str):
    '''Say something as the bot'''
    await ctx.message.delete()
    await ctx.send(message)


@bot.command()
async def restart(ctx):
    if ctx.author.id not in developers:
        return

    await ctx.send("Restarting....")
    await bot.logout()

if __name__ == "__main__":
    if not os.environ.get('TOKEN'):
        print("No token found REEEE!")
    bot.run(os.environ.get('TOKEN').strip('\"'))
