import os.path
import random as random_builtin
import sys

from discord.ext import commands

# This line references the application token
# Without revealing it on Github.
# Remove this if you're implementing your own Zote Bot!
import inf
from auxiliary import *
from init import *


def validator(category):
    try:
        def predicate(ctx):
            ch_name = ctx.message.channel.name
            u_id = ctx.message.author.id

            return u_id in config["mods"] \
                or (category != "modonly"
                    and ch_name in config[category]
                    and u_id not in config["ignored"]
                    and ch_name not in config["silenced"])
        return commands.check(predicate)
    except discord.ext.commands.CheckFailure:
        print("{0} command failed validation".format(category))


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


@zote.command(name="help", pass_context=True, hidden=True)
async def help(ctx):
    await zote.say("See pinned messages in {0} for a list of commands! (contains spoilers)".format(ch_meme))

##############
"""MOD-ONLY"""
##############


@zote.command(name="ignore", pass_context=True, hidden=True)
@logger("Mod: Ignore user", "modonly", ["grub"])
async def ignore(ctx, *args):
    """Ignore users based on their ID
    """
    try:
        a = args[0]
        if a in config["mods"]:
            print("Cannot ignore moderators or administrators")
            await zote.say("Cannot ignore mods or admins!")
        elif a not in config["ignored"]:
            config["ignored"].append(a)
            save()
            print("Now ignoring %s" % a)
            await zote.say("Now ignoring <@%s>" % a)
        else:
            config["ignored"].remove(a)
            save()
            print("%s removed from ignore list" % a)
            await zote.say("Stopped ignoring <@%s>" % a)
    except discord.NotFound:
        print("Could not find user")
    except discord.HTTPException:
        print("HTTP error of some sort")


@zote.command(name="silence", pass_context=True, hidden=True)
@logger("Mod: silence channel", "modonly", ["grub"])
async def silence(ctx, *args):
    a = args[0][2:len(args[0])-1]
    if a not in config["silenced"]:
        config["silenced"].append(a)
        print(config["silenced"])
        save()
        print("Silenced #%s" % a)
        await zote.say("Silenced <#%s>" % a)
    else:
        config["silenced"].remove(a)
        print(config["silenced"])
        save()
        print("Unsilenced %s" % a)
        await zote.say("Unsilenced <#%s>" % a)

@zote.command(name="ignorelist", pass_context=True, hidden=True)
@logger("Mod: Ignore list", "modonly", ["grub"])
async def ignorelist(ctx, *args):
    if len(config["ignored"]) > 0:
        out = "**Ignored members**\n"
        for u_id in config["ignored"]:
            out += "<@{0}>: {0}\n".format(u_id)
        await zote.say(out)
    else:
        await zote.say("No ignored members. Good!")


@zote.command(name="modonly", pass_context=True, hidden=True, aliases=["modhelp", "modcommands"])
@logger("Mod-only commands", "modonly", ["grub"])
async def modonly(ctx, *args):
    await zote.say(modtext())


@zote.command(name="clearzotes", pass_context=True, hidden=True)
@logger("Mod: clear commands", "modonly", ["grub"])
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
@logger("Mod: clear messages", "modonly", ["grub"])
async def clear(ctx, *args):
    if str.isdecimal(args[0][0]):
        num = int(args[0][0])
        mgs = []
        async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=num):
            await zote.delete_message(message)
            # mgs.append(message)
        # if len(mgs) == 1:
        #     await zote.delete_message(mgs[0])
        # else:
        #     await zote.delete_messages(mgs)
        print("Cleared {0} messages from {1}".format(num, ctx.message.channel.name))
    else:
        user = args[0][3:len(args[0]) - 1]
        num = 100 if len(args) == 1 else int(args[1])
        num = num if num <= 100 else 100
        count = 0
        while count < num:
            prev_count = count
            mgs = []
            async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=1000):
                if message.author.id == user:
                    # mgs.append(message)
                    await zote.delete_message(message)
                    count += 1
                    if count == num:
                        break
            # if len(mgs) == 0:
            #     break
            # elif len(mgs) == 1:
            #     await zote.delete_message(mgs[0])
            # else:
            #     await zote.delete_messages(mgs)
            if count == prev_count:
                break
        print("Cleared {0} messages from {1} in {2}".format(num, user, ctx.message.channel.name))


RELEASE_DATE = datetime.datetime(2017, 10, 31, 0, 0, 0, 0)

@zote.command(name="countdown", pass_context=True, aliases=["jonnypls", "gooftroupewhen", "grimmtimer", "whenishalloween"])
@logger("Grimm Troupe countdown", "general", ["dunq"])
async def countdown(ctx, *args):
    current_time = datetime.datetime.now()
    until = RELEASE_DATE - current_time
    hours = until.seconds//3600
    minutes = (until.seconds - hours*3600) // 60
    await zote.say("Hollow Knight: The {0} Troupe releases in:\n**{1} days**,\n**{2} hours**,\n**{3} minutes**,\n**{4} seconds**, and\n**{5} milliseconds**"
                   .format(
                        "Grimm" if random_builtin.randint(0, 10) >= 3 else "Goof",
                        until.days,
                        hours,
                        minutes,
                        until.seconds % 60,
                        until.microseconds/1000
                    )
    )


###############################
"""CHANNEL-SPECIFIC COMMANDS"""
###############################


@zote.command(name="gitgud", pass_context=True, aliases=["waifu", "<:hornetstand:284210489159057408>"])
@logger("Gitgud", "general", ["zote"])
async def gitgud(ctx, *args):
    """IMPROVE YOURSELF
    """
    if ctx.message.channel.name == "general":
        await zote.say(improve())
    else:
        chance = random_builtin.randint(0, 10)
        if chance <= 1:
            await zote.upload(dir_reaction + "/gitwoke.jpg")
        else:
            await zote.upload(dir_reaction + "/gitgud.png")


@zote.command(name="guides", pass_context=True, aliases=["guide", "speedrunguide"])
@logger("Speedrun guides", "speedrunning", ["zote"])
async def guides(ctx, *args):
    """Quick link to speedrun.com guides
    """
    await zote.say("https://www.speedrun.com/hollowknight/guides")


@zote.command(name="helpchannel", pass_context=True, aliases=[])
@logger("Help channel", "modonly", ["grub"])
async def helpchannel(ctx):
    """ help channel text"""
    # #help in Hollow Knight
    cha = zote.get_channel("349116318865424384")
    while zote.logs_from(cha, limit=100).__sizeof__() > 0:
        mgs = []
        async for message in zote.logs_from(cha, limit=100):
            mgs.append(message)
        if len(mgs) == 0:
            break
        elif len(mgs) == 1:
            await zote.delete_message(mgs[0])
        else:
            await zote.delete_messages(mgs)
    await zote.send_message(cha, helptext())


@zote.command(name="hundred", pass_context=True, aliases=["100", "completion", "💯"])
@logger("100% guide", "ref", ["grub"])
async def hundred(ctx, *args):
    await zote.say("**100% completion guide**: https://docs.google.com/document/d/1smOruEIYHbPxsPVocX3RR3E5jrzhpq7RrXhOAocfZDE/edit")


@zote.command(name="spoilers", pass_context=True, aliases=["nospoilers", "psa", "spoiler", "spoileralert"])
@logger("Spoiler Alert", "general", ["grub"])
async def spoilers(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(general_psa())


@zote.command(name="resources", pass_context=True)
@logger("Speedrunning resources", "speedrunning", ["zote"])
async def resources(ctx, *args):
    """Quick link to speedrun.com guides
    """
    await zote.say("https://www.speedrun.com/hollowknight/resources")


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
        await zote.add_reaction(ctx.message, "❌")
        return -1
    await zote.say("<{0}>".format(query))


#####################
"""ZOTE'S PRECEPTS"""
#####################


@zote.command(name="precept", pass_context=True, aliases=["wisdom", "<:zote:321038028384632834>"])
@logger("Precepts of Zote", "ref", ["zote"])
async def precept(ctx, at_loc=-1):
    """Hear the precepts of Zote!
     
     Specify a number from 1 to 57
     for a specific precept,
     or hear them in order.
    alt: wisdom
    """
    if 1 <= at_loc <= 57:
        p = config["precepts"][at_loc - 1]
        await zote.say("Precept {0}: {1}".format(p[0], p[1]))
    else:
        config["precept#"] = (config["precept#"] + 1) % 57
        p = config["precepts"][config["precept#"]-1]
        await zote.say("Precept {0}: {1}".format(p[0], p[1]))
        save()


#################
"""ENEMY ICONS"""
#################


@zote.command(name="enemy", pass_context=True, aliases=["monster", "hj", "hunter", "hunterjournal"])
@logger("Hunter's Journal Icons", "ref", ["zote"])
async def enemy(ctx, *args):
    """See enemy icons!
    This will show Zote by default, but specify the enemy name (e.g Primal Aspid) to see its icon. 
    alt: monster, enemy, hunter, hunterjournal
    """
    fname = enemy_name(args)
    if os.path.isfile(fname):
        await zote.upload(fname)
    else:
        await zote.add_reaction(ctx.message, reactions["aspid"])

##########
# MULTIS #
##########


@zote.command(name="meme", pass_context=True, aliases=["fuckmeupfam", "gimmethatmeme", "<:hollowdab:320735637386821643>", "<:hollowomg:337314365323870209>", "<:hollowlenny:337314901670232064>", "<:corny:309365508682285057>", "<:hollowface:324349140920434690>", "<:hollowwow:343784030828888065>", "<:intenseface:331674362509787136>", "<:hollowwoke:344348211433177088>", "jetfuelcantmeltdankmemes"])
@logger("Meme", "supermeme", ["zote", "corny", "aspid", "grub"])
async def meme(ctx, *args):
    await zote.upload(memes.next())


@zote.command(name="goodmemeplease", pass_context=True, aliases=[])
@logger("Good memes", "meme", ["dunq"])
async def goodmemeplease(ctx, *args):
    await zote.upload(memes.next())


@zote.command(name="grimm", pass_context=True, aliases=["grimmface", "gooftroupe", "grimmadventure"])
@logger("Grimm Troupe Face", "meme", ["zote", "grub"])
async def grimm(ctx, *args):
    await zote.upload(grimmfaces.next())


@zote.command(name="grublove", pass_context=True, aliases=["grubme", "grubs", "raregrub", "raregrubs", "<:grub:314011604696170496>", "<:happygrub:291831002874249216>", "<:sadgrub:316743976474509314>"])
@logger("Grub Love", "meme", ["grub", "heart", "zote"])
async def grublove(ctx, *args):
    await zote.upload(goodgrubs.next())


@zote.command(name="grubhate", pass_context=True, aliases=[])
@logger("Grub Hate", "meme", ["grub", "aspid", "zote"])
async def grubhate(ctx, *args):
    await zote.upload(badgrubs.next())


@zote.command(name="mistake", pass_context=True, aliases=["gittlelirl"])
@logger("Mistake", "meme", ["zote"])
async def mistake(ctx, *args):
    await zote.upload(mistakes.next())

#########
# MEMES #
#########


@zote.command(name="absolutelymobadis", pass_context=True, aliases=["mobadis", "bapanada"])
@logger("Absolutely Mobadis", "general", ["corny"])
async def absolutelymobadis(ctx, *args):
    """Bapanada.
    Alt: mobadis, bapanada
    """
    await zote.upload(dir_reaction + "/absolutelymobadis.jpg")


@zote.command(name="aspid", pass_context=True, aliases=["trollaspid", "trolol", "trololol", "<:primalaspid:297708185899499522>"])
@logger("Troll Aspid", "meme", ["aspid"])
async def aspid(ctx, *args):
    """Troll aspid
    alt: trolol, trololol, trolololol, trololololol, trolololololol
    """
    await zote.upload(dir_reaction + "/trollaspid.png")


@zote.command(name="ban", pass_context=True, aliases=["b4n", "modpoweractivate", "modpowersactivate", "bourgeoisie", "banhammer"])
@logger("Banhammer", "modonly", ["grub", "heart", "aspid"])
async def ban(ctx, *args):
    await zote.upload(dir_reaction + "/banhammer.png")


@zote.command(name="bapanada420", pass_context=True, aliases=["420"])
@logger("Bapanada420", "meme", ["corny"])
async def bapanada420(ctx, *args):
    """ Mobadis friendly
    """
    await zote.upload(dir_reaction + "/420.jpg")


@zote.command(name="celebrate", pass_context=True, aliases=["dance"])
@logger("Celebrate", "general", ["zote"])
async def celebrate(ctx, *args):
    """Like no one is watching
    alt: dance
    """
    await zote.upload(dir_reaction + "/dancing.gif")


@zote.command(name="dashmasterdrake", pass_context=True, aliases=["drake", "dashmaster"])
@logger("Dashmaster Drake", "meme", ["zote"])
async def dashmasterdrake(ctx, *args):
    await zote.upload(dir_reaction + "/dashmaster.jpg")


@zote.command(name="datvoid", pass_context=True, aliases=[])
@logger("O Shit waddup", "meme", ["zote"])
async def datvoid(ctx, *args):
    await zote.upload(dir_reaction + "/datvoid.jpg")


@zote.command(name="disapprove", pass_context=True, aliases=["emilitia"])
@logger("Disapproving Emilitia", "reaction", ["zote"])
async def disapprove(ctx, *args):
    """Emilitia
    alt: emilitia
    """
    await zote.upload(dir_reaction + "/disapprove.png")


@zote.command(name="elderbug", pass_context=True, aliases=["guessilldie", "guilttrip", "<:elderbug:337323354589757451>"])
@logger("Elderbug", "general", ["zote"])
async def elderbug(ctx, *args):
    """Elderbug guilt trip
    alt: guessilldie, guilttrip
    """
    await zote.upload(dir_reaction + "/elderbug die.png")


@zote.command(name="flukemilf", pass_context=True, aliases=["whathaveidone"])
@logger("FlukeMILF", "meme", ["zote"])
async def flukemilf(ctx, *args):
    await zote.upload(dir_reaction + "/flukemilf.gif")


@zote.command(name="gorb", pass_context=True, aliases=["ascend", "ascendbro", "shinygorb"])
@logger("Gorb", "reaction", ["zote"])
async def gorb(ctx, *args):
    """Gorb 
    alt: ascend, ascendbro, shinygorb
    """
    await zote.upload(dir_reaction + "/shinygorb.jpg")


@zote.command(name="grubfather", pass_context=True, aliases=["onthisthedaymydaughteristobemarried", "myeh", "<:grubfather:291831043386769419>"])
@logger("Grubfather", "meme", ["grub"])
async def grubfather(ctx, *args):
    """No respect
    Alt: onthisthedaymydaughteristobemarried, myeh
    """
    await zote.upload(dir_reaction + "/grubfather.jpg")


@zote.command(name="hallonite", pass_context=True, aliases=["holo", "holonite", "loog"])
@logger("Is Halo Nit ok", "meme", ["zote"])
async def hallonite(ctx, *args):
    """is halo nit logo k
    alt: holo, holonite, loog
    """
    await zote.upload(dir_reaction + "/hallonite.jpg")


@zote.command(name="hollowdoot", pass_context=True, aliases=["doot", "dootdoot"])
@logger("Hollow Doot", "meme", ["zote"])
async def hollowdoot(ctx, *args):
    """Doot
    Alt: doot, dootdoot
    """
    await zote.upload(dir_reaction + "/hollowdoot.jpg")


@zote.command(name="hornet", pass_context=True, aliases=["bottleopener", "coldone"])
@logger("Hornet Bottle Opener", "meme", ["zote"])
async def hornet(ctx, *args):
    await zote.upload(dir_reaction + "/hornet bottle opener.jpg")


@zote.command(name="hornetspin", pass_context=True, aliases=["spin", "buhhuhhuh"])
@logger("Hornet Spin", "reaction", ["zote"])
async def hornetspin(ctx, *args):
    await zote.upload(dir_reaction + "/hornetspin.gif")


@zote.command(name="hklogic", pass_context=True, aliases=["stabyourself", "stab", "stabfirst", "youfirst", "<:hollowknice:300572689616076801>"])
@logger("HK Logic", "meme", ["zote"])
async def hklogic(ctx, *args):
    await zote.upload(dir_reaction + "/stabyourselffirst.jpg")


@zote.command(name="meirl", pass_context=True, aliases=["me", "me_irl", "dead"])
@logger("Me_irl", "meme", ["zote"])
async def meirl(ctx, *args):
    """me_irl
    alt: me, me_irl, dead
    """
    await zote.upload(dir_reaction + "/meirl.png")


@zote.command(name="mrmushroom", pass_context=True, aliases=["scuse", "mushroom", "shroom", "mushroomman", "scuze", "mrmush", "excuseme"])
@logger("Mr Mushroom", "reaction", ["zote"])
async def mrmushroom(ctx, *args):
    """Nyush oola mumu?
    alt: scuse, mushroom, shroom, mushroomman, scuze, mrmush, excuseme
    """
    await zote.upload(dir_reaction + "/scuse me.png")


@zote.command(name="nootdoot", pass_context=True, aliases=["noot", "dootnoot"])
@logger("Noot Doot", "meme", ["zote"])
async def nootdoot(ctx, *args):
    """I am Noot
    Alt: noot, dootnoot
    """
    await zote.upload(dir_reaction + "/nootdoot.png")


@zote.command(name="pervertedlight", pass_context=True, aliases=["<:smugrad:300589495437230080>"])
@logger("Perverted Light", "meme", ["zote"])
async def pervertedlight(ctx, *args):
    """Radiance
    """
    await zote.upload(dir_reaction + "/perverted light.gif")


@zote.command(name="popcorn", pass_context=True)
@logger("Popcorn", "general", ["zote"])
async def popcorn(ctx, *args):
    """I'm gonna need some popcorn
    """
    await zote.upload(dir_reaction + "/popcorn.jpg")


@zote.command(name="praise", pass_context=True, aliases=["praisetillyourehollow", "praisetilyourehollow", "praisetil", "420praiseit"])
@logger("Praise", "meme", ["zote"])
async def praise(ctx, *args):
    """Moss Prophet
    alt: praisetillyourehollow, praisetilyourehollow, praisetil, 420praiseit
    """
    await zote.upload(dir_reaction + "/praise the light.jpg")


@zote.command(name="shaw", pass_context=True, aliases=[])
@logger("Shaw", "meme", ["zote"])
async def shaw(ctx, *args):
    await zote.upload(dir_reaction + "/imgonnashaw.jpg")


@zote.command(name="stealyogirl", pass_context=True, aliases=[])
@logger("Steal Yo Girl", "meme", ["zote"])
async def stealyogirl(ctx, *args):
    await zote.upload(dir_reaction + "/stealyogirl.jpg")


@zote.command(name="squadgoals", pass_context=True, aliases=["squad", "tearsquad"])
@logger("Squad Goals", "general", ["zote"])
async def squadgoals(ctx, *args):
    """Husk sentry squad
    alt: squad, tearsquad
    """
    await zote.upload(dir_reaction + "/squad goals.png")


@zote.command(name="steelsoul", pass_context=True, aliases=["darksouls", "danksouls", "defeated", "trialoffools"])
@logger("Steel Soul", "meme", ["zote"])
async def steelsoul(ctx, *args):
    """Defeated
    alt: darksouls, danksouls, defeated, trialoffools
    """
    await zote.upload(dir_reaction + "/defeated.jpg")


@zote.command(name="youfool", pass_context=True, aliases=["xero", "fool"])
@logger("You Fool", "meme", ["zote"])
async def youfool(ctx, *args):
    """Xero
    alt: xero, fool
    """
    await zote.upload(dir_reaction + "/you fool.png")

# sys.tracebacklimit = 1

# Replace inf.token() with your application token
zote.run(inf.token())
