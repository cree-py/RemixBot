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


import requests
import json
import os
import io
import discord
from discord.ext import commands

class ClashOfClans:
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command()
    async def cocprofile(self, ctx, tag=None):
        '''Get a Clash of Clans profile by tag'''
        em = discord.Embed(color=discord.Color(value=0x00ff00))
        if tag == None:
            em.description = "Please enter a tag. For example, c.cocprofile #92CP9Y8PC"
            return await ctx.send(embed=em)
        tag = tag.strip('#')
        try:
            headers={'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjQ3Y2UzZTE3LWQxYmItNDY1MS05YjBiLWQyOWRlMWVhNWIyNCIsImlhdCI6MTUxMjM5NDI2MCwic3ViIjoiZGV2ZWxvcGVyLzM2ZTA0MDAwLTgyMmQtMDk3My1kZjBlLWI4MTZlNTBhMTVlZiIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjM0LjIyNy4xNTAuNDUiXSwidHlwZSI6ImNsaWVudCJ9XX0.NwQOk9rg0D7JexC3Ol-JEKL1nMvdeERXgvIMIm2UhBwsyE01jxESYaVdxujGm_WAdBhOJAOYC47dmkjo046YAQ"}
            response = requests.get('https://api.clashofclans.com/v1/players/%23{tag}', headers=headers)
        except:
             em.description = "Invalid Tag. Please check the tag that you entered is correct"
             return await ctx.send(embed=em)

        status  = response.status_code
        name = response.json()['name']
        clanname=response.json()['clan']['name']
        clan_emoji = bot.get_emoji(387281156258922508)
        trophy_emoji = bot.get_emoji(387281233106698241)
        defense = bot.get_emoji(387281145320046592)
        exp = bot.get_emoji(387315278427717643)
        pb = bot.get_emoji(387281346898165761)
        cc = bot.get_emoji(387281270960422922)
        em.title = "CoC Profile"
        em.description = "Clash of Clans Stats: **BETA**"
        em.set_thumbnail(url=response.json()['league']['iconUrls']['medium'])
        em.set_author(name=f"{response.json()['tag']}", icon_url=response.json()['clan']['badgeUrls']['large'])
        em.add_field(name="Player Name", value=f"{name} {clan_emoji}")
        em.add_field(name="Exp", value=f"{response.json()['expLevel']} {exp}")
        em.add_field(name="Townhall", value=response.json()['townHallLevel'])
        em.add_field(name="Trophies", value=f"{response.json()['trophies']} {trophy_emoji}")
        em.add_field(name="All Time Best", value=f"{response.json()['bestTrophies']} {pb}")
        em.add_field(name="Defenses Won", value=f"{response.json()['defenseWins']} {defense}")
        em.add_field(name="War Stars", value=f"{response.json()['warStars']} :star:")
        em.add_field(name="Clan Name", value=f"{clanname}{cc}")
        em.add_field(name="Clan Role", value=response.json()['role'].title())
        em.set_footer(text="Stats by Cree-Py with CoC API")
        await ctx.send(embed=em)
    
def setup(bot):
    bot.add_cog(ClashOfClans(bot))
