import os.path
import random as random_builtin

from discord.ext import commands

# This line references the application token
# without revealing it on Github.
import inf
from init import *


def validator(category):
    def predicate(ctx):
        ch_name = ctx.message.channel.name
        ch_id = ctx.message.channel.id
        u_id = ctx.message.author.id

        if category == "devplus":
            return u_id in config["devs"] or u_id in config["mods"]
        elif isinstance(ctx.message.channel, discord.PrivateChannel) or ctx.message.server.id != config["init"]["server"]:
            return category != "modonly"
        elif ch_name in config[category]:
            return u_id not in config["ignored"] and ch_id not in config["silenced"]
        elif category != "modonly":
            return u_id in config["devs"] or u_id in config["mods"]
        else:
            return u_id in config["mods"]

    return commands.check(predicate)


def logger(name, category, reaction):

    def wrap(f):

        @validator(category)
        async def wrapped(ctx, *args):
            try:
                log(name, ctx)
                if ctx.message.server.id == config["init"]["server"]:
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
@logger("Gitgud", "general", ["zote"])
async def gitgud(ctx, *args):
    """IMPROVE YOURSELF
    """
    if ctx.message.channel.name == "general":
        await zote.say(improve())
    elif ctx.message.channel.name == "help":
        if ctx.message.author.id not in config["helptrolls"]:
            await zote.say("<#{1}> is a place to provide players with actual assistance, <@{0}>".format(ctx.message.author.id, ctx.message.channel.id))
            config["helptrolls"].add(qoid.Property(tag=ctx.message.author.id, val="1"))
            config.save()
        else:
            await zote.delete_message(ctx.message)
            pr = config["helptrolls"].find(ctx.message.author.id)
            pr.set(pr.tag, str(int(pr.val) + 1))
            config.save()
            if int(pr.val) >= 5:
                config["ignored"].add(qoid.Property(ctx.message.author.id))
                print(ctx.message.author.name + " is ignored for helptrolling")
    else:
        chance = random_builtin.randint(0, 10)
        if chance <= 1 or ctx.message.author.id in config["mods"] or ctx.message.author.id in config["woke"]:
            await zote.add_reaction(ctx.message, reactions["hollowwoke"])
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
@logger("Spoiler Alert", "psa", ["happygrub"])
async def spoilers(ctx, *args):
    """ A friendly reminder for #general"""
    try:
        zote.delete_message(config["init"]["last_psa"])
    except Exception as e:
        print("Could not delete last psa")
    i = config["init"].index("last_psa")
    config["init"].set(i, qoid.Property("last_psa", ctx.message.id))
    await zote.say(general_psa())


@zote.command(name="splrs", pass_context=True, aliases=["psa"])
@logger("Splr lrt", "psa", ["happygrub"])
async def splrs(ctx, *args):
    """ A friendly reminder for #general"""
    try:
        print(config["init"]["last_psa"])
        zote.delete_message(zote.get_message(ctx.message.channel, config["init"]["last_psa"]))
    except Exception as e:
        print("Could not delete last psa")
    i = config["init"].index("last_psa")
    config["init"].set(i, qoid.Property("last_psa", ctx.message.id))
    config.save()
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


@zote.command(name="meme", pass_context=True, aliases=["meme_", "whilst_", "hwhilst", "whilst", "<:hollowomg:337314365323870209>", "<:hollowlenny:337314901670232064>", "<:corny:309365508682285057>", "<:hollowface:324349140920434690>", "<:hollowwow:343784030828888065>", "<:intenseface:331674362509787136>", "<:hollowwoke:344348211433177088>"])
@logger("Meme", "supermeme", ["zote", "corny", "primalaspid", "happygrub"])
async def meme(ctx, *args):
    await zote.upload(img.r("meme"))


@zote.command(name="goodmemeplease", pass_context=True, aliases=[])
@logger("Good memes", "supermeme", ["dunq"])
async def goodmemeplease(ctx, *args):
    await zote.upload(img.r("meme"))


@zote.command(name="fuckmeupfam", pass_context=True, aliases=["gagglemeupgritten"])
@logger("FMUF", "supermeme", ["grimm", "primalaspid", "zote"])
async def fmuf(ctx, *args):
    await zote.upload(img.r("meme"))


@zote.command(name="beelove", pass_context=True, aliases=["🐝"])
@logger("Bee Love", "meme", ["bee", "heart", "zote"])
async def beelove(ctx, *args):
    await zote.upload(img.r("beelove"))


@zote.command(name="comic", pass_context=True, aliases=["psych"])
@logger("Psych Comic", "supermeme", ["zote"])
async def comic(ctx, *args):
    await zote.upload(img.r("psych"))


@zote.command(name="grublove", pass_context=True, aliases=["<:happygrub:291831002874249216>"])
@logger("Grub Love", "meme", ["happygrub", "heart", "zote"])
async def grublove(ctx, *args):
    await zote.upload(img.r("grublove"))


@zote.command(name="grubhate", pass_context=True, aliases=["<:sadgrub:316743976474509314>"])
@logger("Grub Hate", "meme", ["happygrub", "primalaspid", "zote"])
async def grubhate(ctx, *args):
    await zote.upload(img.r("grubhate"))


@zote.command(name="lore", pass_context=True, aliases=["wilbopls"])
@logger("Hollow Knight Lore", "meme", ["zote", "heart", "teamcherry"])
async def lore(ctx, *args):
    await zote.upload(img["reaction"]["lore.jpg"])


@zote.command(name="obvious", pass_context=True, aliases=["ofc", "obv"])
@logger("Lord of the Obvious", "supermeme", ["zote"])
async def obvious(ctx, *args):
    await zote.upload(img.r("obvious"))


@zote.command(name="maggothate", pass_context=True, aliases=["maggoth8", "<:maggot:313428664576376832>"])
@logger("Maggot Hate", "meme", ["maggot", "primalaspid", "zote"])
async def maggothate(ctx, *args):
    await zote.upload(img.r("maggothate"))


@zote.command(name="maggotlove", pass_context=True, aliases=[])
@logger("Maggot LOVE", "meme", ["maggot", "heart", "zote"])
async def maggotlove(ctx, *args):
    await zote.upload(img.r("maggotlove"))


@zote.command(name="mistake", pass_context=True, aliases=["gittlelirl", "gittle", "mistae", "mistaek", "mistkae"])
@logger("Mistake", "meme", ["zote"])
async def mistake(ctx, *args):
    await zote.upload(img.r("mistake"))


@zote.command(name="submit", pass_context=True, aliases=[])
@logger("Submit Meme", "supermeme", ["zote"])
async def submit_meme(ctx, *args):
    if len(ctx.message.attachments) > 0:
        submit(ctx.message.author.name, ctx.message.author.id, ctx.message.attachments[0]["url"])
    elif len(args) > 0:
        for each in args:
            submit(ctx.message.author.name, ctx.message.author.id, each)

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
@logger("Banhammer", "devplus", ["happygrub", "heart", "primalaspid"])
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


@zote.command(name="draw", pass_context=True, hidden=False)
@logger("Holiday Entry", "supermeme", ["teamcherry"])
async def draw(ctx, *args):
    await zote.say("Congratulations <@{0}>! You are the winner!".format(ctx.message.author.id))


@zote.command(name="elderbug", pass_context=True, aliases=["guessilldie", "<:elderbug:337323354589757451>"])
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


@zote.command(name="godseeker", pass_context=True, aliases=["graigseeker"])
@logger("godseeker", "meme", ["primalaspid"])
async def godseeker(ctx, *args):
    await zote.upload(img["reaction"]["godseeker.jpg"])


@zote.command(name="gorb", pass_context=True, aliases=["ascend", "ascendbro", "shinygorb"])
@logger("Gorb", "meme", ["zote"])
async def gorb(ctx, *args):
    """Gorb 
    alt: ascend, ascendbro, shinygorb
    """
    await zote.upload(img["reaction"]["shinygorb.jpg"])


@zote.command(name="graig", pass_context=True, aliases=["graigpls"])
@logger("Graig", "meme", ["zote", "heart", "teamcherry"])
async def graig(ctx, *args):
    await zote.upload(img["reaction"]["graig.png"])


@zote.command(name="grimm", pass_context=True, aliases=["grimmface", "gooftroupe", "grimmadventure"])
@logger("Grimm Snap", "meme", ["zote", "happygrub", "grimm"])
async def grimm(ctx, *args):
    await zote.upload(img["reaction"]["grimm.gif"])


@zote.command(name="grubfather", pass_context=True, aliases=["onthisthedaymydaughteristobemarried", "<:grubfather:341180809228845056>"])
@logger("Grubfather", "meme", ["happygrub"])
async def grubfather(ctx, *args):
    """No respect
    Alt: onthisthedaymydaughteristobemarried, myeh
    """
    await zote.upload(img["reaction"]["grubfather.jpg"])


@zote.command(name="hallonite", pass_context=True, aliases=["holo", "holonite", "holonit", "loog"])
@logger("Is Halo Nit ok", "meme", ["zote"])
async def hallonite(ctx, *args):
    """is halo nit logo k
    alt: holo, holonite, loog
    """
    await zote.upload(img["reaction"]["holonit poteiga.png"])


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


@zote.command(name="hklogic", pass_context=True, aliases=["<:hollowknice:300572689616076801>"])
@logger("HK Logic", "meme", ["zote"])
async def hklogic(ctx, *args):
    await zote.upload(img["reaction"]["stabyourselffirst.jpg"])


@zote.command(name="loremaster", pass_context=True, aliases=[])
@logger("Lore Master Never Lies", "meme", ["zote"])
async def loremaster(ctx, *args):
    await zote.upload(img["reaction"]["lore master never lies.png"])

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


@zote.command(name="pickle", pass_context=True, aliases=[])
@logger("No Pickle Command", "supermeme", ["pick", "l"])
async def pickle(ctx, *args):
    await zote.upload(img["reaction"]["pickle.jpg"])


@zote.command(name="popcorn", pass_context=True)
@logger("Popcorn", "general", ["zote"])
async def popcorn(ctx, *args):
    """I'm gonna need some popcorn
    """
    await zote.upload(img["reaction"]["popcorn.jpg"])


@zote.command(name="praise", pass_context=True, aliases=["420praiseit"])
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


@zote.command(name="verupls", pass_context=True, aliases=["boxpls"])
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


#####################
# SPOLER MANAGEMENT #
#####################


@zote.event
async def on_message(message):
    await zote.process_commands(message)
    if "zote" in message.content.lower() or "<@297840101944459275>" in message.content.lower():
        await zote.add_reaction(message, reactions["zote"])
    if message.channel.id == config["ch"]["general"] or message.channel.id == config["ch"]["bots"]:
        pass
        # for s in blacklist:
        #     if s in message.content.lower():
        #         print("Deleted spoiler {0} in $general".format(s))
        #         await zote.delete_message(message)
        #         await zote.send_message(message.author, splr_lrt() + "\n*(You received this message for saying the spoiler  \"{0}\")*".format(s))
        #         break
    elif message.channel.id == config["ch"]["art"]:
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
