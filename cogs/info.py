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
        created_at = f"Server created on {guild.created_at.strftime('%b %d %Y at %H:%M')}. That\'s over {guild_age} days ago!"
        color = discord.Color(value=0x00ff00)

        em = discord.Embed(description=created_at, color=color)
        em.add_field(name='Online Members', value=len(
            [m for m in guild.members if discord.Status != discord.Status.offline]))
        em.add_field(name='Total Members', value=len(guild.members))
        em.add_field(name='Text Channels', value=len(guild.text_channels))
        em.add_field(name='Voice Channels', value=len(guild.voice_channels))
        em.add_field(name='Roles', value=len(guild.roles))
        em.add_field(name='Owner', value=guild.owner)

        em.set_thumbnail(url=None or guild.icon_url)
        em.set_author(name=guild.name, icon_url=None or guild.icon_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['ui', 'user'])
    async def userinfo(self, ctx, user: discord.Member = None):
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

        rolenames = ', '.join([r.name for r in roles if r != '@everyone']) or 'None'
        time = ctx.message.created_at
        desc = f'{user.name} is chilling in {user.status} mode.'
        member_number = sorted(guild.members,  key=lambda m: m.joined_at).index(user) + 1
        em = discord.Embed(color=color, description=desc, timestamp=time)
        em.add_field(name='Name', value=user.name),
        em.add_field(name='Member Number', value=member_number),
        em.add_field(name='Account Created', value=user.created_at.__format__('%A, %B %d, %Y')),
        em.add_field(name='Join Date', value=user.joined_at.__format__('%A, %B %d, %Y')),
        em.add_field(name='Roles', value=rolenames)
        em.set_thumbnail(url=avi or None)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Info(bot))
