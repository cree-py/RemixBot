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
from discord.ext import commands
import crasync
import json


class ClashRoyale:
    def __init__(self, bot):
        self.bot = bot
        self.client = crasync.Client()

    def cdir(self, obj):
        return [x for x in dir(obj) if not x.startswith('_')]

    def get_chests(self, ctx, p):
        cycle = p.chest_cycle
        pos = cycle.position
        chests = p.get_chest(0).title() + '\n'
        chests += '\n'.join([p.get_chest(x).title() for x in range(1, 8)])
        special = ''
        for i, attr in enumerate(self.cdir(cycle)):
            if attr != 'position':
                e = attr.replace('_', '')
                if getattr(cycle, attr):
                    c_pos = int(getattr(cycle, attr))
                    until = c_pos - pos
                    special += f'{e.title()}: +{until} '
                    return (chests, special)

    @commands.command()
    async def profile(self, ctx, tag=None):
        '''Fetch a Clash Royale Profile by tag'''
        em = discord.Embed(title="Profile", color=discord.Color(value=0x00ff00))
        if tag is None:
            em.description = "Please enter a Clash Royale player tag.\nExample: `c.profile #22UP0G0YU`"
            return await ctx.send(embed=em)
        tag = tag.strip('#').replace('O', '0')
        try:
            profile = await self.client.get_profile(tag)
        except Exception as e:
            return await ctx.send(f'`{e}`')\

        try:
            clan = await profile.get_clan()
        except ValueError:
            pass

        if profile.global_rank is not None:
            global_rank = str(profile.global_rank)
        else:
            global_rank = 'Unranked'

        experience = f'{profile.experience[0]}/{profile.experience[1]}'
        record = f'{profile.wins}-{profile.draws}-{profile.losses}'
        av = profile.clan_badge_url or 'https://i.imgur.com/Y3uXsgj.png'

        chests = self.get_chests(ctx, profile)[0]
        cycle = profile.chest_cycle
        pos = cycle.position
        special = ''

        s = None
        if profile.seasons:
            s = profile.seasons[0]
            global_r = s.end_global
            season = f"Highest: {s.highest} trophies\n" \
                     f"Finish: {s.ending} trophies\n" \
                     f"Global Rank: {global_r}"
        else:
            season = None

        special = self.get_chests(ctx, profile)[1]
        shop_offers = ''
        if profile.shop_offers.legendary:
            shop_offers += f"Legendary Chest: {profile.shop_offers.legendary} days\n"
        if profile.shop_offers.epic:
            shop_offers += f"Epic Chest: {profile.shop_offers.epic} days\n"
        if profile.shop_offers.arena:
            shop_offers += f"Arena: {profile.shop_offers.arena} days\n"

        deck = ''
        for card in profile.deck:
            deck += f'{card.name}: Lvl {card.level}\n'

        em.title = profile.name
        em.description = f'#{tag}'
        em.url = f'http://cr-api.com/profile/{tag}'
        em.set_author(name='Profile', icon_url=av)

        em.add_field(name='Level', value=f'{profile.level} ({experience})')
        em.add_field(name='Arena', value=profile.arena.name)
        em.add_field(
            name='Trophies', value=f'{profile.current_trophies}/{profile.highest_trophies}(PB)/{profile.legend_trophies} Legend')
        em.add_field(name='Global Rank', value=global_rank)
        em.add_field(name='Total Donations', value=f'{profile.total_donations}')
        em.add_field(name='Win Percentage',
                     value=f'{(profile.wins / (profile.wins + profile.losses) * 100):.3f}%')
        em.add_field(name='Max Challenge Wins', value=f'{profile.max_wins}')
        em.add_field(name='Favorite Card', value=profile.favourite_card.replace('_', ' '))
        em.add_field(name='Game Record (Win Streak)', value=f'{record} ({profile.win_streak})')
        if profile.clan_role:
            em.add_field(name='Clan Info', value=f'{clan.name}\n#{clan.tag}\n{profile.clan_role}')
        else:
            em.add_field(name='Clan Info', value='No clan')

        em.add_field(name='Tournament Cards Won', value=str(profile.tournament_cards_won))
        em.add_field(name='Challenge Cards Won', value=str(profile.challenge_cards_won))
        em.add_field(name='Battle Deck', value=deck)
        em.add_field(name=f'Chests (Total {pos} opened)', value=chests)
        em.add_field(name='Chests Until', value=special)
        em.add_field(name='Shop Offers', value=shop_offers)
        if s:
            em.add_field(name=f'Previous Season Results (Season {s.number})', value=season)
        else:
            pass

        em.set_thumbnail(url=profile.arena.image_url)
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)

    @commands.command()
    async def clan(self, ctx, tag=None):
        '''Gets Clan info by clan tag.'''
        em = discord.Embed(title='Clan Info', color=discord.Color(value=0x00ff00))
        if tag is None:
            em.description = "Please enter a clan tag.\n Example: `c.clan #29UQQ282` or `c.clan alpha`"
            return await ctx.send(embed=em)
        with open('./data/clans.json') as f:
            clans = json.load(f)
        try:
            tag = clans[tag.lower()]
        except KeyError:
            tag = tag.strip('#').replace('O', '0')
        try:
            clan = await self.client.get_clan(tag)
        except Exception as e:
            return await ctx.send(f'`{e}`')

        em.set_author(name="Clan Info", icon_url=clan.badge_url or None)
        em.title(f"{clan.name} (#{clan.tag})")
        em.set_thumbnail(url=clan.badge_url)
        em.description(f"{clan.description}")
        em.add_field(name="Clan Name", value=f"{clan.name}")
        em.add_field(name="Clan Trophies", value=f"{clan.score}")
        em.add_field(name="Clan Members", value=f"{len(clan.members)}/50")
        em.add_field(name="Type:", value=f"{clan.type_name}")
        em.add_field(name="Location", value=f"{clan.region}")
        em.add_field(name="Rank", value=f"{clan.rank}")
        em.add_field(name="Donations", value=f"{clan.donations}")
        em.add_field(name="Required Trophies", value=f"{clan.required_trophies}")
        em.set_footer(text="Powered by cr-api.com", icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(ClashRoyale(bot))
