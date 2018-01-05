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
import aiohttp
from bs4 import BeautifulSoup
import json

class BrawlStars:

    # Methods

    # Constructor
    def __init__(self, bot):
        self.bot = bot

    # Get attr using beautiful soup
    def get_attr(type: str, attr: str):
        return soup.find(type, class_=attr).text

    # Get all matches into soup
    def get_all_attrs(type: str, attr: str):
        return soup.find_all(type, class_=attr)

    # Get player tag from json
    def get_tag(self, userid):
        with open('./data/tags/tags.json') as f:
            config = json.load(f)
            try:
                tag = config[userid]
            except KeyError:
                return 'None'
        return tag

    # Save a tag
    def save_tag(self, userid, tag):
        with open('./data/tags/tags.json', 'r+') as f:
            config = json.load(f)
            f.seek(0)
            config[userid] = tag
            json.dump(config, f, indent=4)

    # Check validity of tag
    def check_tag(self, tag):
        for char in tag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False
        return True

    # Commands

    @commands.group(invoke_without_command=True)
    async def brawlstars(self, ctx):
        '''Command group for all BrawlStars commands.'''
        await ctx.send('TODO: brawlstars commands')

    @brawlstars.command()
    async def profile(self, ctx, id="notagspecified"):
        '''Get your profile.'''

        # ID is the player tag, I just screwed up naming the variables
        # Also, since the other variable names are also horrible:
        # lol, newstr, newerstr, and neweststr are all either
        # useless strings or lists I made to get to oimgpath since
        # I'm a noob. test, div, newdiv, newerdiv, and newestdiv
        # are the same except for highestbrawler. 
        # Also I probably could have done the same thing with less lines
        # but whatever

        await ctx.trigger_typing()

        if id == "notagspecified":
            id = self.get_tag(str(ctx.message.author.id)).strip('#').replace('O', '0')
            if id is None:
                await ctx.send("Um... what the heck are you trying to do?")
            else:
                if self.check_tag(id):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                                data = await resp.read()
                        soup = BeautifulSoup(data, 'lxml')

                        lol = (str(soup.find_all("img", class_="mr-2")))
                        newstr = lol.split('src="')
                        newerstr = newstr[1]
                        neweststr = newerstr.split('" w')
                        imgpath = neweststr[0]
                        
                        test = get_all_attrs("div", "brawlers-brawler-slot d-inline-block")
                        div = str(test[0])
                        newdiv = div.split('brawlers/')
                        newerdiv = newdiv[1]
                        newestdiv = newerdiv.split('"')
                        highestbrawler = newestdiv[0].title()

                        em = discord.Embed(color=discord.Color(value=0x00FF00))
                        em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                        em.title = get_attr('div', 'player-name brawlstars-font') + " (#" + id + ")"
                        em.description = "Band: " + get_attr('div', 'band-name mr-2') + " (" + get_attr('div', 'band-tag') + ")"
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
                    except:
                        # Haha you got me I'm lazy
                        await ctx.send("An unknown error occured.")
                else:
                    await ctx.send("You have an invalid tag saved. Which shouldn't happen.")
        else:
            # remove # and replace O with 0
            id = id.strip('#').replace('O', '0')
            if self.check_tag(id):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')

                    lol = (str(soup.find_all("img", class_="mr-2")))
                    newstr = lol.split('src="')
                    newerstr = newstr[1]
                    neweststr = newerstr.split('" w')
                    imgpath = neweststr[0]

                    test = get_all_attrs("div", "brawlers-brawler-slot d-inline-block")
                    div = str(test[0])
                    newdiv = div.split('brawlers/')
                    newerdiv = newdiv[1]
                    newestdiv = newerdiv.split('"')
                    highestbrawler = newestdiv[0].title()

                    em = discord.Embed(color=discord.Color(value=0x00FF00))
                    em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
                    em.title = get_attr('div', 'player-name brawlstars-font') + " (#" + id + ")"
                    em.description = "Band: " + get_attr('div', 'band-name mr-2') + " (" + get_attr('div', 'band-tag') + ")"
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
                except:
                    # Haha you got me I'm lazy
                    await ctx.send("An unknown error occured.")
            else:
                await ctx.send("Invalid tag. Tags can only contain the following characters: ```0289PYLQGRJCUV```")
                await ctx.send("Please check your tag and try again.")

    @brawlstars.command()
    async def save(self, ctx, id=None):
        '''Save a tag.'''
        if id is None:
            await ctx.send("Please specify a tag to save.")
        else:
            id = id.strip('#').replace('O', '0')
            if self.check_tag(id):
                self.save_tag(str(ctx.author.id), id)
                await ctx.send(f'Your tag (#{id}) has been successfully saved.')
            else:
                await ctx.send("Your tag is invalid. Please make sure you only have the characters `0289PYLQGRJCUV` in the tag.")

    @brawlstars.command()
    async def weburl(self, ctx, id=None):
        await ctx.trigger_typing()
        em = discord.Embed(title='brawlstats.io URL')
        em.color = discord.Color(value=0x00ff00)
        if id is None:
            if self.get_tag(str(ctx.author.id)) == 'None':
                return await ctx.send(f'No tag found. Please use `{ctx.prefix}brawlstars save <tag>` to save a tag to your discord profile.')
            id = self.get_tag(str(ctx.author.id))
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

def setup(bot):
    bot.add_cog(BrawlStars(bot))
