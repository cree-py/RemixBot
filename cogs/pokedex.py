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
import aiohttp
import random
from bs4 import BeautifulSoup
from ext.paginator import PaginatorSession


class Pokedex:
    '''Pokemon cog for pokedex entries.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['prandom', 'pokemonrandom'])
    async def pokerandom(self, ctx):
        '''Get stats about a random pokemon.'''
        await ctx.trigger_typing()
        num = random.randint(1, 721)
        pages = []
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/pokemon/{num}/') as resp:
                data = await resp.json()
                pokemonname = data['name']
                id = data['id']
                em = discord.Embed(color=discord.Color.green())
                em.title = data['name'].title()
                em.set_thumbnail(url=data['sprites']['front_default'])
                em.add_field(name="Height", value=str(data['height'] / 10) + ' meters')
                em.add_field(name="Weight", value=str(data['weight'] / 10) + ' kilograms')
                j = 0
                abilities = ""
                for i in range(len(data['abilities'])):
                    abilities += data['abilities'][i]['ability']['name'].title().replace('-', ' ') + "\n"
                    j += 1
                if j == 1:
                    em.add_field(name="Ability", value=abilities)
                else:
                    em.add_field(name="Abilities", value=abilities)
                types = ""
                j = 0
                for i in range(len(data['types'])):
                    types += data['types'][i]['type']['name'].title().replace('-', ' ') + "\n"
                    j += 1
                if j == 1:
                    em.add_field(name="Type", value=types)
                else:
                    em.add_field(name="Types", value=types)
                for i in range(len(data['stats'])):
                    name = data['stats'][i]['stat']['name'].title().replace('-', ' ')
                    if name == "Hp":
                        name = "HP"
                    em.add_field(name=name, value=data['stats'][i]['base_stat'])

        async with aiohttp.ClientSession() as session:
            async with session.get('https://pokeapi.co/api/v2/pokedex/national/') as resp:
                data = await resp.json()
                pokedex = data['pokemon_entries'][id - 1]['pokemon_species']['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(pokedex) as resp:
                data = await resp.json()
                for i in range(len(data['flavor_text_entries'])):
                    if data['flavor_text_entries'][i]['language']['name'] == "en":
                        description = data['flavor_text_entries'][i]['flavor_text']
                        break
                    else:
                        pass
                em.description = description
        pages.append(em)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/pokemon/{num}/') as resp:
                data = await resp.json()
                moves = ""
                tooMany = False
                for i in range(len(data['moves'])):
                    if not i == 0:
                        moves += ", "
                    if len(moves) < 1024:
                        moves += data['moves'][i]['move']['name'].title().replace('-', ' ')
                    else:
                        tooMany = True
        if tooMany:
            moves = "Sorry, this pokemon knows too many moves to be displayed within this embed."
        em = discord.Embed(color=discord.Color.green())
        em.add_field(name="Learnable Moves", value=moves)
        em.set_thumbnail(url=data['sprites']['back_default'])
        pages.append(em)

        em = discord.Embed(color=discord.Color.green())
        em.set_image(url=f'https://raw.githubusercontent.com/110Percent/beheeyem-data/master/gifs/{pokemonname}.gif')
        em.title=pokemonname.title()
        pages.append(em)

        p_session = PaginatorSession(ctx, pages=pages)
        await p_session.run()

    @commands.command(aliases=['pinfo', 'pokemoninfo'])
    async def pokeinfo(self, ctx, pokemon):
        '''Get stats about a pokemon. You can specify either its pokedex number or name.'''
        await ctx.trigger_typing()
        pages = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon}/') as resp:
                    data = await resp.json()
                    id = data['id']
                    pokemonname = data['name']
                    em = discord.Embed(color=discord.Color.green())
                    em.title = data['name'].title()
                    em.set_thumbnail(url=data['sprites']['front_default'])
                    em.add_field(name="Height", value=str(data['height'] / 10) + ' meters')
                    em.add_field(name="Weight", value=str(data['weight'] / 10) + ' kilograms')
                    j = 0
                    abilities = ""
                    for i in range(len(data['abilities'])):
                        abilities += data['abilities'][i]['ability']['name'].title().replace('-', ' ') + "\n"
                        j += 1
                    if j == 1:
                        em.add_field(name="Ability", value=abilities)
                    else:
                        em.add_field(name="Abilities", value=abilities)
                    types = ""
                    j = 0
                    for i in range(len(data['types'])):
                        types += data['types'][i]['type']['name'].title().replace('-', ' ') + "\n"
                        j += 1
                    if j == 1:
                        em.add_field(name="Type", value=types)
                    else:
                        em.add_field(name="Types", value=types)
                    for i in range(len(data['stats'])):
                        name = data['stats'][i]['stat']['name'].title().replace('-', ' ')
                        if name == "Hp":
                            name = "HP"
                        em.add_field(name=name, value=data['stats'][i]['base_stat'])
                        
            async with aiohttp.ClientSession() as session:
                async with session.get('https://pokeapi.co/api/v2/pokedex/national/') as resp:
                    data = await resp.json()
                    pokedex = data['pokemon_entries'][id - 1]['pokemon_species']['url']
            async with aiohttp.ClientSession() as session:
                async with session.get(pokedex) as resp:
                    data = await resp.json()
                    for i in range(len(data['flavor_text_entries'])):
                        if data['flavor_text_entries'][i]['language']['name'] == "en":
                            description = data['flavor_text_entries'][i]['flavor_text']
                            break
                        else:
                            pass
                    em.description = description
            pages.append(em)
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon}/') as resp:
                    data = await resp.json()
                    moves = ""
                    tooMany = False
                    for i in range(len(data['moves'])):
                        if not i == 0:
                            moves += ", "
                        if len(moves) < 1024:
                            moves += data['moves'][i]['move']['name'].title().replace('-', ' ')
                        else:
                            tooMany = True
            if tooMany:
                moves = "Sorry, this pokemon knows too many moves to be displayed within this embed."
            em = discord.Embed(color=discord.Color.green())

            em.add_field(name="Learnable Moves", value=moves)
            em.set_thumbnail(url=data['sprites']['back_default'])
            pages.append(em)

            em = discord.Embed(color=discord.Color.green())
            em.set_image(url=f'https://raw.githubusercontent.com/110Percent/beheeyem-data/master/gifs/{pokemonname}.gif')
            em.title=pokemonname.title()
            pages.append(em)

            p_session = PaginatorSession(ctx, pages=pages)
            await p_session.run()
        except Exception as e:
            await ctx.send("That is not a valid pokemon name or pokedex number. Please check your spelling or note that no Gen 7 pokemon are included in pokeapi.")
            await ctx.send(e)

    @commands.command(aliases=['pmove', 'pokemonmove'])
    async def pokemove(self, ctx, *, move):
        '''Get information about a pokemon move.
        Accepts name of the move or its pokeapi.co ID.'''
        await ctx.trigger_typing()
        urlmove = move.lower().replace(' ', '-')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://pokeapi.co/api/v2/move/{urlmove}/') as resp:
                    data = await resp.json()
                    em = discord.Embed(color=discord.Color.green())
                    em.title = data['name'].title().replace('-', ' ')
                    em.add_field(name="Accuracy", value=data['accuracy'])
                    em.add_field(name="PP", value=data['pp'])
                    em.add_field(name="Priority", value=data['priority'])
                    em.add_field(name="Damage", value=data['power'])
                    em.add_field(name="Type", value=data['type']['name'].title())
                    for i in range(len(data['flavor_text_entries'])):
                        if data['flavor_text_entries'][i]['language']['name'] == "en":
                            description = data['flavor_text_entries'][i]['flavor_text']
                            break
                        else:
                            pass
                    type = data['type']['name']
                    em.description = description.replace('\n', ' ')
                    em.set_thumbnail(url=f'https://raw.githubusercontent.com/cree-py/remixweb/master/assets/{type}.png')
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("That is not a valid move name or ID. Please check your spelling or note that no Gen 7 moves are included in pokeapi.")
            await ctx.send(e)

    @commands.command(aliases=['pfusion', 'pokemonfusion'])
    async def pokefusion(self, ctx):
        '''Get a pokemon fusion.'''
        async with aiohttp.ClientSession() as session:
            async with session.get('http://pokemon.alexonsager.net/') as resp:
                data = await resp.read()
        soup = BeautifulSoup(data, 'lxml')
        em = discord.Embed(color=discord.Color.green())
        em.title = soup.find('div', class_='title').text
        em.set_image(url=str(soup.find_all('img')[0].get('src')))
        await ctx.send(embed=em)

    @commands.command(aliases=['ptype', 'pokemontype'])
    async def poketype(self, ctx, ptype=None):
        '''Get information about a type.'''
        if ptype is None:
            return await ctx.send("Specify a type to get information about!")

        ptype = ptype.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/type/{ptype}') as resp:
                data = await resp.json()

        em = discord.Embed(color=discord.Color.green())
        em.title = data['name'].title()
        ptypename = data['name']
        em.set_thumbnail(url=f'https://raw.githubusercontent.com/cree-py/remixweb/master/assets/{ptypename}.png')

        if data['damage_relations']['half_damage_from']:
            halfdamagefrom = ""
            for i in range(len(data['damage_relations']['half_damage_from'])):
                halfdamagefrom += data['damage_relations']['half_damage_from'][i]['name'].title() + '\n'
            em.add_field(name="Half Damage From", value=halfdamagefrom)

        if data['damage_relations']['double_damage_from']:
            doubledamagefrom = ""
            for i in range(len(data['damage_relations']['double_damage_from'])):
                doubledamagefrom += data['damage_relations']['double_damage_from'][i]['name'].title() + '\n'
            em.add_field(name="Double Damage From", value=doubledamagefrom)

        if data['damage_relations']['no_damage_from']:
            nodamagefrom = ""
            for i in range(len(data['damage_relations']['no_damage_from'])):
                nodamagefrom += data['damage_relations']['no_damage_from'][i]['name'].title() + '\n'
            em.add_field(name="No Damage From", value=nodamagefrom)

        if data['damage_relations']['half_damage_to']:
            halfdamageto = ""
            for i in range(len(data['damage_relations']['half_damage_to'])):
                halfdamageto += data['damage_relations']['half_damage_to'][i]['name'].title() + '\n'
            em.add_field(name="Half Damage To", value=halfdamageto)

        if data['damage_relations']['double_damage_to']:
            doubledamageto = ""
            for i in range(len(data['damage_relations']['double_damage_to'])):
                doubledamageto += data['damage_relations']['double_damage_to'][i]['name'].title() + '\n'
            em.add_field(name="Double Damage To", value=doubledamageto)

        if data['damage_relations']['no_damage_to']:
            nodamageto = ""
            for i in range(len(data['damage_relations']['no_damage_to'])):
                nodamageto += data['damage_relations']['no_damage_to'][i]['name'].title() + '\n'
            em.add_field(name="No Damage To", value=nodamageto)

        await ctx.send(embed=em)

    @commands.command(aliases=['pitem', 'pokemonitem'])
    async def pokeitem(self, ctx, *, item=None):
        if item is None:
            return await ctx.send("Please tell me what item you want information about!")

        item = item.replace(' ', '-').lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/item/{item}') as resp:
                data = await resp.json()

        em = discord.Embed(color=discord.Color.green())

        name = data['name']
        cost = int(data['cost']) or "N/A"

        for i in range(len(data['flavor_text_entries'])):
            if data['flavor_text_entries'][i]['language']['name'] == "en":
                description = data['flavor_text_entries'][i]['text']
                break
            else:
                pass
        em.description = description

        name = name.replace('-', ' ')
        name = name.title()
        em.title = name

        category = data['category']['name']
        category = category.replace('-', ' ')
        category = category.title()
        em.add_field(name="Category", value=category)

        em.add_field(name="Cost", value=str(cost))

        name = name.replace(' ', '-')
        name = name.lower()

        em.set_thumbnail(url=f"https://raw.githubusercontent.com/110Percent/beheeyem-data/master/sprites/items/{name}.png")

        await ctx.send(embed=em)

    @commands.command(aliases=['pability', 'pokemonability'])
    async def pokeability(self, ctx, *, ability=None):
        if ability is None:
            return await ctx.send("Please tell me what item you want information about!")
        ability = ability.replace(' ', '-').lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/ability/{ability}') as resp:
                data = await resp.json()

        em = discord.Embed(color=discord.Color.green())
        name = data['name'].replace('-', ' ').title()

        for i in range(len(data['flavor_text_entries'])):
            if data['flavor_text_entries'][i]['language']['name'] == "en":
                description = data['flavor_text_entries'][i]['flavor_text']
                break
            else:
                pass
        em.description = description
        em.title = name
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Pokedex(bot))