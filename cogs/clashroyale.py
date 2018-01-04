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
import clashroyale
import json
import re


class Clash_Royale:

    def __init__(self, bot):
        self.bot = bot
        with open('./data/auths.json') as f:
            auth = json.load(f)
            self.token = auth.get('CR-API')
        self.client = clashroyale.Client(token=self.token, is_async=True, cache_fp='cache.db')

    # The following lines of code are taken from the clashroyale wrapper for cr-api by kyber
    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')

    def _to_snake_case(self, name):
        s1 = self.first_cap_re.sub(r'\1-\2', name)
        return self.all_cap_re.sub(r'\1-\2', s1).title()
    # This marks the end of that code. We give full credit to Kyber

    def get_tag(self, userid):
        with open('./data/tags/tags.json') as f:
            config = json.load(f)
            try:
                tag = config[userid]
            except KeyError:
                return 'None'
        return tag

    def save_tag(self, userid, tag):
        with open('./data/tags/tags.json', 'r+') as f:
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
        if emoji == 'chestmagic':
            emoji = 'chestmagical'
        with open('data/emojis.json') as f:
            emojis = json.load(f)
            e = emojis[emoji]
        return self.bot.get_emoji(e)

    def cdir(self, obj):
        return [x for x in dir(obj) if not x.startswith('_')]

    def get_chests(self, ctx, p):
        cycle = p.chest_cycle
        chests = f'| {self.emoji("chest" + cycle.upcoming[0].lower())} | '
        chests += ''.join([f'{self.emoji("chest" + cycle.upcoming[x].lower())}' for x in range(1, 8)])
        special = f'{self.emoji("chestsupermagical")}{cycle.super_magical} {self.emoji("chestmagical")}{cycle.magical} {self.emoji("chestlegendary")}{cycle.legendary} {self.emoji("chestepic")}{cycle.epic} {self.emoji("chestgiant")}{cycle.giant}'
        return (chests, special)

    @commands.command()
    async def save(self, ctx, tag=None):
        '''Save a tag to your discord profile'''
        if tag is None:
            return await ctx.send(f'Please enter a tag.\nExample: `{ctx.prefix}save #CY8G8VVQ`')
        tag = tag.strip('#').replace('O', '0')
        if not self.check_tag(tag):
            return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
        self.save_tag(str(ctx.author.id), tag)
        await ctx.send(f'Your tag (#{tag}) has been successfully saved.')

    @commands.command()
    async def profile(self, ctx, tag=None):
        '''Fetch a profile by tag'''
        await ctx.trigger_typing()
        em = discord.Embed(title="Profile", color=discord.Color(value=0x00ff00))
        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        # Gets the player's clan, ValueError if no clan, ignores it.
        try:
            clan = await profile.get_clan()
        except ValueError:
            pass

        # If global rank is 0, then replace it with "Unranked"
        if profile.rank is not None:
            global_rank = f"{profile.rank} {self.emoji('global')}"
        else:
            global_rank = f'Unranked {self.emoji("global")}'

        record = f'{profile.games.wins}/{profile.games.losses}/{profile.games.draws}'
        av = profile.clan.badge.image or 'https://i.imgur.com/Y3uXsgj.png'

        chests = self.get_chests(ctx, profile)[0]

        # Gets the most recent season info, otherwise none
        s = None
        if profile.league_statistics:
            s = profile.league_statistics.previous_season
            global_r = s.rank
            season = f"Highest: {s.best_trophies} {self.emoji('trophy')}\n" \
                     f"Finish: {s.trophies} {self.emoji('trophy')}\n" \
                     f"Global Rank: {global_r} {self.emoji('global')}"
        else:
            season = None

        special = self.get_chests(ctx, profile)[1]

        # Gets the emoji of level of all cards in a deck
        deck = ''
        for card in profile.current_deck:
            deck += f"{self.emoji(card.name.lower().replace('.', '').replace('-', '').replace(' ', ''))}{card.level}"

        em.title = profile.name
        em.description = f'#{tag}'
        em.url = f'http://cr-api.com/profile/{tag}'
        em.set_author(name='Profile', icon_url=av)

        em.add_field(name='Level', value=f'{profile.stats.level} {self.emoji("xp")}')
        em.add_field(name='Arena', value=profile.arena.name)
        em.add_field(
            name='Trophies', value=f'{profile.trophies}/{profile.stats.max_trophies} {self.emoji("trophy")}')
        em.add_field(name='Global Rank', value=global_rank)
        em.add_field(name='Total Donations', value=f'{profile.stats.total_donations} {self.emoji("cards")}')
        em.add_field(name='Win Percentage',
                     value=f'{(profile.games.wins / (profile.games.wins + profile.games.losses) * 100):.3f}% {self.emoji("crownblue")}')
        em.add_field(name='Max Challenge Wins', value=f'{profile.stats.challenge_max_wins} {self.emoji("cards")}')
        em.add_field(name='Favorite Card', value=f"{profile.stats.favorite_card.name.replace('_', ' ')}{self.emoji(profile.stats.favorite_card.name.lower().replace('.', '').replace('-', '').replace(' ', ''))}")
        em.add_field(name='Game Record (W/L/D)', value=f'{record} {self.emoji("clashswords")}')
        if profile.clan.role:
            em.add_field(name='Clan Name', value=f'{clan.name} {self.emoji("clan")}')
            em.add_field(name='Clan Tag', value=f"#{clan.tag} {self.emoji('clan')}")
            em.add_field(name='Clan Role', value=f'{self._to_snake_case(profile.clan.role)} {self.emoji("clan")}')
        else:
            em.add_field(name='Clan Info', value=f'No clan {self.emoji("clan")}')
        em.add_field(name='Tournament Cards Won', value=f"{profile.stats.tournament_cards_won} {self.emoji('cards')}")
        em.add_field(name='Challenge Cards Won', value=f"{profile.stats.challenge_cards_won} {self.emoji('cards')}")
        em.add_field(name='Battle Deck', value=deck, inline=False)
        em.add_field(name=f'Upcoming Chests', value=chests, inline=False)
        em.add_field(name='Chests Until', value=special, inline=False)
        if s:
            em.add_field(name=f'Previous Season Results ({s.id})', value=season, inline=False)

        em.set_thumbnail(url=f'https://cr-api.github.io/cr-api-assets/arenas/arena{profile.arena.arenaID}.png'))
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)

    @commands.command()
    async def chests(self, ctx, tag=None):
        '''Get a profile's chest cycle'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Upcoming Chests', color=discord.Color(value=0x00ff00))
        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        chests = self.get_chests(ctx, profile)[0]
        special = self.get_chests(ctx, profile)[1]

        em.url = f'http://cr-api.com/profile/{tag}'
        em.add_field(name='Upcoming', value=chests, inline=False)
        em.add_field(name='Chests Until', value=special, inline=False)
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
        em.set_author(name='Upcoming Chests')
        em.title = f'{profile.name} (#{profile.tag})'

        await ctx.send(embed=em)

    @commands.command()
    async def clan(self, ctx, tag=None):
        '''Gets a clan's info by clan tag'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Clan Info', color=discord.Color(value=0x00ff00))
        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            with open('./data/clans.json') as f:
                clans = json.load(f)
            try:
                tag = clans[tag.lower()]
            except KeyError:
                tag = tag.strip('#').replace('O', '0')
            try:
                clan = await self.client.get_clan(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if not clan.rank:
            rank = f"Unranked {self.emoji('global')}"
        else:
            rank = f"{clan.rank} {self.emoji('global')}"

        if clan.clan_chest.status == 'inactive':
            chest = f"Inactive {self.emoji('chestclan')}"
        else:
            crowns = 0
            for m in clan.members:
                crowns += m.clan_chest_crowns
            chest = f'{crowns}/1600 {self.emoji("chestclan")}'

        pushers = []
        if len(clan.members) >= 3:
            for i in range(3):
                pushers.append(
                    f"**{clan.members[i].name}**\n{clan.members[i].trophies} {self.emoji('trophy')}\n#{clan.members[i].tag}")
        contributors = list(reversed(sorted(clan.members, key=lambda x: x.clan_chest_crowns)))

        ccc = []
        if len(clan.members) >= 3:
            for i in range(3):
                ccc.append(
                    f"**{contributors[i].name}**\n{contributors[i].clan_chest_crowns} {self.emoji('crownred')}\n#{contributors[i].tag}")

        em.set_author(name="Clan Info", icon_url=clan.badge.image or None)
        em.title = f"{clan.name} (#{clan.tag})"
        em.set_thumbnail(url=clan.badge.image)
        em.description = f"{clan.description}"
        em.add_field(name="Score", value=f"{clan.score} {self.emoji('trophy')}")
        em.add_field(name="Members", value=f"{len(clan.members)}/50 {self.emoji('clan')}")
        em.add_field(name="Type", value=f"{clan.type.title()} :envelope_with_arrow:")
        em.add_field(name="Region", value=f"{clan.location.name} :earth_americas:")
        em.add_field(name="Global Rank", value=rank)
        em.add_field(name="Chest Progress", value=chest)
        em.add_field(name="Donations", value=f"{clan.donations} {self.emoji('cards')}")
        em.add_field(name="Required Trophies", value=f"{clan.required_score} {self.emoji('trophy')}")
        em.add_field(name='Top Players', value='\n\n'.join(pushers))
        em.add_field(name='Top Contributors', value='\n\n'.join(ccc))
        em.set_footer(text="Stats made by Cree-Py | Powered by cr-api.com", icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png")
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def members(self, ctx):
        '''A command group that finds the worst and best members in a clan'''
        await ctx.send(f'Proper usage: `{ctx.prefix}members <best | worst> <clan_tag>`')

    @members.command()
    async def worst(self, ctx, tag=None):
        '''Find the worst members in a clan'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Least Valuable Members')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            with open('./data/clans.json') as f:
                clans = json.load(f)
            try:
                tag = clans[tag.lower()]
            except KeyError:
                tag = tag.strip('#').replace('O', '0')
            try:
                clan = await self.client.get_clan(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.clan_chest_crowns * 10) + (m.trophies / 7)) / 3

            to_kick = sorted(clan.members, key=lambda m: m.score)[:4]

            em.description = 'Here are the least valuable members of the clan currently.'
            em.set_author(name=clan)
            em.set_thumbnail(url=clan.badge.image)
            em.set_footer(text='Stats made by Cree-Py | Powered by cr-api.com',
                          icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

            for m in reversed(to_kick):
                em.add_field(name=f'{m.name} ({self._to_snake_case(m.role)})',
                             value=f"#{m.tag}\n{m.trophies} {self.emoji('trophy')}\n{m.clan_chest_crowns} {self.emoji('crownblue')}\n{m.donations} {self.emoji('cards')}")

            await ctx.send(embed=em)

    @members.command()
    async def best(self, ctx, tag=None):
        '''Find the best members in a clan'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Most Valuable Members')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            with open('./data/clans.json') as f:
                clans = json.load(f)
            try:
                tag = clans[tag.lower()]
            except KeyError:
                tag = tag.strip('#').replace('O', '0')
            try:
                clan = await self.client.get_clan(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.clan_chest_crowns * 10) + (m.trophies / 7)) / 3

        best = sorted(clan.members, key=lambda m: m.score, reverse=True)[:4]

        em.description = 'Here are the most valuable members of the clan currently.'
        em.set_author(name=clan)
        em.set_thumbnail(url=clan.badge.image)
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api.com',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        for m in reversed(best):
            em.add_field(name=f'{m.name} ({self._to_snake_case(m.role)})',
                         value=f"#{m.tag}\n{m.trophies} {self.emoji('trophy')}\n{m.clan_chest_crowns} {self.emoji('crownblue')}\n{m.donations} {self.emoji('cards')}")

        await ctx.send(embed=em)

    @commands.command()
    async def trophies(self, ctx, tag=None):
        '''Get your current, record, and legend trophies'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Trophies')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag.strip('#').replace('O', '0')):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        em.title = profile.name
        em.set_author(
            name='Trophies', icon_url=ctx.author.avatar_url)
        em.description = f'Trophies: {profile.trophies} {self.emoji("trophy")}\nPersonal Best: {profile.stats.wmax_trophies} {self.emoji("trophy")}'
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)

    @commands.command()
    async def deck(self, ctx, tag=None):
        '''View a player's current battle deck'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Battle Deck')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag.strip('#').replace('O', '0')):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        deck = ''
        aoe = 0
        for card in profile.current_deck:
            deck += f"{self.emoji(card.name.lower().replace('.', '').replace('-', '').replace(' ', ''))}{card.level}"
            aoe += card.elixir
        aoe = f'{(aoe / 8):.3f}'

        em.title = profile.name
        em.set_author(name='Battle Deck', icon_url='https://cdn.discordapp.com/emojis/376367875965059083.png')
        em.description = deck
        em.add_field(name='Average Elixir Cost', value=aoe)
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)

    @commands.command()
    async def weburl(self, ctx, tag=None):
        '''Get the cr-api.com url for a player tag'''
        await ctx.trigger_typing()
        em = discord.Embed(title='cr-api.com URL')
        em.color = discord.Color(value=0x00ff00)
        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag.strip('#').replace('O', '0')):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            tag = tag.strip('#').replace('O', '0')

        em.url = f'http://cr-api.com/profile/{tag}'
        em.title = ctx.author.name
        em.add_field(name='URL', value=f'http://cr-api.com/profile/{tag}')
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Clash_Royale(bot))
