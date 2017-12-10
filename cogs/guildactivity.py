import discord
from discord.ext import commands
import json


class Guild_Activity:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['setwelcome', 'welcomemsg', 'joinmessage', 'welcomeset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('./data/welcs.json', 'r+') as f:
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
                return await ctx.send('Welcome messages disabled for this guild.')
            else:
                welc[str(ctx.message.guild.id)]['welctype'] = True
                await ctx.send('Which channel do you want the welcome messages to be set to? Use a channel mention.')
                channel = await self.bot.wait_for('message', check=pred)
                id = channel.content.strip('<#').strip('>')
                if id == channel.content:
                    return await ctx.send('Please mention a channel.')
                welc[str(ctx.message.guild.id)]['welcchannel'] = id
                await ctx.send('What do you want the message to be?\nUsage:```\n{mention}: Mentions the joining user.\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
                msg = await self.bot.wait_for('message', check=pred)
                welc[str(ctx.message.guild.id)]['welc'] = str(msg.content)
                json.dump(welc, f, indent=4)
                await ctx.send('Your welcome message has been successfully set.')

    @commands.command(aliases=['setleave', 'leavemsg', 'leavemessage', 'leaveset'], no_pm=True)
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx, type):
        '''Enable or disable a leave message for your guild'''
        def pred(m):
            return m.author == ctx.author and m.channel == ctx.message.channel

        with open('./data/welcs.json', 'r+') as f:
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
            else:
                leave[str(ctx.message.guild.id)]['leavetype'] = True
                await ctx.send('Which channel do you want the leave messages to be set to? Use a channel mention.')
                channel = await self.bot.wait_for('message', check=pred)
                id = channel.content.strip('<#').strip('>')
                if id == channel.content:
                    return await ctx.send('Please mention a channel.')
                leave[str(ctx.message.guild.id)]['leavechannel'] = id
                await ctx.send('What do you want the message to be?\nUsage:```\n{name}: Replaces this with the user\'s name.\n{server}: Server name.\n{membercount}: Returns the number of members in the guild.\n```')
                msg = await self.bot.wait_for('message', check=pred)
                leave[str(ctx.message.guild.id)]['leave'] = str(msg.content)
                json.dump(leave, f, indent=4)
                await ctx.send('Your leave message has been successfully set.')


def setup(bot):
    bot.add_cog(Guild_Activity(bot))
