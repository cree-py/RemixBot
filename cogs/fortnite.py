'''
MIT License

Copyright (c) 2017-2018 Cree-Py

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
from ext.paginator import PaginatorSession
import pynite
import os


class Fortnite:
    '''Get Fortnite Battle Royale statistics!'''

    def __init__(self, bot):
        self.bot = bot
        self.client = pynite.Client(
            os.environ.get('TRN-Api-Key'),
            timeout=3,
            session=self.bot.session,
            loop=self.bot.loop
        )

    async def get_name(self, userid):
        result = await self.bot.db.fortnite.find_one({'_id': userid})
        if not result:
            return None
        return result.get('name')

    async def get_plat(self, userid):
        result = await self.bot.db.fortnite.find_one({'_id': userid})
        if not result:
            return None
        return result.get('platform')

    async def save_info(self, userid, plat, name):
        await self.bot.db.fortnite.update_one({'_id': userid}, {'$set': {'_id': userid, 'platform': plat, 'name': name}}, upsert=True)

    @commands.command(aliases=['fsave', 'fortnitesave'])
    async def fnsave(self, ctx, plat, name):
        ''' Save your fortnite information.
        Usage: {p}fnsave <pc|psn|xbl> <username>'''
        plat = plat.lower()
        if plat not in ('psn', 'pc', 'xbl'):
            return await ctx.send("Invalid platform. Accepted platforms: `xbl, psn, pc`")

        await self.save_info(str(ctx.author.id), plat, name)
        await ctx.send(f'Your information (Platform: `{plat}` | Name: `{name}`) has been successfully saved.')

    @commands.command(aliases=['fprofile', 'fortniteprofile'])
    async def fnprofile(self, ctx, plat=None, name=None):
        '''Get your fortnite stats.'''
        await ctx.trigger_typing()
        if plat is None and name is None:
            # connect to db
            plat = await self.get_plat(str(ctx.author.id))
            name = await self.get_name(str(ctx.author.id))
            if plat is None or name is None:
                return await ctx.send(f'Use `{ctx.prefix}fnsave <plat> <name>` to save a profile.')
        else:
            if plat is None or name is None:
                return await ctx.send("Please specify a username as well as the platform.")

        if plat not in ['psn', 'xbl', 'pc']:
            return await ctx.send("Invalid platform.")

        hasSolos = True
        hasDuos = True
        hasSquads = True
        hasLifetime = True

        try:
            player = await self.client.get_player(plat, name)
        except Exception as e:
            return await ctx.send(f'```py\nError {e.code}: {e.error}\n```')
        try:
            solos = await player.get_solos()
        except Exception as e:
            hasSolos = False
        try:
            duos = await player.get_duos()
        except Exception as e:
            hasDuos = False
        try:
            squads = await player.get_squads()
        except Exception as e:
            hasSquads = False
        try:
            lifetime = await player.get_lifetime_stats()
        except Exception as e:
            hasLifetime = False

        pages = []

        if hasLifetime:
            em = discord.Embed(color=discord.Color.green())
            em.title = player.epic_user_handle + '- Lifetime Stats'
            em.description = 'Platform: ' + player.platform_name_long
            em.add_field(name='Wins (%)', value=f'{lifetime[8].value} ({lifetime[9] .value})')
            em.add_field(name='Top 5', value=lifetime[1].value)
            em.add_field(name='Top 12', value=lifetime[4].value)

            em.add_field(name='Score', value=lifetime[6].value)
            em.add_field(name='Matches Played', value=lifetime[7].value)
            em.add_field(name='Time Played', value=lifetime[13].value)

            em.add_field(name='Kills', value=lifetime[10].value)
            em.add_field(name='Kill/Death Ratio', value=lifetime[11].value)
            em.add_field(name='Kills/Min', value=lifetime[12].value)

            pages.append(em)

        if hasSolos:
            em = discord.Embed(color=discord.Color.green())
            em.title = player.epic_user_handle + '- Solos'
            em.description = f'Platform: {player.platform_name_long}'
            em.add_field(name="Victory Royales", value=solos.top1.value)
            em.add_field(name='Top 10', value=solos.top10.value)
            em.add_field(name='Top 25', value=solos.top25.value)

            em.add_field(name="Score", value=solos.score.value)
            em.add_field(name="TRN Rating", value=f'[{solos.trn_rating.display_value}](https://fortnitetracker.com/article/23/trn-rating-you)')
            em.add_field(name="K/D", value=solos.kd.value)

            em.add_field(name="Kills", value=solos.kills.value)
            em.add_field(name="Kills per Minute", value=solos.kpm.value)
            em.add_field(name="Kills per Match", value=solos.kpg.value)

            em.add_field(name="Matches Played", value=solos.matches.value)
            em.add_field(name="Minutes Played", value=solos.minutes_played.display_value)
            em.add_field(name="Average Match Time", value=solos.avg_time_played.display_value)
            pages.append(em)

        if hasDuos:
            em = discord.Embed(color=discord.Color.green())
            em.title = player.epic_user_handle + '- Duos'
            em.description = f'Platform: {player.platform_name_long}'
            em.add_field(name="Victory Royales", value=duos.top1.value)
            em.add_field(name='Top 5', value=duos.top5.value)
            em.add_field(name='Top 10', value=duos.top10.value)

            em.add_field(name="Score", value=duos.score.value)
            em.add_field(name="TRN Rating", value=f'[{duos.trn_rating.display_value}](https://fortnitetracker.com/article/23/trn-rating-you)')
            em.add_field(name="K/D", value=duos.kd.value)

            em.add_field(name="Kills", value=duos.kills.value)
            em.add_field(name="Kills per Minute", value=duos.kpm.value)
            em.add_field(name="Kills per Match", value=duos.kpg.value)

            em.add_field(name="Matches Played", value=duos.matches.value)
            em.add_field(name="Minutes Played", value=duos.minutes_played.display_value)
            em.add_field(name="Average Match Time", value=duos.avg_time_played.display_value)
            pages.append(em)

        if hasSquads:
            em = discord.Embed(color=discord.Color.green())
            em.title = player.epic_user_handle + '- Squads'
            em.description = f'Platform: {player.platform_name_long}'
            em.add_field(name="Victory Royales", value=squads.top1.value)
            em.add_field(name='Top 3', value=squads.top3.value)
            em.add_field(name='Top 6', value=squads.top6.value)

            em.add_field(name="Score", value=squads.score.value)
            em.add_field(name="TRN Rating", value=f'[{squads.trn_rating.display_value}](https://fortnitetracker.com/article/23/trn-rating-you)')
            em.add_field(name="K/D", value=squads.kd.value)

            em.add_field(name="Kills", value=squads.kills.value)
            em.add_field(name="Kills per Minute", value=squads.kpm.value)
            em.add_field(name="Kills per Match", value=squads.kpg.value)

            em.add_field(name="Matches Played", value=squads.matches.value)
            em.add_field(name="Minutes Played", value=squads.minutes_played.display_value)
            em.add_field(name="Average Match Time", value=squads.avg_time_played.display_value)
            pages.append(em)

        p_session = PaginatorSession(ctx, footer=f'Stats made by Cree-Py | Powered by fortnitetracker.com', pages=pages)
        await p_session.run()

    @commands.command(aliases=['fmatches', 'fortnitematches'])
    async def fnmatches(self, ctx, plat=None, name=None):
        '''Get a player's most recent matches.'''
        await ctx.trigger_typing()
        if plat is None and name is None:
            # connect to db
            plat = await self.get_plat(str(ctx.author.id))
            name = await self.get_name(str(ctx.author.id))
            if plat is None or name is None:
                return await ctx.send(f'Use `{ctx.prefix}fnsave <plat> <name>` to save a profile.')
        else:
            if plat is None or name is None:
                return await ctx.send("Please specify a username as well as the platform.")

        if plat not in ['psn', 'xbl', 'pc']:
            return await ctx.send("Invalid platform.")

        try:
            player = await self.client.get_player(plat, name)
        except Exception as e:
            return await ctx.send(f'Error {e.code}: {e.error}')

        try:
            matches = player.recent_matches
        except Exception as e:
            return await ctx.send('This player has no recent matches.')

        modes = {
            'p2': 'Solos',
            'p10': 'Duos',
            'p9': 'Squads'
        }

        pages = []

        for index, match in enumerate(matches):
            em = discord.Embed(color=discord.Color.green())
            em.title = f'{player.epic_user_handle}- Match {index + 1}/{len(matches)}'
            em.description = 'Platform: ' + player.platform_name_long
            em.set_thumbnail(url='https://pbs.twimg.com/profile_images/872808170225270784/_ccP8lTm_400x400.jpg')

            em.add_field(name='Match ID', value=str(match.id))
            em.add_field(name='Mode', value=modes[match.playlist])
            em.add_field(name='Minutes Played', value=str(match.minutes_played))
            em.add_field(name='Kills', value=str(match.kills))

            pages.append(em)

        p_session = PaginatorSession(ctx, footer=f'Stats made by Cree-Py | Powered by fortnitetracker.com', pages=pages)
        await p_session.run()


def setup(bot):
    bot.add_cog(Fortnite(bot))
