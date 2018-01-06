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
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import aiohttp
import datetime
import json
import pytz


class BrawlStars:

    def __init__(self, bot):
        self.bot = bot
        with open('./data/auths.json') as f:
            auth = json.load(f)
            mongo_uri = auth.get('MONGODB')
        mongo = AsyncIOMotorClient(mongo_uri)
        self.db = mongo.RemixBot

    def get_attr(self, type: str, attr: str):
        return soup.find(type, class_=attr).text

    def get_all_attrs(self, type: str, attr: str):
        return soup.find_all(type, class_=attr)

    async def get_tag(self, userid):
        result = await self.db.brawlstars.find_one({'_id': userid})
        if not result:
            return 'None'
        return result['tag']

    async def save_tag(self, userid, tag):
        await self.db.brawlstars.update_one({'_id': userid}, {'$set': {'_id': userid, 'tag': tag}}, upsert=True)

    def check_tag(self, tag):
        for char in tag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False
        return True

    @commands.group(invoke_without_command=True)
    async def bs(self, ctx):
        '''Command group for all BrawlStars commands.'''
        await ctx.send(f'Commands:\n`{ctx.prefix}bs save <tag>` Saves a tag to your profile.\n`{ctx.prefix}bs profile [tag]` Get a brawl stars profile.\n`{ctx.prefix}bs weburl [tag]` Get the url for more info on a profile.\n`{ctx.prefix}bs band [tag]` Get information about a band. If no tag is specified it will default to the band you are in.')

    @bs.command()
    async def profile(self, ctx, id=None):
        '''Get a brawl stars profile.'''

        # ID is the player tag
        # Also I probably could have done the same thing with less lines
        await ctx.trigger_typing()

        def get_attr(type: str, attr: str):
            return soup.find(type, class_=attr).text

        def get_all_attrs(type: str, attr: str):
            return soup.find_all(type, class_=attr)

        if not id:
            id = await self.get_tag(str(ctx.message.author.id))
            id = id.strip('#').replace('O', '0')
            if id == 'None':
                return await ctx.send(f"Please save your player tag using `{ctx.prefix}bs save <tag>`")
            else:
                if self.check_tag(id):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                                data = await resp.read()
                        soup = BeautifulSoup(data, 'lxml')
                    except Exception as e:
                        await ctx.send(f'`{e}`')
                    else:
                        success = True

                else:
                    return await ctx.send("You have an invalid tag.")
        else:
            id = id.strip('#').replace('O', '0')
            if self.check_tag(id):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(e)
                else:
                    success = True
            else:
                await ctx.send("Invalid tag. Tags can only contain the following characters: `0289PYLQGRJCUV`")
        if success:
            source = str(soup.find_all("img", class_="mr-2"))
            src = source.split('src="')[1]
            imgpath = src.split('" w')[0]

            brawlers = get_all_attrs("div", "brawlers-brawler-slot d-inline-block")
            top = str(brawlers[0])
            name_after = top.split('brawlers/')[1]
            highestbrawler = name_after.split('"')[0].title()

            em = discord.Embed(color=discord.Color(value=0x00FF00))
            em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
            em.title = f"{get_attr('div', 'player-name brawlstars-font')} (#{id})"
            em.description = f"Band: {get_attr('div', 'band-name mr-2')} ({get_attr('div', 'band-tag')})"
            em.add_field(name="Level", value=get_attr('div', 'experience-level'))
            em.add_field(name="Experience", value=get_attr('div', 'progress-text'))
            em.add_field(name="Trophies", value=get_all_attrs('div', 'trophies')[0].text)
            em.add_field(name="Highest Trophies", value=get_all_attrs('div', 'trophies')[1].text)
            em.add_field(name="Highest Brawler", value=highestbrawler)
            em.add_field(name="Highest Brawler Trophies", value=get_all_attrs('div', 'trophies')[2].text)
            em.add_field(name="Victories", value=get_attr('div', 'victories'))
            em.add_field(name="Showdown Victories", value=get_attr('div', 'showdown-victories'))
            em.add_field(name="Best time as boss", value=get_attr('div', 'boss-time'))
            em.add_field(name="Best robo rumble time", value=get_attr('div', 'robo-time'))
            await ctx.send(embed=em)

    @bs.command()
    async def save(self, ctx, id=None):
        '''Save a tag.'''
        if not id:
            await ctx.send("Please specify a tag to save.")
        else:
            id = id.strip('#').replace('O', '0')
            if self.check_tag(id):
                await self.save_tag(str(ctx.author.id), id)
                await ctx.send(f'Your tag (#{id}) has been successfully saved.')
            else:
                await ctx.send("Your tag is invalid. Please make sure you only have the characters `0289PYLQGRJCUV` in the tag.")

    @bs.command()
    async def weburl(self, ctx, id=None):
        await ctx.trigger_typing()
        em = discord.Embed(title='brawlstats.io URL')
        em.color = discord.Color(value=0x00ff00)
        if id is None:
            if await self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}brawlstars save <tag>` to save a tag to your discord profile.')
            id = await self.get_tag(str(ctx.author.id))
        else:
            if not self.check_tag(id.strip('#').replace('O', '0')):
                return await ctx.send('Invalid Tag. Please make sure your tag is correct.')
            id = id.strip('#').replace('O', '0')

        em.url = f'http://brawlstats.io/players/{id}'
        em.title = ctx.author.name
        em.add_field(name='URL', value=f'http://brawlstats.io/players/{id}')
        em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats',
                      icon_url='http://brawlstats.io/images/bs-stats.png')

        await ctx.send(embed=em)

    @bs.command()
    async def band(self, ctx, id=None):
        def get_attr(type: str, attr: str):
            return soup.find(type, class_=attr).text

        def get_all_attrs(type: str, attr: str):
            return soup.find_all(type, class_=attr)

        await ctx.trigger_typing()
        if id is None:
            if await self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}bs save <tag>` to save a tag to your discord profile.')
            else:
                id = await self.get_tag(str(ctx.author.id))
                # get player stats
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(f'`{e}`')
                bandtag = get_attr('div', 'band-tag').strip("#")
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/bands/{bandtag}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(f'`{e}`')

                name = str(get_attr('div', 'name'))
                desc = str(get_attr('div', 'clan-description'))

                totaltrophiesbeta = str(get_all_attrs('div', 'trophies')[0]).split(">")
                totaltrophiesgamma = totaltrophiesbeta[1].split("<")
                totaltrophies = totaltrophiesgamma[0]
                reqdtrophiesbeta = str(get_all_attrs('div', 'trophies')[1]).split(">")
                reqdtrophiesgamma = reqdtrophiesbeta[1].split("<")
                reqdtrophies = reqdtrophiesgamma[0]

                memberonenamealpha = str(get_all_attrs('tr', 'jumpc')[0])
                memberonenamebeta = memberonenamealpha.split('<div class="name">')
                memberonenamegamma = memberonenamebeta[1].split('</div><div class="clan">')
                memberonename = memberonenamegamma[0]
                memberonerankbeta = memberonenamegamma[1].split('</div></div><div class="trophy-count">')
                memberonerank = memberonerankbeta[0]
                memberonetrophybeta = memberonerankbeta[1]
                memberonetrophygamma = memberonetrophybeta.split("</div>")
                memberonetrophy = memberonetrophygamma[0]

                membertwonamealpha = str(get_all_attrs('tr', 'jumpc')[1])
                membertwonamebeta = membertwonamealpha.split('<div class="name">')
                membertwonamegamma = membertwonamebeta[1].split('</div><div class="clan">')
                membertwoname = membertwonamegamma[0]
                membertworankbeta = membertwonamegamma[1].split('</div></div><div class="trophy-count">')
                membertworank = membertworankbeta[0]
                membertwotrophybeta = membertworankbeta[1]
                membertwotrophygamma = membertwotrophybeta.split("</div>")
                membertwotrophy = membertwotrophygamma[0]

                memberthreenamealpha = str(get_all_attrs('tr', 'jumpc')[2])
                memberthreenamebeta = memberthreenamealpha.split('<div class="name">')
                memberthreenamegamma = memberthreenamebeta[1].split('</div><div class="clan">')
                memberthreename = memberthreenamegamma[0]
                memberthreerankbeta = memberthreenamegamma[1].split('</div></div><div class="trophy-count">')
                memberthreerank = memberthreerankbeta[0]
                memberthreetrophybeta = memberthreerankbeta[1]
                memberthreetrophygamma = memberthreetrophybeta.split("</div>")
                memberthreetrophy = memberthreetrophygamma[0]

                memberfournamealpha = str(get_all_attrs('tr', 'jumpc')[3])
                memberfournamebeta = memberfournamealpha.split('<div class="name">')
                memberfournamegamma = memberfournamebeta[1].split('</div><div class="clan">')
                memberfourname = memberfournamegamma[0]
                memberfourrankbeta = memberfournamegamma[1].split('</div></div><div class="trophy-count">')
                memberfourrank = memberfourrankbeta[0]
                memberfourtrophybeta = memberfourrankbeta[1]
                memberfourtrophygamma = memberfourtrophybeta.split("</div>")
                memberfourtrophy = memberfourtrophygamma[0]

                text = str(get_attr('div', 'board-header my-3'))
                thing = text.split(' ')
                members = thing[2].strip('(')

                source = str(get_all_attrs('div', 'badge'))
                src = source.split('src="')[1]
                imgpathbeta = src.split('" w')[0]
                imgpath = imgpathbeta.split('"')[0]

                em = discord.Embed(color=discord.Color(value=0x00FF00))
                em.title = name + " (#" + bandtag + ")"
                em.description = desc
                em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                em.add_field(name="Total trophies", value=totaltrophies)
                em.add_field(name="Required trophies", value=reqdtrophies)

                em2 = discord.Embed(color=discord.Color(value=0x00FF00))
                em2.title = "Top members"
                em2.description = "This is calculated through total trophy count."
                em2.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                em2.add_field(name=memberonename, value=memberonerank + "\n" + memberonetrophy)
                em2.add_field(name=membertwoname, value=membertworank + "\n" + membertwotrophy)
                em2.add_field(name=memberthreename, value=memberthreerank + "\n" + memberthreetrophy)
                em2.add_field(name=memberfourname, value=memberfourrank + "\n" + memberfourtrophy)

                await ctx.send(embed=em)
                await ctx.send(embed=em2)

        else:
            # don't want to fix indentation level
            try:
                # Get ID
                # get player stats
                bandtag = id.strip('#')
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/bands/{bandtag}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(f'`{e}`')

                name = str(get_attr('div', 'name'))
                desc = str(get_attr('div', 'clan-description'))

                totaltrophiesbeta = str(get_all_attrs('div', 'trophies')[0]).split(">")
                totaltrophiesgamma = totaltrophiesbeta[1].split("<")
                totaltrophies = totaltrophiesgamma[0]
                reqdtrophiesbeta = str(get_all_attrs('div', 'trophies')[1]).split(">")
                reqdtrophiesgamma = reqdtrophiesbeta[1].split("<")
                reqdtrophies = reqdtrophiesgamma[0]

                memberonenamealpha = str(get_all_attrs('tr', 'jumpc')[0])
                memberonenamebeta = memberonenamealpha.split('<div class="name">')
                memberonenamegamma = memberonenamebeta[1].split('</div><div class="clan">')
                memberonename = memberonenamegamma[0]
                memberonerankbeta = memberonenamegamma[1].split('</div></div><div class="trophy-count">')
                memberonerank = memberonerankbeta[0]
                memberonetrophybeta = memberonerankbeta[1]
                memberonetrophygamma = memberonetrophybeta.split("</div>")
                memberonetrophy = memberonetrophygamma[0]

                membertwonamealpha = str(get_all_attrs('tr', 'jumpc')[1])
                membertwonamebeta = membertwonamealpha.split('<div class="name">')
                membertwonamegamma = membertwonamebeta[1].split('</div><div class="clan">')
                membertwoname = membertwonamegamma[0]
                membertworankbeta = membertwonamegamma[1].split('</div></div><div class="trophy-count">')
                membertworank = membertworankbeta[0]
                membertwotrophybeta = membertworankbeta[1]
                membertwotrophygamma = membertwotrophybeta.split("</div>")
                membertwotrophy = membertwotrophygamma[0]

                memberthreenamealpha = str(get_all_attrs('tr', 'jumpc')[2])
                memberthreenamebeta = memberthreenamealpha.split('<div class="name">')
                memberthreenamegamma = memberthreenamebeta[1].split('</div><div class="clan">')
                memberthreename = memberthreenamegamma[0]
                memberthreerankbeta = memberthreenamegamma[1].split('</div></div><div class="trophy-count">')
                memberthreerank = memberthreerankbeta[0]
                memberthreetrophybeta = memberthreerankbeta[1]
                memberthreetrophygamma = memberthreetrophybeta.split("</div>")
                memberthreetrophy = memberthreetrophygamma[0]

                memberfournamealpha = str(get_all_attrs('tr', 'jumpc')[3])
                memberfournamebeta = memberfournamealpha.split('<div class="name">')
                memberfournamegamma = memberfournamebeta[1].split('</div><div class="clan">')
                memberfourname = memberfournamegamma[0]
                memberfourrankbeta = memberfournamegamma[1].split('</div></div><div class="trophy-count">')
                memberfourrank = memberfourrankbeta[0]
                memberfourtrophybeta = memberfourrankbeta[1]
                memberfourtrophygamma = memberfourtrophybeta.split("</div>")
                memberfourtrophy = memberfourtrophygamma[0]

                text = str(get_attr('div', 'board-header my-3'))
                thing = text.split(' ')
                members = thing[2].strip('(')

                source = str(get_all_attrs('div', 'badge'))
                src = source.split('src="')[1]
                imgpathbeta = src.split('" w')[0]
                imgpath = imgpathbeta.split('"')[0]

                em = discord.Embed(color=discord.Color(value=0x00FF00))
                em.title = name + " (#" + bandtag + ")"
                em.description = desc
                em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                em.add_field(name="Total trophies", value=totaltrophies)
                em.add_field(name="Required trophies", value=reqdtrophies)

                em2 = discord.Embed(color=discord.Color(value=0x00FF00))
                em2.title = "Top members"
                em2.description = "This is calculated through total trophy count."
                em2.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                em2.add_field(name=memberonename, value=memberonerank + "\n" + memberonetrophy)
                em2.add_field(name=membertwoname, value=membertworank + "\n" + membertwotrophy)
                em2.add_field(name=memberthreename, value=memberthreerank + "\n" + memberthreetrophy)
                em2.add_field(name=memberfourname, value=memberfourrank + "\n" + memberfourtrophy)

                await ctx.send(embed=em)
                await ctx.send(embed=em2)

            except Exception as e:
                await ctx.send("This tag is invalid. Make sure that you have a band tag, not a player tag, and that it only contains the characters `0289PYLQGRJCUV`.")
                await ctx.send(e)

    @bs.command()
    async def events(self, ctx, when=None):
        '''Information about events.'''

        url = 'https://brawlstats.io/events/'

        def get_attr(type: str, attr: str):
            return soup.find(type, class_=attr).text

        def get_all_attrs(type: str, attr: str):
            return soup.find_all(type, class_=attr)

        now = datetime.datetime.now(pytz.UTC)
        now = now.astimezone(pytz.timezone("US/Pacific"))
        dayofwk = int(now.weekday()) + 1

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
        soup = BeautifulSoup(data, 'lxml')

        em = discord.Embed(color=discord.Color(value=0x00FF00))
        em2 = discord.Embed(color=discord.Color(value=0x00FF00))

        if when is None:
            await ctx.send(f'Commands:\n`{ctx.prefix}bs events current` Get the events that are running right now.\n`{ctx.prefix}bs events upcoming` Get the events that are upcoming.\n`{ctx.prefix}bs events both` Get both at the same time! Man, science is so amazing.')
            return
        elif when == "current":
            await ctx.trigger_typing()
            if dayofwk in [1, 2, 3, 4, 5]:
                em.title = "Current events"
                j = 0
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i].text) + '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i].text), value=val)
                await ctx.send(embed=em)
            else:
                em.title = "Current events"
                j = 0
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i].text) + '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i].text), value=val)
                em.add_field(name=str(get_all_attrs('h4', 'card-title')[3].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[3].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em)
        elif when == "upcoming":
            await ctx.trigger_typing()
            j = 6
            if dayofwk in [1, 2, 3, 4, 5]:
                em2.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 3].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em2.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 3].text), value=val)

                em2.add_field(name=str(get_all_attrs('h4', 'card-title')[6].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[6].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em2)
            else:
                em2.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 4].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em2.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 4].text), value=val)
                em2.add_field(name=str(get_all_attrs('h4', 'card-title')[7].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[7].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em2)
        elif when == "both":
            await ctx.trigger_typing()
            if dayofwk in [1, 2, 3, 4, 5]:
                em.title = "Current events"
                j = 0
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i].text) + '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i].text), value=val)

                em2.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 3].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em2.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 3].text), value=val)

                em2.add_field(name=str(get_all_attrs('h4', 'card-title')[6].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[6].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')

                await ctx.send(embed=em)
                await ctx.send(embed=em2)
            else:
                em.title = "Current events"
                j = 0
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i].text) + '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i].text), value=val)
                em.add_field(name=str(get_all_attrs('h4', 'card-title')[3].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[3].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                em2.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 4].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em2.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 4].text), value=val)
                em2.add_field(name=str(get_all_attrs('h4', 'card-title')[7].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[7].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em)
                await ctx.send(embed=em2)
        else:
            await ctx.send(f'Commands:\n`{ctx.prefix}bs events current` Get the events that are running right now.\n`{ctx.prefix}bs events upcoming` Get the events that are upcoming.\n`{ctx.prefix}bs events both` Get both at the same time! Man, science is so amazing.')
            return


def setup(bot):
    bot.add_cog(BrawlStars(bot))
