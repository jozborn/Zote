import os.path
import random as random_builtin
from discord.ext import commands

# This line references the application token
# without revealing it on Github.
import inf
from init import *

cooldown = 0
conrad = "151542934892707840"


def validator(category):
    def predicate(ctx):
        global cooldown
        ch_name = ctx.message.channel.name
        ch_id = ctx.message.channel.id
        u_id = ctx.message.author.id

        if u_id in config["mods"]:
            return True
        elif category == "devplus":
            return u_id in config["devs"]
        elif isinstance(ctx.message.channel, discord.PrivateChannel) or ctx.message.server.id != config["init"]["server"]:
            return category != "modonly"
        elif u_id in config["ignored"] or ch_id in config["silenced"]:
            return False
        else:
            return ch_name in config[category] and cooldown < 5

    return commands.check(predicate)


def logger(name, category, reaction):

    def wrap(f):

        @validator(category)
        async def wrapped(ctx, *args):
            global cooldown
            try:
                log(name, ctx)
                cooldown += 1
                if ctx.message.server is not None and cooldown < 5:
                    try:
                        if isinstance(reaction, list):
                            for each in reaction:
                                await zote.add_reaction(ctx.message, reactions[each])
                        else:
                            await zote.add_reaction(ctx.message, reactions[reaction])
                    except Exception as e:
                        pass
                    await f(ctx, *args)
                else:
                    try:
                        await zote.add_reaction(ctx.message, reactions["no"])
                    except Exception as e:
                        pass
                cooldown -= 1
            except Exception as exc:
                with open(dir_logs + "error.zote", "a") as file:
                    file.write(str(type(exc)) + ":" + str(exc) + "\n")
                print(">>>>>", type(exc), str(exc))
                cooldown -= 1
        return wrapped

    return wrap


def embed(url, desc=None):
    out = discord.Embed()
    out.set_image(url=url)
    if desc is not None:
        out.description = desc
    return out


@zote.command(name="help", pass_context=True, hidden=True)
async def help(ctx):
    await zote.say("See the pins in <#{0}> for a list of commands! (contains spoilers)".format(config["ch"]["meme"]))

##############
"""MOD-ONLY"""
##############


@zote.command(name="ignore", pass_context=True, hidden=True)
@logger("Mod: Ignore user", "modonly", ["happygrub"])
async def ignore(ctx, *args):
    """Ignore users based on their ID
    """
    try:
        a = args[0]
        a = a[2:len(a)-1]
        if a in config["mods"]:
            print("Cannot ignore moderators or administrators")
            await zote.say("Cannot ignore mods or admins!")
        elif a not in config["ignored"]:
            config["ignored"].add_new(tag=a, val=None)
            config.save()
            print("Now ignoring %s" % a)
            await zote.say("Now ignoring <@%s>" % a)
        else:
            config["ignored"].remove(a)
            config.save()
            print("%s removed from ignore list" % a)
            await zote.say("Stopped ignoring <@%s>" % a)
    except discord.NotFound:
        print("Could not find user")
    except discord.HTTPException:
        print("HTTP error of some sort")


@zote.command(name="silence", pass_context=True, hidden=True)
@logger("Mod: silence channel", "modonly", ["happygrub"])
async def silence(ctx, *args):
    a = args[0][2:len(args[0])-1]
    if a not in config["silenced"]:
        config["silenced"].add_new(tag=a, val=None)
        config.save()
        print("Silenced #%s" % a)
        await zote.say("Silenced <#%s>" % a)
    else:
        config["silenced"].remove(a)
        config.save()
        print("Unsilenced %s" % a)
        await zote.say("Unsilenced <#%s>" % a)


@zote.command(name="ignorelist", pass_context=True, hidden=True)
@logger("Mod: Ignore list", "modonly", ["happygrub"])
async def ignorelist(ctx, *args):
    if len(config["ignored"]) > 0:
        out = "**Ignored members**\n"
        for u_id in config["ignored"]:
            out += "<@{0}>: {0}\n".format(u_id)
        await zote.say(out)
    else:
        await zote.say("No ignored members. Good!")


@zote.command(name="modonly", pass_context=True, hidden=True, aliases=["modhelp", "modcommands"])
@logger("Mod-only commands", "modonly", ["happygrub"])
async def modonly(ctx, *args):
    await zote.say(modtext())


@zote.command(name="clearzotes", pass_context=True, hidden=True)
@logger("Mod: clear commands", "modonly", ["happygrub"])
async def clearzotes(ctx, *args):
    count = 0
    prev_count = -1
    num = -1
    if len(args) > 0:
        try:
            num = int(args[0])
        except Exception:
            num = -1
    while -1 == num or (num > count != prev_count):
        prev_count = count
        async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=1000):
            if message.author.id == zote.id or message.content.startswith('_'):
                await zote.delete_message(message)
                count += 1
                if count == num:
                    break
    print("Cleared {0} Zotes".format(count))


@zote.command(name="clear", pass_context=True, hidden=True)
@logger("Mod: clear messages", "modonly", ["happygrub"])
async def clear(ctx, *args):
    if str.isdecimal(args[0]):
        num = int(args[0])
        mgs = []
        async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=num):
            await zote.delete_message(message)
        print("Cleared {0} messages from {1}".format(num, ctx.message.channel.name))
    else:
        user = args[0][2:len(args[0]) - 1]
        try:
            num = 100 if len(args) == 1 else int(args[1])
            num = num if num <= 100 else 100
        except Exception as e:
            num = 100
        count = 0
        while count < num:
            prev_count = count
            async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=1000):
                if message.author.id == user:
                    await zote.delete_message(message)
                    count += 1
                    if count == num:
                        break
            if count == prev_count:
                break
        print("Cleared {0} messages from {1} in {2}".format(num, user, ctx.message.channel.name))


@zote.command(name="helpchannel", pass_context=True, hidden=True, aliases=[])
@logger("Help channel", "modonly", [])
async def helpchannel(ctx, *args):
    """Clears the help channel"""
    cha = zote.get_channel(config["ch"]["help"])
    LOGS = zote.logs_from(cha, limit=100)
    while LOGS.__sizeof__() > 0:
        pinned_count = 0
        mgs = []
        async for message in LOGS:
            if not message.pinned:
                mgs.append(message)
            else:
                pinned_count += 1
        if len(mgs) == 0 or pinned_count == LOGS.__sizeof__():
            break
        elif len(mgs) == 1:
            await zote.delete_message(mgs[0])
        else:
            await zote.delete_messages(mgs)
        LOGS = zote.logs_from(cha, limit=100)
    print("Messages cleared from help")


@zote.command(name="members", pass_context=True, hidden=True, aliases=["membercount"])
@logger("Member count", "modonly", ["happygrub"])
async def member_count(ctx, *args):
    await zote.say("There are **{0}** members in the Hollow Knight server.".format(ctx.message.server.member_count))

###############################
"""CHANNEL-SPECIFIC COMMANDS"""
###############################


@zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
@logger("Gitgud", "meme", ["zote"])
async def gitgud(ctx, *args):
    """IMPROVE YOURSELF
    """
    chance = random_builtin.randint(0, 10)
    if chance <= 1\
            or ctx.message.author.id in config["mods"]\
            or ctx.message.author.id in config["woke"]\
            or ctx.message.author.id in config["devs"]:
        await zote.add_reaction(ctx.message, reactions["hollowwoke"])
        await zote.say(embed=embed(zdn("reaction", "gitwoke.jpg")))
    else:
        await zote.say(embed=embed(zdn("reaction", "gitgud.png")))


@zote.command(name="guides", pass_context=True, aliases=["guide", "speedrunguide"])
@logger("Speedrun guides", "speedrunning", ["zote"])
async def guides(ctx, *args):
    """Quick link to speedrun.com guides"""
    await zote.say("https://www.speedrun.com/hollowknight/guides")


@zote.command(name="hundred", pass_context=True, aliases=["100", "completion", "💯"])
@logger("100% guide", "ref", ["happygrub"])
async def hundred(ctx, *args):
    await zote.say("**100% guide**: https://docs.google.com/document/d/1smOruEIYHbPxsPVocX3RR3E5jrzhpq7RrXhOAocfZDE")


@zote.command(name="resources", pass_context=True)
@logger("Speedrunning resources", "speedrunning", ["zote"])
async def resources(ctx, *args):
    """Quick link to speedrun.com guides"""
    await zote.say("https://www.speedrun.com/hollowknight/resources")


@zote.command(name="spoilers", pass_context=True, aliases=["nospoilers", "spoiler", "spoileralert"])
@logger("Spoiler Alert", "psa", ["happygrub"])
async def spoilers(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(general_psa())


@zote.command(name="splrs", pass_context=True, aliases=["psa"])
@logger("Splr lrt", "psa", ["happygrub"])
async def splrs(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(splr_lrt())


@zote.command(name="wiki", pass_context=True, aliases=["askzote", "<:dunq:335555573481472000>"])
@logger("HK Wiki search", "ref", ["zote"])
async def wiki(ctx, *args):
    if len(args) == 0:
        await zote.say("{0}Zote, The Mighty".format(wiki_str))
        return -1
    r = args[0]
    for each in args[1:]:
        r = "{0} {1}".format(r, each.lower())
    query = wiki_search(r)
    if query == "None found":
        await zote.add_reaction(ctx.message, reactions["no"])
        return -1
    await zote.say("<{0}>".format(query))


#####################
"""ZOTE'S PRECEPTS"""
#####################


@zote.command(name="precept", pass_context=True, aliases=["wisdom", "<:zote:371947495330414595>"])
@logger("Precepts of Zote", "meme", ["zote"])
async def precept(ctx, *args):
    """Hear the precepts of Zote!

     Specify a number from 1 to 57
     for a specific precept,
     or hear them in order.`
    """
    try:
        p = config["precepts"].get(index=(int(args[0]) - 1) % 57)
    except Exception as e:
        p = config["precepts"].get(index=int(config["init"]["precept#"]))
        config["init"].set(tag="precept#", val=str((int(config["init"]["precept#"]) + 1) % 57))
        config.save()
    await zote.say("Precept {0}".format(p))


#################
"""ENEMY ICONS"""
#################


@zote.command(name="enemy", pass_context=True, aliases=["monster", "hj", "hunter", "hunterjournal"])
@logger("Hunter's Journal Icons", "ref", ["zote"])
async def enemy(ctx, *args):
    """See enemy icons! Shows Zote by default, but specify the enemy name (e.g Primal Aspid) to see its icon."""
    if len(args) == 0:
        # await zote.upload(img["hj"]["Zote.png"])
        await zote.add_reaction(ctx.message, reactions["zote"])
    else:
        r = args[0].capitalize()
        for each in args[1:]:
            r = "{0}_{1}".format(r, each.capitalize())
        get = zdn("hj", r + ".png")
        if get is not None:
            await zote.say(embed=embed(get, r.replace("_", " ")))
        else:
            await zote.add_reaction(ctx.message, reactions["primalaspid"])

##################
# IMAGE COMMANDS #
##################


def get_kind(data):

    if data["kind"] == "multi":
        async def multi(ctx, *args): await zote.say(embed=embed(zdn(data["loc"])))
        return multi

    if data["kind"] == "single":
        async def single(ctx, *args): await zote.say(embed=embed(zdn(data["loc"], data["img"])))
        return single


print("Loading commands...")
COG = Index.open("data/cog.cxr")

for e in COG:
    # print(e.tag)
    try:
        if e.tag:
            # retrieve parameterized wrapper from logger
            cmd = logger(e["log"], e["category"], e.all_of("reaction"))

            # retrieve appropriate function from data
            cmd = cmd(get_kind(e))

            # submit command to client
            zote.command(name=e.tag, pass_context=True, aliases=e.all_of("alias"))(cmd)
    except QoidError:
        print("Ignoring read exception in #{0}".format(e.tag))
    except discord.errors.ClientException as dece:
        print("Issue adding command {0}, check aliases".format(e.tag), dece)


@zote.command(name="submit", pass_context=True, aliases=[])
@logger("Submit Meme", "meme", ["zote"])
async def submit_meme(ctx, *args):
    if len(ctx.message.attachments) > 0:
        for each in ctx.message.attachments:
            submit(ctx.message.author.name, ctx.message.author.id, each["url"])
    elif len(args) > 0:
        for each in args:
            submit(ctx.message.author.name, ctx.message.author.id, each)


@zote.command(name="dab", pass_context=True, aliases=["bro", "d4b", "dab_", "<:dabright:320735637386821643>", "<:dableft:369966711648026624>"])
@logger("Dab", "meme", ["dableft", "zote", "dabright"])
async def dab(ctx, *args):
    pass


@zote.command(name="random", pass_context=True, aliases=["randomizer", "seed"])
@logger("Randomizer seed", "speedrunning", ["primalaspid"])
async def randomizerseed(ctx, *args):
    seed = [random_builtin.randint(1, 9)]
    seed += [random_builtin.randint(0, 9) for k in range(8)]
    g = ""
    for each in seed:
        g += str(each)
    if len(args) > 0 and args[0] == "m":
        await zote.send_message(ctx.message.author, "Your randomizer seed is {0}. {1}".format(g, randomizer_taunt()))
    else:
        await zote.say("Your randomizer seed is {0}. {1}".format(g, randomizer_taunt()))


##########
# EVENTS #
##########

@zote.event
async def on_message(message):
    raw = message.content.lower()
    message.content = raw
    await zote.process_commands(message)
    try:
        if message.channel.id == config["ch"]["meme"]:
            if "zote" in raw or "<@297840101944459275>" in raw:
                await zote.add_reaction(message, reactions["zote"])
            if "dab" in raw:
                await zote.add_reaction(message, reactions["dableft"])
                await zote.add_reaction(message, reactions["dabright"])
            if "whomst" in raw:
                await zote.add_reaction(message, reactions["hollowface"])
        if message.channel.id == config["ch"]["general"] or message.channel.id == config["ch"]["bots"]:
            pass
            # for s in blacklist:
            #     if s in message.content.lower():
            #         print("Deleted spoiler {0} in $general".format(s))
            #         await zote.delete_message(message)
            #         await zote.send_message(message.author, splr_lrt() + "\n*(You received this message for saying the spoiler  \"{0}\")*".format(s))
            #         break
    except discord.errors.Forbidden as f:
        pass


#######
# 420 #
#######


@zote.command(name="conradfixyourbot", pass_context=True, aliases=["suggest", "report", "ihate", "pleaseban"])
@logger("CFYB", "general", ["happygrub"])
async def report(ctx, *args):
    if len(args) > 0:
        s = args[0]
        for e in args[1:]:
            s += " " + e
        add_report(s + " < {0} < {1} < {2} < {3}".format(ctx.message.author.name, ctx.message.author.id, ctx.message.channel, ctx.message.timestamp))
        config.save()

####################
# GLAD THAT'S OVER #
####################

while True:
    try:
        # Replace inf.token() with your application token
        zote.run(inf.token())
    except Exception as e:
        zote.close()
        with(dir_logs + "error.zote", "a") as f:
            f.write(str(e) + "\n")
        print(str(e))
    input("Error. Press Enter to reinitialize...")
