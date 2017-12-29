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


class Clash_Royale:
    def __init__(self, bot):
        self.bot = bot
        with open('./data/auths.json') as f:
            auth = json.load(f)
            self.token = auth.get('CR-API')
        self.client = clashroyale.Client(token=self.token, is_async=True, cache_fp='cache.db')

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
        pos = cycle.position
        chests = f'| {self.emoji("chest" + p.get_chest(0).lower())} | '
        chests += ''.join([f'{self.emoji("chest" + p.get_chest(x).lower())}' for x in range(1, 8)])
        special = ''
        for i, attr in enumerate(self.cdir(cycle)):
            if attr != 'position':
                e = attr.replace('_', '')
                if getattr(cycle, attr):
                    c_pos = int(getattr(cycle, attr))
                    until = c_pos - pos
                    special += f'{self.emoji("chest" + e.lower())}{until} '
        return (chests, special)

    @commands.command()
    async def save(self, ctx, tag=None):
        '''Save a tag to your discord profile'''
        if tag is None:
            return await ctx.send('Please enter a tag.\nExample: `c.save #CY8G8VVQ`')
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        try:
            clan = await profile.get_clan()
        except ValueError:
            pass

        if profile.rank is not None:
            global_rank = f"{profile.rank} {self.emoji('global')}"
        else:
            global_rank = f'Unranked {self.emoji("global")}'

        record = f'{profile.games.wins}/{profile.games.draws}/{profile.games.losses}'
        av = profile.clan.badge_url or 'https://i.imgur.com/Y3uXsgj.png'

        chests = self.get_chests(ctx, profile)[0]
        cycle = profile.chest_cycle
        pos = cycle.position
        special = ''

        s = None
        if profile.seasons:
            s = profile.seasons[0]
            global_r = s.end_global
            season = f"Highest: {s.highest} {self.emoji('trophy')}\n" \
                     f"Finish: {s.ending} {self.emoji('trophy')}\n" \
                     f"Global Rank: {global_r} {self.emoji('global')}"
        else:
            season = None

        special = self.get_chests(ctx, profile)[1]

        deck = ''
        for card in profile.deck:
            deck += f"{self.emoji(card.name.lower().strip('.').strip('-').replace(' ', ''))}{card.level}"

        em.title = profile.name
        em.description = f'#{tag}'
        em.url = f'http://cr-api.com/player/{tag}'
        em.set_author(name='Profile', icon_url=av)

        em.add_field(name='Level', value=f'{profile.level} {self.emoji("xp")}')
        em.add_field(name='Arena', value=profile.arena.name)
        em.add_field(
            name='Trophies', value=f'{profile.current_trophies}/{profile.highest_trophies} {self.emoji("trophy")}')
        em.add_field(name='Global Rank', value=global_rank)
        em.add_field(name='Total Donations', value=f'{profile.total_donations} {self.emoji("cards")}')
        em.add_field(name='Win Percentage',
                     value=f'{(profile.games.wins / (profile.games.wins + profile.games.losses) * 100):.3f}% {self.emoji("crownblue")}')
        em.add_field(name='Max Challenge Wins', value=f'{profile.max_wins} {self.emoji("cards")}')
        em.add_field(name='Favorite Card', value=f"{profile.favourite_card.replace('_', ' ')}{self.emoji(profile.favourite_card.lower().strip('.').strip('-').replace(' ', ''))}")
        em.add_field(name='Game Record', value=f'{record} {self.emoji("clashswords")}')
        if profile.clan.role:
            em.add_field(name='Clan Name', value=f'{clan.name} {self.emoji("clan")}')
            em.add_field(name='Clan Tag', value=f"#{clan.tag} {self.emoji('clan')}")
            em.add_field(name='Clan Role', value=f'{profile.clan.role} {self.emoji("clan")}')
        else:
            em.add_field(name='Clan Info', value=f'No clan {self.emoji("clan")}')
        em.add_field(name='Win Streak', value=f"{profile.win_streak} {self.emoji('crownblue')}")
        em.add_field(name='Legendary Trophies', value=f"{profile.legend_trophies} {self.emoji('legendtrophy')}")
        em.add_field(name='Tournament Cards Won', value=f"{profile.tournament_cards_won} {self.emoji('cards')}")
        em.add_field(name='Challenge Cards Won', value=f"{profile.challenge_cards_won} {self.emoji('cards')}")
        em.add_field(name='Battle Deck', value=deck, inline=False)
        em.add_field(name=f'Chests (Total {pos} opened)', value=chests, inline=False)
        em.add_field(name='Chests Until', value=special, inline=False)
        if s:
            em.add_field(name=f'Previous Season Results (Season {s.number})', value=season, inline=False)
        else:
            pass

        em.set_thumbnail(url=profile.arena.image_url)
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        chests = self.get_chests(ctx, profile)[0]
        cycle = profile.chest_cycle
        pos = cycle.position
        special = self.get_chests(ctx, profile)[1]

        em.description = f'{pos} total chests opened.'
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
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
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if clan.rank == 0:
            rank = f"Unranked {self.emoji('global')}"
        else:
            rank = f"{clan.rank} {self.emoji('global')}"

        chest = f'{clan.clan_chest.crowns}/{clan.clan_chest.required} {self.emoji("chestclan")}'

        pushers = []
        if len(clan.members) >= 3:
            for i in range(3):
                pushers.append(
                    f"**{clan.members[i].name}**\n{clan.members[i].trophies} {self.emoji('trophy')}\n#{clan.members[i].tag}")
        contributors = list(reversed(sorted(clan.members, key=lambda x: x.crowns)))

        ccc = []
        if len(clan.members) >= 3:
            for i in range(3):
                ccc.append(
                    f"**{contributors[i].name}**\n{contributors[i].crowns} {self.emoji('crownred')}\n#{contributors[i].tag}")

        em.set_author(name="Clan Info", icon_url=clan.badge_url or None)
        em.title = f"{clan.name} (#{clan.tag})"
        em.set_thumbnail(url=clan.badge_url)
        em.description = f"{clan.description}"
        em.add_field(name="Score", value=f"{clan.score} {self.emoji('trophy')}")
        em.add_field(name="Members", value=f"{len(clan.members)}/50 {self.emoji('clan')}")
        em.add_field(name="Type", value=f"{clan.type_name} :envelope_with_arrow:")
        em.add_field(name="Region", value=f"{clan.region} :earth_americas:")
        em.add_field(name="Global Rank", value=rank)
        em.add_field(name="Chest Progress", value=chest)
        em.add_field(name="Donations", value=f"{clan.donations} {self.emoji('cards')}")
        em.add_field(name="Required Trophies", value=f"{clan.required_trophies} {self.emoji('trophy')}")
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
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
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.crowns * 10) + (m.trophies / 7)) / 3

            to_kick = sorted(clan.members, key=lambda m: m.score)[:4]

            em.description = 'Here are the least valuable members of the clan currently.'
            em.set_author(name=clan)
            em.set_thumbnail(url=clan.badge_url)
            em.set_footer(text='Stats made by Cree-Py | Powered by cr-api.com',
                          icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

            for m in reversed(to_kick):
                em.add_field(name=f'{m.name} ({m.role_name})',
                             value=f"#{m.tag}\n{m.trophies} {self.emoji('trophy')}\n{m.crowns} {self.emoji('crownblue')}\n{m.donations} {self.emoji('cards')}")

            await ctx.send(embed=em)

    @members.command()
    async def best(self, ctx, tag=None):
        '''Find the best members in a clan'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Most Valuable Members')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
                clan = await profile.get_clan()
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
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
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.crowns * 10) + (m.trophies / 7)) / 3

        best = sorted(clan.members, key=lambda m: m.score, reverse=True)[:4]

        em.description = 'Here are the most valuable members of the clan currently.'
        em.set_author(name=clan)
        em.set_thumbnail(url=clan.badge_url)
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api.com',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        for m in reversed(best):
            em.add_field(name=f'{m.name} ({m.role_name})',
                         value=f"#{m.tag}\n{m.trophies} {self.emoji('trophy')}\n{m.crowns} {self.emoji('crownblue')}\n{m.donations} {self.emoji('cards')}")

        await ctx.send(embed=em)

    @commands.command()
    async def trophies(self, ctx, tag=None):
        '''Get your current, record, and legend trophies'''
        await ctx.trigger_typing()
        em = discord.Embed(title='Trophies')
        em.color = discord.Color(value=0x00ff00)

        if tag is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        em.title = profile.name
        em.set_author(
            name='Trophies', icon_url=ctx.author.avatar_url)
        em.description = f'Trophies: {profile.current_trophies} {self.emoji("trophy")}\nPersonal Best: {profile.highest_trophies} {self.emoji("trophy")}\nLegend Trophies: {profile.legend_trophies} {self.emoji("legendtrophy")}'
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
            try:
                profile = await self.client.get_player(tag)
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            try:
                profile = await self.client.get_player(tag.strip('#').replace('O', '0'))
            except (crasync.errors.NotResponding, crasync.errors.ServerError) as e:
                return await ctx.send(f'`Error {e.code}: {e.error}`')

        deck = ''
        aoe = 0
        for card in profile.deck:
            deck += f"{self.emoji(card.name.lower().strip('.').strip('-').replace(' ', ''))}{card.level}"
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
                return await ctx.send('No tag found. Please use `c.save <tag>` to save a tag to your discord profile.')
            tag = self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(tag):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            tag = tag.strip('#').replace('O', '0')

        em.url = f'http://cr-api.com/player/{tag}'
        em.title = ctx.author.name
        em.add_field(name='URL', value=f'http://cr-api.com/player/{tag}')
        em.set_footer(text='Stats made by Cree-Py | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Clash_Royale(bot))
