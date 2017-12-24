import discord
from discord.ext import commands
import datetime
import json


class Config:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx, *, pre):
        '''Set a custom prefix for the guild. Doesn't work yet.'''
        with open('./data/config.json', 'r+') as f:
            prefix = json.load(f)
            try:
                p = prefix[str(ctx.message.guild.id)]
            except KeyError:
                prefix[str(ctx.message.guild.id)] = dict()
                prefix[str(ctx.message.guild.id)]['prefix'] = 'c.'
            f.seek(0)

            prefix[str(ctx.message.guild.id)]['prefix'] = str(pre)
            json.dump(prefix, f, indent=4)
            await ctx.send('The guild prefix has been set to `{pre}`')

    @commands.command(aliases=['setwelcome', 'welcomemsg', 'joinmessage', 'welcomeset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('./data/config.json', 'r+') as f:
            welc = json.load(f)
            try:
                g = welc[str(ctx.message.guild.id)]
            except KeyError:
                welc[str(ctx.message.guild.id)] = dict()
                welc[str(ctx.message.guild.id)]['welctype'] = False
            f.seek(0)

            if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
                welc[str(ctx.message.guild.id)]['welctype'] = False
                json.dump(welc, f, indent=4)
                await ctx.send('Welcome messages disabled for this guild.')
            else:
                welc[str(ctx.message.guild.id)]['welctype'] = True
                await ctx.send('Which channel do you want the welcome messages to be set to? Use a channel mention.')
                channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
                id = channel.content.strip('<#').strip('>')
                if id == channel.content:
                    return await ctx.send('Please mention a channel.')
                welc[str(ctx.message.guild.id)]['welcchannel'] = id
                await ctx.send('What do you want the message to be?\nUsage:```\n{mention}: Mentions the joining user.\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
                msg = await self.bot.wait_for('message', check=pred, timeout=60.0)
                welc[str(ctx.message.guild.id)]['welc'] = str(msg.content).replace('"', '\"')
                json.dump(welc, f, indent=4)
                await ctx.send('Your welcome message has been successfully set.')

    @commands.command(aliases=['setleave', 'leavemsg', 'leavemessage', 'leaveset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('./data/config.json', 'r+') as f:
            leave = json.load(f)
            try:
                g = leave[str(ctx.message.guild.id)]
            except KeyError:
                leave[str(ctx.message.guild.id)] = dict()
                leave[str(ctx.message.guild.id)]['leavetype'] = False
            f.seek(0)

            if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
                leave[str(ctx.message.guild.id)]['leavetype'] = False
                json.dump(leave, f, indent=4)
                await ctx.send('Leave messages disabled for this guild.')
            else:
                leave[str(ctx.message.guild.id)]['leavetype'] = True
                await ctx.send('Which channel do you want the leave messages to be set to? Use a channel mention.')
                channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
                id = channel.content.strip('<#').strip('>')
                if id == channel.content:
                    return await ctx.send('Please mention a channel.')
                leave[str(ctx.message.guild.id)]['leavechannel'] = id
                await ctx.send('What do you want the message to be?\nUsage:```\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
                msg = await self.bot.wait_for('message', check=pred, timeout=60.0)
                leave[str(ctx.message.guild.id)]['leave'] = str(msg.content).replace('"', '\"')
                json.dump(leave, f, indent=4)
                await ctx.send('Your leave message has been successfully set.')

    @commands.command(aliases=['mod-log'])
    @commands.has_permissions(view_audit_log=True)
    async def modlog(self, ctx, type):
        '''Toggle mod-logs for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('./data/config.json', 'r+') as f:
            logs = json.load(f)
            try:
                g = logs[str(ctx.message.guild.id)]
            except KeyError:
                logs[str(ctx.message.guild.id)] = dict()
                logs[str(ctx.message.guild.id)]['logtype'] = False
            f.seek(0)

            if type.lower() in ('n', 'no', 'disabled', 'disable', 'off'):
                logs[str(ctx.message.guild.id)]['logtype'] = False
                json.dump(logs, f, indent=4)
                await ctx.send('Mod-logs are disabled for this guild.')
            else:
                logs[str(ctx.message.guild.id)]['logtype'] = True
                await ctx.send('Which channel do you want the events to be logged in? Use a channel mention.')
                channel = await self.bot.wait_for('message', check=pred, timeout=60.0)
                id = channel.content.strip('<#').strip('>')
                if id == channel.content:
                    return await ctx.send('Please mention a channel.')
                logs[str(ctx.message.guild.id)]['logchannel'] = id
                json.dump(logs, f, indent=4)
                await ctx.send(f'Mod-logs have been successfully set in <#{id}>')

    # ------------Mod-log events below-------------

    def logtype(self, item):
        with open('./data/config.json') as f:
            type = json.load(f)
            try:
                enabled = type[str(item.guild.id)]['logtype']
                channel = type[str(item.guild.id)]['logchannel']
            except KeyError:
                return
            else:
                if enabled:
                    return True, self.bot.get_channel(int(channel))
                else:
                    return False

    # async def on_raw_message_delete(self, message, ch):
    #     msg = await self.bot.get_channel(ch).get_message(message)
    #     if not self.logtype(msg)[0]:
    #         return
    #     em = discord.Embed(description=f'**Message sent by {msg.author.mention} deleted in {ch.mention}**\n{msg.content}')
    #     em.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
    #     em.set_footer(f'ID: {msg.id}')
    #     await self.logtype(msg)[1].send(embed=em)

    async def on_guild_channel_create(self, channel):
        if not self.logtype(channel)[0]:
            return
        em = discord.Embed(title='Channel Created', description=f'Channel {channel.mention} was created.', color=0x00ff00)
        em.timestamp = datetime.datetime.utcnow()
        em.set_footer(text=f'ID: {channel.id}')
        await self.logtype(channel)[1].send(embed=em)

    async def on_guild_channel_delete(self, channel):
        if not self.logtype(channel)[0]:
            return
        em = discord.Embed(title='Channel Deleted', description=f'Channel {channel.mention} was deleted.', color=0xff0000)
        em.timestamp = datetime.datetime.utcnow()
        em.set_footer(text=f'ID: {channel.id}')
        await self.logtype(channel)[1].send(embed=em)


def setup(bot):
    bot.add_cog(Config(bot))
