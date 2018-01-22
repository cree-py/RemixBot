from discord.ext import commands
import json


def developer():
    def wrapper(ctx):
        with open('data/devs.json') as f:
            devs = json.load(f)
        if ctx.author.id in devs:
            return True
        return False
    return commands.check(wrapper)
