import discord
from discord.ext import commands


class Info:
    '''Get info for a user, server, or role'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['si', 'server'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        '''Get server info'''
        guild = ctx.guild
        guild_age = (ctx.message.created_at - guild.created_at).days
        created_at = f'Server created on %b %d %Y at %H:%M. That\'s over {guild_age} days ago!'
        color = discord.Color(value=0x00ff00)

        em = discord.Embed(description=created_at, color=color)
        fields = [
            ('Online Members', len(
                [m for m in guild.members if discord.Status != discord.Status.offline])),
            ('Total Members', len(guild.members)),
            ('Text Channels', len(guild.text_channels)),
            ('Voice Channels', len(guild.voice_channels)),
            ('Roles', len(guild.roles)),
            ('Owner', guild.owner)
        ]
        for f, v in fields:
            em.add_field(name=f, value=v)

        em.set_thumbnail(url=None or guild.icon_url)
        em.set_author(name=guild.name, icon_url=None or guild.icon_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['ui', 'user'])
    async def userinfo(self, ctx, user: discord.Member=None):
        '''Get user info for yourself or someone in the guild'''
        user = user or ctx.message.author
        guild = ctx.message.guild
        guild_owner = guild.owner
        avi = user.avatar_url
        roles = sorted(user.roles, key=lambda r: r.position)

        for role in roles:
            if str(role.color) != '#000000':
                color = role.color
        if 'color' not in locals():
            color = 0

        rolenames = ', '.join([r.name for r in user.roles if r != '@everyone']) or 'None'
        time = ctx.message.created_at
        desc = f'{user.name} is chilling in {user.status} mode.'
        member_number = sorted(guild.members,  key=lambda m: m.joined_at).index(user) + 1
        em = discord.Embed(color=color, description=desc, timestamp=time)

        fields = [
            ('Name', user.name),
            ('Member Number', member_number),
            ('Account Created', user.created_at.__format__('%A, %B %d, %Y')),
            ('Join Date', user.joined_at.__format__('%A, %B %d, %Y')),
            ('Roles', rolenames)
        ]
        for f, v in fields:
            em.add_field(name=f, value=v)
        em.set_thumbnail(avi)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Info(bot))
