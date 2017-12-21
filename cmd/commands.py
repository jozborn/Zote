import os.path
import random as random_builtin

from discord.ext import commands

# This line references the application token
# without revealing it on Github.
import inf
from init import *
from contest import *


def validator(category):
    def predicate(ctx):
        ch_name = ctx.message.channel.name
        ch_id = ctx.message.channel.id
        u_id = ctx.message.author.id

        return u_id in config["mods"] \
            or (category != "modonly"
                and ch_name in config[category]
                and u_id not in config["ignored"]
                and ch_id not in config["silenced"])
    return commands.check(predicate)


def logger(name, category, reaction):

    def wrap(f):

        @validator(category)
        async def wrapped(ctx, *args):
            try:
                log(name, ctx)
                if isinstance(reaction, list):
                    for each in reaction:
                        await zote.add_reaction(ctx.message, reactions[each])
                else:
                    await zote.add_reaction(ctx.message, reactions[reaction])
                await f(ctx, *args)
            except Exception as exc:
                with open(dir_logs + "error.zote", "a") as file:
                    file.write(str(type(exc)) + ":" + str(exc) + "\n")
                print(">>>>>", type(exc), str(exc))
        return wrapped

    return wrap


@zote.command(name="help", pass_context=True, hidden=True)
async def help(ctx):
    await zote.say("See pinned messages in {0} for a list of commands! (contains spoilers)".format(config["ch"]["meme"]))

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
        if a in config["mods"]:
            print("Cannot ignore moderators or administrators")
            await zote.say("Cannot ignore mods or admins!")
        elif a not in config["ignored"]:
            config["ignored"].add_new(a)
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
    print(a)
    if a not in config["silenced"]:
        config["silenced"].add_new(tag=a)
        print(config["silenced"])
        config.save()
        print("Silenced #%s" % a)
        await zote.say("Silenced <#%s>" % a)
    else:
        config["silenced"].remove(a)
        print(config["silenced"])
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
        print("getting logs")
        async for message in zote.logs_from(zote.get_channel(ctx.message.channel.id), limit=1000):
            print("have log")
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
@logger("Help channel", "modonly", ["happygrub"])
async def helpchannel(ctx, *args):
    """ help channel text"""
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


###############################
"""CHANNEL-SPECIFIC COMMANDS"""
###############################


@zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
@logger("Gitgud", "general", ["zote"])
async def gitgud(ctx, *args):
    """IMPROVE YOURSELF
    """
    if ctx.message.channel.name == "general":
        await zote.say(improve())
    else:
        chance = random_builtin.randint(0, 10)
        if chance <= 1:
            await zote.upload(img["reaction"]["gitwoke.jpg"])
        else:
            await zote.upload(img["reaction"]["gitgud.png"])


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
@logger("Spoiler Alert", "spoilers", ["happygrub"])
async def spoilers(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(general_psa())


@zote.command(name="splrs", pass_context=True, aliases=["psa"])
@logger("Splr lrt", "spoilers", ["happygrub"])
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
@logger("Precepts of Zote", "ref", ["zote"])
async def precept(ctx, *args):
    """Hear the precepts of Zote!

     Specify a number from 1 to 57
     for a specific precept,
     or hear them in order.
    """
    try:
        p = config["precepts"][(int(args[0]) - 1) % 57]
        await zote.say("Precept {0}".format(p))
    except Exception as e:
        current = config["init"]
        p = config["precepts"][int(current["precept#"])]
        await zote.say("Precept {0}".format(p))

        pr_num = current["precept#"]
        current.set(index=current.index(current.find("precept#")), this=qoid.Property("precept#", str((int(pr_num) + 1) % 57)))
        config.save()


#################
"""ENEMY ICONS"""
#################


@zote.command(name="enemy", pass_context=True, aliases=["monster", "hj", "hunter", "hunterjournal"])
@logger("Hunter's Journal Icons", "ref", ["zote"])
async def enemy(ctx, *args):
    """See enemy icons! Shows Zote by default, but specify the enemy name (e.g Primal Aspid) to see its icon."""
    if len(args) == 0:
        await zote.upload(img["hj"]["Zote.png"])
    else:
        r = args[0].capitalize()
        for each in args[1:]:
            r = "{0} {1}".format(r, each.capitalize())
        fname = img["hj"][r + ".png"]
        if os.path.isfile(fname):
            await zote.upload(fname)
        else:
            await zote.add_reaction(ctx.message, reactions["primalaspid"])

##########
# MULTIS #
##########


@zote.command(name="meme", pass_context=True, aliases=["fuckmeupfam", "gimmethatmeme", "<:hollowomg:337314365323870209>", "<:hollowlenny:337314901670232064>", "<:corny:309365508682285057>", "<:hollowface:324349140920434690>", "<:hollowwow:343784030828888065>", "<:intenseface:331674362509787136>", "<:hollowwoke:344348211433177088>", "jetfuelcantmeltdankmemes"])
@logger("Meme", "supermeme", ["zote", "corny", "primalaspid", "happygrub"])
async def meme(ctx, *args):
    await zote.upload(img.r("meme"))


@zote.command(name="goodmemeplease", pass_context=True, aliases=[])
@logger("Good memes", "supermeme", ["dunq"])
async def goodmemeplease(ctx, *args):
    await zote.upload(img.r("meme"))


@zote.command(name="beelove", pass_context=True, aliases=["🐝"])
@logger("Bee Love", "meme", ["bee", "heart", "zote"])
async def beelove(ctx, *args):
    await zote.upload(img.r("beelove"))


@zote.command(name="grublove", pass_context=True, aliases=["<:happygrub:291831002874249216>"])
@logger("Grub Love", "meme", ["happygrub", "heart", "zote"])
async def grublove(ctx, *args):
    await zote.upload(img.r("grublove"))


@zote.command(name="grubhate", pass_context=True, aliases=["<:sadgrub:316743976474509314>"])
@logger("Grub Hate", "meme", ["happygrub", "primalaspid", "zote"])
async def grubhate(ctx, *args):
    await zote.upload(img.r("grubhate"))


@zote.command(name="lore", pass_context=True, aliases=["wilbopls"])
@logger("Hollow Knight Lore", "general", ["zote", "heart", "teamcherry"])
async def lore(ctx, *args):
    await zote.upload(img["reaction"]["lore.jpg"])


@zote.command(name="maggothate", pass_context=True, aliases=["maggoth8", "<:maggot:313428664576376832>"])
@logger("Maggot Hate", "meme", ["maggot", "primalaspid", "zote"])
async def maggothate(ctx, *args):
    await zote.upload(img.r("maggothate"))


@zote.command(name="mistake", pass_context=True, aliases=["gittlelirl", "gittle", "mistae", "mistaek", "mistkae"])
@logger("Mistake", "meme", ["zote"])
async def mistake(ctx, *args):
    await zote.upload(img.r("mistake"))

#########
# MEMES #
#########


@zote.command(name="absolutelymobadis", pass_context=True, aliases=["mobadis", "bapanada"])
@logger("Absolutely Mobadis", "general", ["corny"])
async def absolutelymobadis(ctx, *args):
    """Bapanada.
    Alt: mobadis, bapanada
    """
    await zote.upload(img["reaction"]["absolutelymobadis.jpg"])


@zote.command(name="aspid", pass_context=True, aliases=["trollaspid", "trolol", "trololol", "<:primalaspid:297708185899499522>"])
@logger("Troll Aspid", "meme", ["primalaspid"])
async def aspid(ctx, *args):
    """Troll aspid
    alt: trolol, trololol, trolololol, trololololol, trolololololol
    """
    await zote.upload(img["reaction"]["trollaspid.png"])


@zote.command(name="ban", pass_context=True, aliases=["b4n", "modpoweractivate", "modpowersactivate", "bourgeoisie", "banhammer"])
@logger("Banhammer", "modonly", ["happygrub", "heart", "primalaspid"])
async def ban(ctx, *args):
    await zote.upload(img["reaction"]["banhammer.png"])


@zote.command(name="bapanada420", pass_context=True, aliases=["420"])
@logger("Bapanada420", "meme", ["corny"])
async def bapanada420(ctx, *args):
    """ Mobadis friendly"""
    await zote.upload(img["reaction"]["420.jpg"])


@zote.command(name="celebrate", pass_context=True, aliases=["dance"])
@logger("Celebrate", "general", ["zote"])
async def celebrate(ctx, *args):
    """Like no one is watching"""
    await zote.upload(img["reaction"]["dancing.gif"])


@zote.command(name="dab", pass_context=True, aliases=["bro", "d4b", "dab_", "<:dabright:320735637386821643>", "<:dableft:369966711648026624>"])
@logger("Dab", "general", ["dableft", "zote", "dabright"])
async def dab(ctx, *args):
    pass


@zote.command(name="dashmasterdrake", pass_context=True, aliases=["drake", "dashmaster"])
@logger("Dashmaster Drake", "meme", ["zote"])
async def dashmasterdrake(ctx, *args):
    await zote.upload(img["reaction"]["dashmaster.jpg"])


@zote.command(name="datvoid", pass_context=True, aliases=[])
@logger("O Shit waddup", "meme", ["zote"])
async def datvoid(ctx, *args):
    await zote.upload(img["reaction"]["datvoid.jpg"])


@zote.command(name="disapprove", pass_context=True, aliases=["emilitia"])
@logger("Disapproving Emilitia", "meme", ["zote"])
async def disapprove(ctx, *args):
    """Emilitia"""
    await zote.upload(img["reaction"]["disapprove.png"])


@zote.command(name="elderbug", pass_context=True, aliases=["guessilldie", "guilttrip", "<:elderbug:337323354589757451>"])
@logger("Elderbug", "general", ["zote"])
async def elderbug(ctx, *args):
    """Elderbug guilt trip
    alt: guessilldie, guilttrip
    """
    await zote.upload(img["reaction"]["elderbug die.png"])


@zote.command(name="frug", pass_context=True, aliases=[])
@logger("Frug", "general", ["happygrub"])
async def frug(ctx, *args):
    await zote.upload(img["reaction"]["frug.jpg"])


@zote.command(name="flukemilf", pass_context=True, aliases=["whathaveidone"])
@logger("FlukeMILF", "meme", ["zote"])
async def flukemilf(ctx, *args):
    await zote.upload(img["reaction"]["flukemilf.gif"])


@zote.command(name="gorb", pass_context=True, aliases=["ascend", "ascendbro", "shinygorb"])
@logger("Gorb", "meme", ["zote"])
async def gorb(ctx, *args):
    """Gorb 
    alt: ascend, ascendbro, shinygorb
    """
    await zote.upload(img["reaction"]["shinygorb.jpg"])


@zote.command(name="graig", pass_context=True, aliases=["graigpls"])
@logger("Graig", "ref", ["zote", "heart", "teamcherry"])
async def graig(ctx, *args):
    await zote.upload(img["reaction"]["graig.png"])


@zote.command(name="grimm", pass_context=True, aliases=["grimmface", "gooftroupe", "grimmadventure"])
@logger("Grimm Snap", "meme", ["zote", "happygrub", "grimm"])
async def grimm(ctx, *args):
    await zote.upload(img["reaction"]["grimm.gif"])


@zote.command(name="grubfather", pass_context=True, aliases=["onthisthedaymydaughteristobemarried", "myeh", "<:grubfather:341180809228845056>"])
@logger("Grubfather", "meme", ["happygrub"])
async def grubfather(ctx, *args):
    """No respect
    Alt: onthisthedaymydaughteristobemarried, myeh
    """
    await zote.upload(img["reaction"]["grubfather.jpg"])


@zote.command(name="hallonite", pass_context=True, aliases=["holo", "holonite", "loog"])
@logger("Is Halo Nit ok", "meme", ["zote"])
async def hallonite(ctx, *args):
    """is halo nit logo k
    alt: holo, holonite, loog
    """
    await zote.upload(img["reaction"]["hallonite.jpg"])


@zote.command(name="hollowdoot", pass_context=True, aliases=["doot", "dootdoot"])
@logger("Hollow Doot", "meme", ["zote"])
async def hollowdoot(ctx, *args):
    """Doot
    Alt: doot, dootdoot
    """
    await zote.upload(img["reaction"]["hollowdoot.jpg"])


@zote.command(name="hornet", pass_context=True, aliases=["bottleopener", "coldone"])
@logger("Hornet Bottle Opener", "meme", ["zote"])
async def hornet(ctx, *args):
    await zote.upload(img["reaction"]["hornet bottle opener.jpg"])


@zote.command(name="hornetspin", pass_context=True, aliases=["spin", "buhhuhhuh"])
@logger("Hornet Spin", "meme", ["zote"])
async def hornetspin(ctx, *args):
    await zote.upload(img["reaction"]["hornetspin.gif"])


@zote.command(name="hklogic", pass_context=True, aliases=["stabyourself", "stab", "stabfirst", "youfirst", "<:hollowknice:300572689616076801>"])
@logger("HK Logic", "meme", ["zote"])
async def hklogic(ctx, *args):
    await zote.upload(img["reaction"]["stabyourselffirst.jpg"])


@zote.command(name="meirl", pass_context=True, aliases=["me", "me_irl", "dead"])
@logger("Me_irl", "meme", ["zote"])
async def meirl(ctx, *args):
    """me_irl
    alt: me, me_irl, dead
    """
    await zote.upload(img["reaction"]["meirl.png"])


@zote.command(name="mrmushroom", pass_context=True, aliases=["🍄", "mushroom", "shroom", "mushroomman", "excuseme"])
@logger("Mr Mushroom", "meme", ["zote"])
async def mrmushroom(ctx, *args):
    """Nyush oola mumu?
    alt: scuse, mushroom, shroom, mushroomman, scuze, mrmush, excuseme
    """
    await zote.upload(img["reaction"]["scuse me.png"])


@zote.command(name="nootdoot", pass_context=True, aliases=["noot", "dootnoot"])
@logger("Noot Doot", "meme", ["zote"])
async def nootdoot(ctx, *args):
    """I am Noot
    Alt: noot, dootnoot
    """
    await zote.upload(img["reaction"]["nootdoot.png"])


@zote.command(name="pervertedlight", pass_context=True, aliases=["<:smugrad:300589495437230080>"])
@logger("Perverted Light", "meme", ["zote"])
async def pervertedlight(ctx, *args):
    """Radiance
    """
    await zote.upload(img["reaction"]["perverted light.gif"])


@zote.command(name="pickle", pass_context=True, aliases=[""])
@logger("No Pickle Command", "supermeme", ["pick", "l"])
async def pickle(ctx, *args):
    await zote.upload(img["reaction"]["pickle.jpg"])


@zote.command(name="popcorn", pass_context=True)
@logger("Popcorn", "general", ["zote"])
async def popcorn(ctx, *args):
    """I'm gonna need some popcorn
    """
    await zote.upload(img["reaction"]["popcorn.jpg"])


@zote.command(name="praise", pass_context=True, aliases=["praisetillyourehollow", "praisetilyourehollow", "praisetil", "420praiseit"])
@logger("Praise", "meme", ["zote"])
async def praise(ctx, *args):
    """Moss Prophet
    alt: praisetillyourehollow, praisetilyourehollow, praisetil, 420praiseit
    """
    await zote.upload(img["reaction"]["praise the light.jpg"])


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


@zote.command(name="shaw", pass_context=True, aliases=[])
@logger("Shaw", "meme", ["zote"])
async def shaw(ctx, *args):
    await zote.upload(img["reaction"]["imgonnashaw.jpg"])


@zote.command(name="squadgoals", pass_context=True, aliases=["squad", "tearsquad"])
@logger("Squad Goals", "general", ["zote"])
async def squadgoals(ctx, *args):
    """Husk sentry squad
    alt: squad, tearsquad
    """
    await zote.upload(img["reaction"]["squad goals.png"])


@zote.command(name="stealyogirl", pass_context=True, aliases=[])
@logger("Steal Yo Girl", "meme", ["zote"])
async def stealyogirl(ctx, *args):
    await zote.upload(img["reaction"]["stealyogirl.jpg"])


@zote.command(name="steelsoul", pass_context=True, aliases=["darksouls", "danksouls", "defeated", "trialoffools"])
@logger("Steel Soul", "meme", ["zote"])
async def steelsoul(ctx, *args):
    """Defeated
    alt: darksouls, danksouls, defeated, trialoffools
    """
    await zote.upload(img["reaction"]["defeated.jpg"])


@zote.command(name="verupls", pass_context=True, aliases=[])
@logger("Verupls", "general", ["zote"])
async def verupls(ctx, *args):
    """Defeated
    alt: darksouls, danksouls, defeated, trialoffools
    """
    await zote.say("That is not a valid command.")


@zote.command(name="youfool", pass_context=True, aliases=["xero", "fool"])
@logger("You Fool", "meme", ["zote"])
async def youfool(ctx, *args):
    """Xero
    alt: xero, fool
    """
    await zote.upload(img["reaction"]["you fool.png"])


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


############
# GIVEAWAY #
############


@zote.command(name="enter", pass_context=True, hidden=False)
@logger("Holiday Entry", "hollowmas", [])
async def enter(ctx, *args):
    result = enter_contest(ctx.message.author.id)
    if result == "already":
        await zote.add_reaction(ctx.message, reactions["yes"])
        await zote.send_message(ctx.message.author, "You are already entered in the Hollowmas Giveaway. You now have a chance to win a prize on each of the 12 days of Hollowmas!")
        await zote.send_message(ctx.message.author, "\n\nThe Hollowmas Giveaway runs every day through December 24th. Winners will be tagged at 6AM AEDT in #hollowmas-giveaway!")
    elif result == "added":
        await zote.add_reaction(ctx.message, reactions["yes"])
        await zote.send_message(ctx.message.author, "You are now entered in the Hollowmas Giveaway. You now have a chance to win a prize on each of the 12 days of Hollowmas!")
        await zote.send_message(ctx.message.author, "\n\nThe Hollowmas Giveaway runs every day through December 24th. Winners will be tagged at 6AM AEDT in #hollowmas-giveaway!")
        if len(ENTRIES) % 100 == 0:
            await zote.say("<@{0}> is the {1}th person to enter the Hollowmas Giveaway!".format(ctx.message.author.id, len(ENTRIES)))
    elif result == "error":
        await zote.add_reaction(ctx.message, reactions["no"])
        await zote.say("<@{0}> An error occurred. Please try to _enter again!")


@zote.command(name="draw", pass_context=True, hidden=False)
@logger("Holiday Drawing", "modonly", [])
async def draw(ctx, *args):
    if len(ENTRIES) == 1:
        s = ENTRIES.pop(0)
        await zote.say("Congratulations <@{0}>! You are the winner!".format(s))
    elif len(args) == 0:
        found = False
        while not found:
            s = ENTRIES.pop(random.randint(0, len(ENTRIES) - 1))
            if s not in WINNERS and s not in config["mods"]:
                found = True
        print("{0} selected".format(s))
        await zote.say("Congratulations <@{0}>! You are the winner!".format(s))
        win_contest(s)
    elif 1 <= int(args[0]) <= 10:
        s = []
        while len(s) < int(args[0]) and len(ENTRIES) > 0:
            g = ENTRIES.pop(random.randint(0, len(ENTRIES) - 1))
            if g not in s and g not in WINNERS and g not in config["mods"]:
                s.append(g)
            else:
                ENTRIES.append(g)
        r = "Congratulations to the winners:\n\n"
        for each in s:
            r += "<@{0}>\n".format(each)
        await zote.say(r)
        for each in s:
            win_contest(each)


@zote.command(name="drawspecial", pass_context=True, hidden=False)
@logger("Holiday Drawing", "modonly", [])
async def draw2(ctx, *args):
    if len(ENTRIES) == 1:
        s = ENTRIES.pop(0)
        await zote.say("Congratulations <@{0}>! You are the winner!".format(s))
    elif len(args) == 0:
        s = ""
        found = False
        while not found:
            s = ENTRIES[random.randint(0, len(ENTRIES) - 1)]
            if s not in WINNERS2:
                found = True
        print("{0} selected".format(s))
        await zote.say("Congratulations <@{0}>! You are the winner!".format(s))
        win_contest(s)
    elif 1 <= int(args[0]) <= 10:
        s = []
        while len(s) < int(args[0]) and len(ENTRIES) > 0:
            g = ENTRIES[random.randint(0, len(ENTRIES) - 1)]
            if g not in s and g not in WINNERS2:
                s.append(g)
            else:
                ENTRIES.append(g)
        r = "Congratulations to each of the winners:\n\n"
        for each in s:
            r += "<@{0}>\n".format(each)
        await zote.say(r)
        for each in s:
            win_contest2(each)


@zote.command(name="check", pass_context=True, hidden=True, aliases=["checkentries"])
@logger("See # Hollowmas Entries", "modonly", ["teamcherry"])
async def check_entries(ctx, *args):
    await zote.say("There are {0} entries in the Hollow-mas giveaway!".format(len(ENTRIES)))


@zote.command(name="isentry", pass_context=True, hidden=True)
@logger("Check for User Entry", "modonly", ["teamcherry"])
async def is_entry(ctx, *args):
    if len(args) > 0:
        k = args[0][3:len(args[0]) - 1]if args[0][2] == "!" else args[0][2:len(args[0]) - 1]
        print(args[0])
        print(k)
        await zote.say("<@{0}> is {1}entered in the Hollowmas Giveaway.".format(k, "" if k in ENTRIES else "not "))


################
# END GIVEAWAY #
################


while True:
    print("Initializing...")
    try:
        # Replace inf.token() with your application token
        zote.run(inf.token())
    except Exception as e:
        zote.close()
        with(dir_logs + "error.zote", "a") as f:
            f.write(str(e) + "\n")
        print(str(e))
    input("Error. Press Enter to reinitialize...")
