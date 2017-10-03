from discord.ext import commands
from init import *


def validator(category):

    def predicate(ctx):
        ch_name = ctx.message.channel.name
        u_id = ctx.message.author.id

        return u_id in config["mods"] \
            or (category != "modonly"
                and ch_name in config[category]
                and u_id not in config["ignored"]
                and ch_name not in config["silenced"])

    return commands.check(predicate)


def logger(name, category, reaction):

    def wrap(f):

        @validator(category)
        async def wrapped(ctx, *args):
            log(name, ctx)
            if isinstance(reaction, list):
                for each in reaction:
                    await zote.add_reaction(ctx.message, reactions[each])
            else:
                await zote.add_reaction(ctx.message, reactions[reaction])
            await f(ctx, *args)
        return wrapped

    return wrap
