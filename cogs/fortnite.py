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
import pynite
from ext.paginator import PaginatorSession

class Fortnite:
    '''Base class for Fortnite commands.'''
    def __init__(self, bot):
        self.bot = bot
        with open('./data/auths.json') as f:
            auth = json.load(f)
            self.token = auth.get('TRN-Api-Key')
        self.client = pynite.Client(self.token, timeout=5)

    async def get_name(self, userid):
        result = await self.bot.db.fortnite.find_one({'_id': userid})
        if not result:
            return 'None'
        return result['name']

    async def get_plat(self, userid):
        result = await self.bot.db.fortnite.find_one({'_id': userid})
        if not result:
            return 'None'
        return result['platform']

    async def save_info(self, userid, plat, name):
        await self.bot.db.fortnite.update_one({'_id': userid}, {'$set': {'_id': userid, 'platform': plat, 'name': name}}, upsert=True)

    @commands.command(aliases=['fsave', 'fortnitesave'])
    async def fnsave(self, ctx, plat=None, name=None):
        ''' Save your fortnite information.'''
        if plat is None:
            return await ctx.send("Usage: `-fnsave [psn|pc|xbl] [username]`")
        plat = plat.lower()
        if plat not in ['psn', 'pc', 'xbl']:
            return await ctx.send("Invalid platform. Accepted platforms: `xbl, psn, pc`")
        if name is None:
            return await ctx.send("You must provide a username to save.")

        await self.save_info(str(ctx.author.id), plat, name)
        await ctx.send(f'Your information (Platform: {plat} | Name: {name}) has been successfully saved.')
        
    @commands.command(aliases=['fprofile', 'fortniteprofile']):
    async def fnprofile(self, ctx, plat=None, name=None):
        '''Get your fortnite stats.'''
        await ctx.trigger_typing()
        if plat is None:
            if name is None:
                # connect to db
                try:
                    plat = await self.get_plat(str(ctx.author.id))
                    name = await self.get_name(str(ctx.author.id))
                except Exception as e:
                    return await ctx.send(e)
                if plat is None:
                    return await ctx.send("Please specify a platform and username.")
                else:
                    if name is None:
                        return await ctx.send("Please specify a platform and username.")
                    else:
                        pass # Connected to DB and everything works
            else:
                return # shouldn't happen
        else:
            if name is None:
                return await ctx.send("Please specify a username as well as the platform.")
            else:
                pass

        hasSolos = True
        hasDuos = True
        hasSquads = True

        try:
            player = await self.client.get_player(platform, name)
        except NotFound, NoKeyError as e:
            return await ctx.send(f'Error {e.code}: {e.error}')
        try:
            solos = await player.get_solos()
        except NoGames as e:
            hasSolos = False
        try:
            duos = await player.get_duos()
        except NoGames as e:
            hasDuos = False
        try:
            squads = await player.get_squads()
        except NoGames as e:
            hasSquads = False

        pages = []

        if hasSolos:
            solos = await player.get_solos()
            em1 = discord.Embed(color=discord.Color.green())
            em1.title = player.epicUserHandle
            em1.description = f'Platform: {player.platformNameLong}'
            em1.add_field(name="TRN Rating", value=solos.trn_rating.display_value)
            em1.add_field(name="Score", value=solos.score.display_value)
            em1.add_field(name="Victory Royales", value=solos.top1.display_value)
            em1.add_field(name="K/D", value=solos.kd.display_value)
            em1.add_field(name="Matches Played", value=solos.matches.display_value)
            em1.add_field(name="Kills", value=solos.kills.display_value)
            em1.add_field(name="Minutes Played", value=solos.minutes_played.display_value)
            em1.add_field(name="Kills per Minute", value=solos.kpm.display_value)
            em1.add_field(name="Kills per Match", value=solos.kpg.display_value)
            em1.add_field(name="Average Match Time", value=solos.avg_time_played.display_value)
            em1.add_field(name="Score per Match", value=solos.score_per_match.display_value)
            em1.add_field(name="Score per Minute", value=solos.score_per_minute.display_value)
            pages.append(em1)

        if hasDuos:
            duos = await player.get_duos()
            em2 = discord.Embed(color=discord.Color.green())
            em2.title = player.epicUserHandle
            em2.description = f'Platform: {player.platformNameLong}'
            em2.add_field(name="TRN Rating", value=duos.trn_rating.display_value)
            em2.add_field(name="Score", value=duos.score.display_value)
            em2.add_field(name="Victory Royales", value=duos.top1.display_value)
            em2.add_field(name="K/D", value=duos.kd.display_value)
            em2.add_field(name="Matches Played", value=duos.matches.display_value)
            em2.add_field(name="Kills", value=duos.kills.display_value)
            em2.add_field(name="Minutes Played", value=duos.minutes_played.display_value)
            em2.add_field(name="Kills per Minute", value=duos.kpm.display_value)
            em2.add_field(name="Kills per Match", value=duos.kpg.display_value)
            em2.add_field(name="Average Match Time", value=duos.avg_time_played.display_value)
            em2.add_field(name="Score per Match", value=duos.score_per_match.display_value)
            em2.add_field(name="Score per Minute", value=duos.score_per_minute.display_value)
            pages.append(em2)

        if hasSquads:
            squads = await player.get_squads()
            em3 = discord.Embed(color=discord.Color.green())
            em3.title = player.epicUserHandle
            em3.description = f'Platform: {player.platformNameLong}'
            em3.add_field(name="TRN Rating", value=squads.trn_rating.display_value)
            em3.add_field(name="Score", value=squads.score.display_value)
            em3.add_field(name="Victory Royales", value=squads.top1.display_value)
            em3.add_field(name="K/D", value=squads.kd.display_value)
            em3.add_field(name="Matches Played", value=squads.matches.display_value)
            em3.add_field(name="Kills", value=squads.kills.display_value)
            em3.add_field(name="Minutes Played", value=squads.minutes_played.display_value)
            em3.add_field(name="Kills per Minute", value=squads.kpm.display_value)
            em3.add_field(name="Kills per Match", value=squads.kpg.display_value)
            em3.add_field(name="Average Match Time", value=squads.avg_time_played.display_value)
            em3.add_field(name="Score per Match", value=squads.score_per_match.display_value)
            em3.add_field(name="Score per Minute", value=squads.score_per_minute.display_value)
            pages.append(em3)

        p_session = PaginatorSession(ctx, footer=f'Stats made by Cree-Py | Powered by pynite', pages=pages)
        await p_session.run()

def setup(bot):
    bot.add_cog(Fortnite(bot))