import discord
import os
import io
import traceback
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands

client = discord.Client()
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


@bot.command()
async def help(ctx):
    '''Shows this message'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Help"
    em.description = "A bot under development by Antony, Sleedyak, Victini, Free TNT, and SharpBit. Feel free to drop into the server and help with development and for support [here](https://discord.gg/qv9UcBh)"
    em.add_field(name="Ping", value="Pong!")
    em.add_field(name="Invite", value="Invite me to your server.")
    em.add_field(name="Kick", value="Kick someone from the server.")
    em.add_field(name="Ban", value="Ban someone from the server.")
    em.add_field(
        name="Mute", value="Mutes someone from a specified channel. Requires the ban members permission")
    em.add_field(
        name="Unmute", value="Unmute someone you previously muted. Requires the ban members permission")
    em.add_field(name="Say", value="Say something as the bot.")
    em.add_field(name="Warn", value="Warn a user. Usage : c.warn @user <reason>")
    em.add_field(name="Randomnumber", value="Returns a number between 1 and 100")
    em.add_field(name="8ball", value="Ask 8ball a question")
    em.add_field(name="Quote", value="Inspirational quotes")
    em.add_field(name="Dice", value="Roll some dice")
    em.add_field(name="Coin", value="Flip a coin")
    em.add_field(name="Help", value="Shows this message.")
    await bot.get_user(ctx.message.author.id).send(embed=em)
    if ctx.message.channel.guild:
        await ctx.send(f"{ctx.message.author.mention}, I DMed you a list of commands.")
    else:
        pass


@bot.command()
async def ping(ctx):
    '''Pong! Check if bot is working'''
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "Pong!"
    em.description = f'{bot.ws.latency * 1000:.4f} ms'
    await ctx.send(embed=em)


@bot.command(name='presence')
async def _presence(ctx, type=None, *, game=None):
    if ctx.author.id not in developers:
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
