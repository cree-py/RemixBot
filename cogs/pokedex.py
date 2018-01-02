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

# Import dependencies
import discord
from discord.ext import commands
import json
import aiohttp
import random

class Pokedex:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def pokemon(self, ctx):
        '''Base group for pokemon commands.'''
        await ctx.send("TODO: list pokemon commands")
        
    @pokemon.command()
    async def random(self, ctx):
        '''Get stats about a random pokemon.'''
        num = random.randint(1, 721)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/pokemon/{num}/') as resp:
                data = await resp.json()
                id = data['id']
                em = discord.Embed(color=discord.Color(value=0x00FF00))
                em.title = data['name'].title()
                em.set_thumbnail(url=data['sprites']['front_default'])
                em.add_field(name="Height", value=str(data['height']/10) + ' meters')
                em.add_field(name="Weight", value=str(data['weight']/10) + ' kilograms')
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
        async with aiohttp.ClientSession() as session:
            async with session.get('https://pokeapi.co/api/v2/pokedex/national/') as resp:
                data = await resp.json()
                pokedex = data['pokemon_entries'][id-1]['pokemon_species']['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(pokedex) as resp:
                data = await resp.json()
                for i in range(len(data['flavor_text_entries'])):
                    if data['flavor_text_entries'][i]['language']['name'] == "en":
                        description = data['flavor_text_entries'][i]['flavor_text']
                        break
                    else:
                        pass       
                em.description=description
        await ctx.send(embed=em)
        
    @pokemon.command()
    async def info(self, ctx, pokemon):
        '''Get stats about a pokemon. You can specify either its pokedex number or name.'''
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon}/') as resp:
                    data = await resp.json()
                    id = data['id']
                    em = discord.Embed(color=discord.Color(value=0x00FF00))
                    em.title = data['name'].title()
                    em.set_thumbnail(url=data['sprites']['front_default'])
                    em.add_field(name="Height", value=str(data['height']/10) + ' meters')
                    em.add_field(name="Weight", value=str(data['weight']/10) + ' kilograms')
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
            async with aiohttp.ClientSession() as session:
                async with session.get('https://pokeapi.co/api/v2/pokedex/national/') as resp:
                    data = await resp.json()
                    pokedex = data['pokemon_entries'][id-1]['pokemon_species']['url']
            async with aiohttp.ClientSession() as session:
                async with session.get(pokedex) as resp:
                    data = await resp.json()
                    for i in range(len(data['flavor_text_entries'])):
                        if data['flavor_text_entries'][i]['language']['name'] == "en":
                            description = data['flavor_text_entries'][i]['flavor_text']
                            break
                        else:
                            pass       
                    em.description=description
            await ctx.send(embed=em)
        except:
            await ctx.send("That is not a valid pokemon name or pokedex number. Please check your spelling or note that no Gen 7 pokemon are included in pokeapi.")

def setup(bot):
    bot.add_cog(Pokedex(bot))
