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
from bs4 import BeautifulSoup
from ext.paginator import PaginatorSession
import aiohttp
import datetime
import json
import pytz


class Brawl_Stars:
    '''Brawl Stars stats.'''

    def __init__(self, bot):
        self.bot = bot

    def emoji(self, emoji):
        with open('data/emojis.json') as f:
            emojis = json.load(f)
            e = emojis[emoji]
        return e

    async def get_tag(self, userid):
        result = await self.bot.db.brawlstars.find_one({'_id': userid})
        if not result:
            return 'None'
        return result['tag']

    async def save_tag(self, userid, tag):
        await self.bot.db.brawlstars.update_one({'_id': userid}, {'$set': {'_id': userid, 'tag': tag}}, upsert=True)

    def check_tag(self, tag):
        for char in tag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False
        return True

    @commands.command()
    async def bsprofile(self, ctx, id=None):
        '''Get a brawl stars profile.'''

        # ID is the player tag
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
                id = await self.get_tag(str(ctx.author.id))
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

            em = discord.Embed(color=discord.Color.green())
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
            em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats',
                          icon_url='http://brawlstats.io/images/bs-stats.png')
            await ctx.send(embed=em)

    @commands.command()
    async def bssave(self, ctx, id=None):
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

    @commands.command()
    async def bsweburl(self, ctx, id=None):
        '''Get the url to your brawl stars profile'''
        await ctx.trigger_typing()
        em = discord.Embed(title='brawlstats.io URL')
        em.color = discord.Color.green()
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

    @commands.command()
    async def bsband(self, ctx, id=None):
        '''Get a brawl stars band's stats'''
        def get_attr(type: str, attr: str):
            return soup.find(type, class_=attr).text

        def get_all_attrs(type: str, attr: str):
            return soup.find_all(type, class_=attr)

        await ctx.trigger_typing()
        if not id:
            id = await self.get_tag(str(ctx.message.author.id))
            id = id.strip('#').replace('O', '0')
            if id == 'None':
                return await ctx.send(f'Please save your player tag using `{ctx.prefix}bs save <tag>`')
            else:
                id = await self.get_tag(str(ctx.author.id))
                if self.check_tag(id):
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
                    else:
                        success = True
                else:
                    return await ctx.send("You have an invalid tag.")
        else:
            id = id.strip('#').replace('O', '0')
            if self.check_tag(id):
                bandtag = id.strip('#')
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/bands/{bandtag}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(f'`{e}`')
                else:
                    success = True
            else:
                await ctx.send("Invalid tag. Tags can only contain the following characters: `0289PYLQGRJCUV`")
        if success:
            pages = []
            name = str(get_attr('div', 'name'))
            desc = str(get_attr('div', 'clan-description'))

            trophies = get_all_attrs('div', 'trophies')[0].text
            required = get_all_attrs('div', 'trophies')[1].text

            n = 1
            r = 0
            t = 0
            info = []

            for i in range(4):
                player = {}
                player['name'] = get_all_attrs('div', 'name')[n].text
                player['role'] = get_all_attrs('div', 'clan')[r].text
                player['trophies'] = get_all_attrs('div', 'trophy-count')[t].text
                info.append(player)
                n += 1
                r += 1
                t += 1

            source = str(get_all_attrs('div', 'badge'))
            src = source.split('src="')[1]
            url = src.split('" w')[0]
            imgpath = url.split('"')[0]

            em = discord.Embed(color=discord.Color.green())
            em.title = f'{name} (#{bandtag})'
            em.description = desc
            em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
            em.add_field(name="Total trophies", value=trophies)
            em.add_field(name="Required trophies", value=required)
            em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
            pages.append(em)

            em = discord.Embed(color=discord.Color.green())
            em.title = "Top members"
            em.description = "This is calculated through total trophy count."
            em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
            em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
            for entry in info:
                em.add_field(name=entry['name'], value=f"{entry['role'].replace(' ', '-')}\n{entry['trophies']}")
            pages.append(em)

            p_session = PaginatorSession(ctx, footer=f'Stats made by Cree-Py | Powered by brawlstats', pages=pages)
            await p_session.run()

    @commands.command()
    async def bsevents(self, ctx, when=None):
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

        if when not in ('current', 'upcoming', 'both'):
            return await ctx.send(f'Usage: `{ctx.prefix}bsevents <current|upcoming|both>`')
        if when == "current":
            await ctx.trigger_typing()
            em = discord.Embed(color=discord.Color.green())
            em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats', icon_url='http://brawlstats.io/images/bs-stats.png')
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
                em = discord.Embed(color=discord.Color.green())
                em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats', icon_url='http://brawlstats.io/images/bs-stats.png')
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
            em = discord.Embed(color=discord.Color.green())
            em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats', icon_url='http://brawlstats.io/images/bs-stats.png')
            j = 6
            if dayofwk in [1, 2, 3, 4, 5]:
                em.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 3].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 3].text), value=val)

                em.add_field(name=str(get_all_attrs('h4', 'card-title')[6].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[6].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em)
            else:
                em.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 4].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 4].text), value=val)
                em.add_field(name=str(get_all_attrs('h4', 'card-title')[7].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[7].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                await ctx.send(embed=em)
        elif when == "both":
            em = discord.Embed(color=discord.Color.green())
            em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
            pages = []
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
                pages.append(em)

                em = discord.Embed(color=discord.Color.green())
                em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
                em.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 3].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 3].text), value=val)

                em.add_field(name=str(get_all_attrs('h4', 'card-title')[6].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[6].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                pages.append(em)

                p_session = PaginatorSession(ctx, footer='Stats made by Cree-Py | Powered by brawlstats', pages=pages)
                await p_session.run()
            else:
                em = discord.Embed(color=discord.Color.green())
                em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
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
                pages.append(em)

                em = discord.Embed(color=discord.Color.green())
                em.set_footer(icon_url='http://brawlstats.io/images/bs-stats.png')
                em.title = "Upcoming events"
                for i in range(3):
                    val = str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[i + 4].text)
                    val += '\n'
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins\n'
                    j += 1
                    val += str(get_all_attrs('div', 'card-map-coins')[j].text)
                    val += ' Coins'
                    j += 1
                    em.add_field(name=str(get_all_attrs('h4', 'card-title')[i + 4].text), value=val)
                em.add_field(name=str(get_all_attrs('h4', 'card-title')[7].text), value=str(get_all_attrs('h6', 'card-subtitle mb-2 text-muted')[7].text) + '\n' + str(get_attr('div', 'card-map-tickets')) + ' Tickets')
                pages.append(em)
                p_session = PaginatorSession(ctx, footer='Stats made by Cree-Py | Powered by brawlstats', pages=pages)
                await p_session.run()

    @commands.command()
    async def bsbrawlers(self, ctx, tag=None):
        '''Get the level and trophies of a players brawlers.'''
        def get_attr(type: str, attr: str):
            return soup.find(type, class_=attr).text

        def get_all_attrs(type: str, attr: str):
            return soup.find_all(type, class_=attr)

        await ctx.trigger_typing()

        if tag is None:
            tag = await self.get_tag(str(ctx.message.author.id))
            tag = tag.strip('#').replace('O', '0')
            if tag == 'None':
                return await ctx.send(f'You do not have a saved tag. Please save your player tag using `{ctx.prefix}bs save <tag>`')
            else:
                tag = await self.get_tag(str(ctx.author.id))
                if self.check_tag(tag):
                    # get player stats
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://brawlstats.io/players/{tag}') as resp:
                                data = await resp.read()
                        soup = BeautifulSoup(data, 'lxml')
                    except Exception as e:
                        await ctx.send(f'`{e}`')
                    else:
                        success = True
                else:
                    return await ctx.send("You have an invalid tag.")
        else:
            tag = tag.strip('#').replace('O', '0')
            if self.check_tag(tag):
                tag = tag.strip('#')
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/players/{tag}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(f'`{e}`')
                else:
                    success = True
            else:
                await ctx.send("Invalid tag. Tags can only contain the following characters: `0289PYLQGRJCUV`")

        if success:

            em = discord.Embed(color=discord.Color.green())
            everything = (str(get_all_attrs('div', 'brawlers-brawler-slot d-inline-block')))
            one = everything.split('url("')

            tobeprinted = ""

            for i in range(len(one) - 1):
                plist = one[i + 1].split('");";')
                tobeprinted += plist[0] + '\n'

            playername = get_attr('div', 'player-name brawlstars-font')
            playertag = "Q8P2ULP"

            imglist = tobeprinted.split('\n')
            em.title = "Brawlers"

            em.description = playername + " (#" + playertag + ")"

            for i in range(len(get_all_attrs('span', 'trophy-nr'))):

                tooprint = ""

                tooprint += str(get_all_attrs('span', 'lbskew-power-txt')[i].text + ' :cloud_lightning:') + '\n'

                tooprint += str(get_all_attrs('span', 'trophy-nr')[i].text) + ' ' + str(self.bot.get_emoji(self.emoji('bstrophy'))) + '\n'

                em.add_field(name=str(get_all_attrs('div', 'name')[i].text) + ' ' + str(self.bot.get_emoji(self.emoji(str(get_all_attrs('div', 'name')[i].text).replace(' ', '-').lower()))), value=tooprint)

            em.set_thumbnail(url=f'https://brawlstats.io{str(imglist[0])}')
            em.set_footer(text='Stats made by Cree-Py | Powered by brawlstats',
                          icon_url='http://brawlstats.io/images/bs-stats.png')
            try:
                await ctx.send(embed=em)
            except Exception as e:
                print(e)
                await ctx.send(e)


def setup(bot):
    bot.add_cog(Brawl_Stars(bot))
