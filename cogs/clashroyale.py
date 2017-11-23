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

class ClashRoyale:
    def __init__(self,bot):
        self.bot = bot
        self.client = crasync.Client()
    
    @commands.command()
    async def profile(self, ctx, tag=None):
        '''Fetch a Clash Royale Profile by tag'''
        em = discord.Embed(title="Profile", color=discord.Color(value=0x00ff00))
        if tag == None:
            em.description = "Please enter a clash royale tag.\nExample: `c.profile #22UP0G0YU`"
            return await ctx.send(embed=em)
        tag = tag.strip('#').replace('O' ,'0')
        try:
            profile = await self.client.get_profile(tag)
        except Exception as e:
            return await ctx.send(f'`{e}`')
        
        
        
        em.title = profile.name
        em.set_thumbnail(url=profile.arena.image_url)
        em.description = f"#{tag}"
        em.url = f"http://cr-api.com/profile/{tag}"
        em.add_field(name="Current Trophies",value=f"{profile.current_trophies}")
        em.add_field(name="Highest Trophies", value=f"{profile.highest_trophies}")
        em.add_field(name="Legend Trophies", value=f"{profile.legend_trophies}")
        em.add_field(name="Level", value=f"{profile.level}")
        em.add_field(name="Experience", value=f"{profile.experience[0]}/{profile.experience[1]}")
        em.add_field(name="Global Rank", value=f"{profile.global_rank}")
        em.add_field(name="Wins/Losses/Draws", value=f"{profile.wins}/{profile.losses}/{profile.draws}")
        em.add_field(name="Win Streak", value=f"{profile.win_streak}")
        em.add_field(name="Win Rate", value=f"{(profile.wins / (profile.wins + profile.losses) * 100):.3f}%")
        try:
            em.add_field(name="Clan Info", value=f"{profile.clan_name}\n{profile.clan_role}\n#{profile.clan_tag}")
        except ValueError:
            em.add_field(name='Clan Info', value='No clan')
        em.set_footer(text="Powered by cr-api.com", icon_url="http://cr-api.com/static/img/branding/cr-api-logo.png")
        try:
            em.set_author(name="Profile", icon_url=profile.clan_badge_url)
        except:
            em.set_author(name="Profile")
            
       
        await ctx.send(embed=em)
        
    @commands.command()
    async def clan(self, ctx, tag=None):
        '''Gets Clan info by clan tag.'''
        em = discord.Embed(title='Clan Info', color=discord.Color(value=0x00ff00))
        if tag == None:
            em.description = "Please enter a clan tag.\n Example: `c.clan #29UQQ282`"
            return await ctx.send(embed=em)
        tag = tag.strip('#').replace('O', '0')
        try:
            clan = await self.client.get_clan(tag)
        except Exception as e:
            return await ctx.send(f'`{e}`')
            return await ctx.send(embed=em)
        
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
    
