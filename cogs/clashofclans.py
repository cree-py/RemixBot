'''
MIT License

Copyright (c) 2017-2018 Cree-py

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
from discord.ext import commands
import aiohttp
import json
import re
import cocasync


class Clash_of_Clans:
    '''A cog for Clash of Clans stats.'''

    def __init__(self, bot):
        self.bot = bot
        self.apikey = bot.auth.get('COC-API')
        self.client = cocasync.Client(token=self.apikey)

    # The following lines of code are taken from the clashroyale wrapper for cr-api by kyber
    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')

    def _to_snake_case(self, name):
        s1 = self.first_cap_re.sub(r'\1 \2', name)
        return self.all_cap_re.sub(r'\1 \2', s1).title()
    # This marks the end of that code. We give full credit to Kyber

    async def get_tag(self, userid):
        result = await self.bot.db.clashofclans.find_one({'_id': userid})
        if not result:
            return 'None'
        return result['tag']

    async def save_tag(self, userid, tag):
        await self.bot.db.clashofclans.update_one({'_id': userid}, {'$set': {'_id': userid, 'tag': tag}}, upsert=True)

    def check_tag(self, tag):
        for char in tag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False
        return True

    def emoji(self, emoji):
        with open('data/emojis.json') as f:
            emojis = json.load(f)
            e = emojis[emoji]
        return self.bot.get_emoji(e)

    @commands.command()
    async def cocsave(self, ctx, tag=None):
        '''Save a Clash of Clans tag to your discord profile'''
        if tag is None:
            return await ctx.send(f'Please enter a tag.\nExample: `{ctx.prefix}save #92CP9Y8PC`')
        tag = tag.strip('#').replace('O', '0')
        if not self.check_tag(tag):
            return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
        await self.save_tag(str(ctx.author.id), tag)
        await ctx.send(f'Your tag (#{tag}) has been successfully saved.')

    @commands.command()
    async def cocprofile(self, ctx, tag=None):
        '''Get a Clash of Clans profile by tag'''
        em = discord.Embed(color=discord.Color.green())

        if tag is None:
            if await self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}cocsave <tag>` to save a tag to your discord profile.')
            tag = await self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag):
                return await ctx.send('`Invalid Tag. Please make sure your tag is correct.`')
            tag = tag.strip('#')

        player = await self.client.getPlayer(tag)
       
        name = player.name
        em.title = "CoC Profile"
        em.description = "Clash of Clans Stats"
        try:
            em.set_thumbnail(url=player.league.iconUrls.medium)
        except:
            em.set_thumbnail(url='http://clash-wiki.com/images/progress/leagues/no_league.png')
        try:
            em.set_author(name=player.tag, icon_url=player.clan.badgeUrls.large)
        except:
            em.set_author(name=player.tag, icon_url='http://clash-wiki.com/images/progress/leagues/no_league.png')
        em.add_field(name="Player Name", value=f"{name} {self.emoji('clan')}")
        em.add_field(name="Exp", value=f"{player.expLevel} {self.emoji('cocexp')}")
        em.add_field(name="Townhall", value=player.townHallLevel)
        em.add_field(name="Trophies", value=f"{player.trophies} {self.emoji('coctrophy')}")
        em.add_field(name="All Time Best", value=f"{player.bestTrophies} {self.emoji('cocpb')}")
        em.add_field(name="Attacks Won", value=f"{player.attackWins} {self.emoji('sword')}")
        em.add_field(name="Defenses Won", value=f"{player.defenseWins} {self.emoji('cocshield')}")
        em.add_field(name="War Stars", value=f"{player.warStars} {self.emoji('cocstar')}")
        try:
            types = {
                'member': 'Member',
                'admin': 'Elder',
                'coLeader': 'Co-Leader',
                'leader': 'Leader'
            }
            em.add_field(name="Clan Name", value=f"{player.clan.name}{self.emoji('cc')}")
                    em.add_field(name="Clan Role", value=types[player.role])
                    em.add_field(name="Donations", value=f"{player.donations}")
                    em.add_field(name="Donations Received", value=player.donationsReceived)
        except KeyError:
            em.add_field(name='Clan', value=f"No clan {self.emoji('cc')}")
        try:
            em.add_field(name="BH Level", value=f"{player.builderHallLevel} {self.emoji('builderhall')}")
            em.add_field(name="BH Trophies", value=f"{player.versusTrophies} {self.emoji('coctrophy')}")
            em.add_field(name="BH Highest Trophies", value=f"{player.bestVersusTrophies} {self.emoji('cocpb')}")
            em.add_field(name="BH Attacks Won", value=f"{player.versusBattleWins} {self.emoji('sword')}")

        except KeyError:
            em.add_field(name='Builder Base', value=f"Not unlocked yet {self.emoji('builderhall')}")

        em.set_footer(text="Stats by Cree-Py | Powered by the cocasync")
        await ctx.send(embed=em)

    @commands.command()
    async def cocclan(self, ctx, tag=None):
        '''Get the stats of a clan in CoC'''
        em = discord.Embed(color=discord.Color.green())

        if tag is None:
            if await self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}cocsave <tag>` to save a tag to your discord profile.')
            tag = await self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag):
                return await ctx.send('`Invalid Tag. Please make sure your tag is correct.`')
            tag = tag.strip('#')

        tag = tag.strip('#')

        try:
            player = await self.client.getPlayer(tag)
        except:
            try:
                clan = await self.client.getClan(tag)
            except:
                return await ctx.send('Invalid tag.')
        else:
            try:
                clan = await player.getClan()
            except:
                return await ctx.send('You are not in a clan.')

        em.title = "Clan Info"
        em.description = f"{clan.description}"
        em.set_author(name=f"{clan.name} (#{clan.tag})", icon_url=clan.badgeUrls.large)
        em.set_thumbnail(url=clan.badgeUrls.large)
        em.add_field(name="Clan Level", value=f"{clan.clanLevel} {self.emoji('cocexp')}")
        em.add_field(name="Location", value=f"{clan.location.name} :earth_americas:")
        em.add_field(name="Type", value=f"{self._to_snake_case(clan.type)} :envelope_with_arrow:")
        em.add_field(name='Required Trophies', value=f"{clan.requiredTrophies} {self.emoji('coctrophy')}")
        em.set_footer(text="Stats by Cree-Py | Powered by cocasync")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Clash_of_Clans(bot))
