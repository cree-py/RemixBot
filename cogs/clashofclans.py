'''
MIT License

Copyright (c) 2017 Cree-py

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
import json


class Clash_of_Clans:

    def __init__(self, bot):
        self.bot = bot

    def get_tag(self, userid):
        with open('./data/tags/coctags.json') as f:
            config = json.load(f)
            try:
                tag = config[userid]
            except KeyError:
                return 'None'
        return tag

    def save_tag(self, userid, tag):
        with open('./data/tags/coctags.json', 'r+') as f:
            config = json.load(f)
            f.seek(0)
            config[userid] = tag
            json.dump(config, f, indent=4)

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
            return await ctx.send('Please enter a tag.\nExample: `c.save #92CP9Y8PC`')
        tag = tag.strip('#').replace('O', '0')
        if not self.check_tag(tag):
            return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
        self.save_tag(str(ctx.author.id), tag)
        await ctx.send(f'Your tag (#{tag}) has been successfully saved.')

    @commands.command()
    async def cocprofile(self, ctx, tag=None):
        '''Get a Clash of Clans profile by tag'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))

        with open('data/auths.json') as f:
            coc = json.load(f)
            apikey = coc.get('COC-API')

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send('No tag found. Please use `c.cocsave <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag):
                return await ctx.send('`Invalid Tag. Please make sure your tag is correct.`')
            tag = tag.strip('#')

        headers = {'Authorization': apikey}
        async with self.bot.session as session:
            async with session.get(f'https://api.clashofclans.com/v1/players/%23{tag}', headers=headers) as resp:
                name = resp['name']
                em.title = "CoC Profile"
                em.description = "Clash of Clans Stats"
                try:
                    em.set_thumbnail(url=resp['league']['iconUrls']['medium'])
                except KeyError:
                    em.set_thumbnail(url='http://clash-wiki.com/images/progress/leagues/no_league.png')
                try:
                    em.set_author(name=f"{resp['tag']}", icon_url=resp['clan']['badgeUrls']['large'])
                except KeyError:
                    em.set_author(name=f"{resp['tag']}", icon_url='http://clash-wiki.com/images/progress/leagues/no_league.png')
                em.add_field(name="Player Name", value=f"{name} {self.emoji('clan')}")
                em.add_field(name="Exp", value=f"{resp['expLevel']} {self.emoji('cocexp')}")
                em.add_field(name="Townhall", value=resp['townHallLevel'])
                em.add_field(name="Trophies", value=f"{resp['trophies']} {self.emoji('coctrophy')}")
                em.add_field(name="All Time Best", value=f"{resp['bestTrophies']} {self.emoji('cocpb')}")
                em.add_field(name="Attacks Won", value=f"{resp['attackWins']} {self.emoji('sword')}")
                em.add_field(name="Defenses Won", value=f"{resp['defenseWins']} {self.emoji('cocshield')}")
                em.add_field(name="War Stars", value=f"{resp['warStars']} {self.emoji('cocstar')}")
                try:
                    types = {
                        'member': 'Member',
                        'admin': 'Elder',
                        'coLeader': 'Co-Leader',
                        'leader': 'Leader'
                    }
                    em.add_field(name="Clan Name", value=f"{resp['clan']['name']}{self.emoji('cc')}")
                    em.add_field(name="Clan Role", value=types[resp['role']])
                    em.add_field(name="Donations", value=f"{resp['donations']}")
                    em.add_field(name="Donations Received", value=resp['donationsReceived'])
                except KeyError:
                    em.add_field(name='Clan', value=f"No clan {self.emoji('cc')}")
                try:
                    em.add_field(name="BH Level", value=f"{resp['builderHallLevel']} {self.emoji('builderhall')}")
                    em.add_field(name="BH Trophies", value=f"{resp['versusTrophies']} {self.emoji('coctrophy')}")
                    em.add_field(name="BH Highest Trophies", value=f"{resp['bestVersusTrophies']} {self.emoji('cocpb')}")
                    em.add_field(name="BH Attacks Won", value=f"{resp['versusBattleWins']} {self.emoji('sword')}")

                except KeyError:
                    em.add_field(name='Builder Base', value=f"Not unlocked yet {self.emoji('builderhall')}")

                em.set_footer(text="Stats by Cree-Py | Powered by the CoC API")
                await ctx.send(embed=em)

    @commands.command()
    async def cocclan(self, ctx, tag=None):
        '''Get the stats of a clan in CoC'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))

        with open('data/auths.json') as f:
            coc = json.load(f)
            apikey = coc.get('COC-API')

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send('No tag found. Please use `c.cocsave <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag):
                return await ctx.send('`Invalid Tag. Please make sure your tag is correct.`')
            tag = tag.strip('#')

        headers = {'Authorization': apikey}
        async with self.bot.session as session:
            async with session.get(f'https://api.clashofclans.com/v1/players/%23{tag}', headers=headers) as resp:
                try:
                    clantag = resp['clan']['tag'].strip('#')
                except KeyError:
                    em.title = "Error"
                    em.description = "You are not in a clan"
                    return await ctx.send(embed=em)
        async with self.bot.session as session:
            async with session.get(f'https://api.clashofclans.com/v1/clans/%23{clantag}', headers=headers) as resp:
                em.title = "Clan Info"
                em.description = f"{resp['description']}"
                em.set_author(name=f"{resp['name']} (#{clantag})", icon_url=resp['badgeUrls']['large'])
                em.add_field(name="Clan Level", value=f"{resp['clanLevel']} {self.emoji('cocexp')}")
                em.add_field(name="Location", value=f"{resp['location']['name']} :earth_americas:")
                em.add_field(name="Type", value=f"{resp['type']} :envelope_with_arrow:")
                em.add_field(name='Required Trophies', value=f"{resp['requiredTrophies']} {self.emoji('coctrophy')}")
                em.set_footer(text="Stats by Cree-Py | Powered by the CoC API")

                await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Clash_of_Clans(bot))
