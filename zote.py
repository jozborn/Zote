import discord
import os.path
import random as random_builtin
from discord.ext.commands import Bot
from helper import *
from wiki import *

# This line references the application token
# Without revealing it on Github.
# Remove this if you're implementing your own Zote Bot!
import inf

##########
"""INIT"""
##########

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")

zote = Bot(command_prefix=pre)
except_message = "Bah! There is no such thing!"
zote.remove_command("help")
zote.is_listening = True
zote.no_memes = False
zote.general_meme_ignore = False
dir_reaction = "reaction"
dir_mistake = dir_reaction + "/mistake"
dir_grubs = dir_reaction + "/rare grubs"
dir_meme = "meme"

mistake_folder = [name for name in os.listdir(dir_mistake) if os.path.isfile(os.path.join(dir_mistake, name))]
grub_folder = [name for name in os.listdir(dir_grubs) if os.path.isfile(os.path.join(dir_grubs, name))]
random_folder = [name for name in os.listdir(dir_meme) if os.path.isfile(os.path.join(dir_meme, name))]
zote.current_iter = list(random_folder)

heart = "❤"
zote_head = discord.Emoji(
    require_colons="True",
    managed=False,
    id="321038028384632834",
    name="zote",
    roles=[],
    server='283467363729408000')
no = discord.Emoji(
    require_colons="True",
    managed=False,
    id="297708185899499522",
    name="primalaspid",
    roles=[],
    server='283467363729408000'
)
grub = discord.Emoji(
    require_colons="True",
    managed=False,
    id="291831002874249216",
    name="grub",
    roles=[],
    server='283467363729408000'
)
dunq = discord.Emoji(
    require_colons="True",
    managed=False,
    id="335555573481472000",
    name="dunq",
    roles=[],
    server='283467363729408000'
)

reactions = {}
reactions.update({"zote": zote_head, "yes": "", "no": no, "grub": grub, "heart": heart, "dunq": dunq})

def selectmeme():
    selection = random_builtin.randint(0, len(zote.current_iter) - 1)
    next_img = zote.current_iter.pop(selection)
    if len(zote.current_iter) == 0:
        zote.current_iter = list(random_folder)
    return next_img


@zote.command(pass_context=True, hidden=True)
async def help(ctx):
    await zote.say("See pinned messages in {0} for a list of commands! (contains spoilers)".format(ch_meme))

##############
"""MOD-ONLY"""
##############


def validate(category, ctx):
    ch_name = ctx.message.channel.name
    u_id = ctx.message.author.id
    u_name = ctx.message.author.name
    if category == "supermeme":
        if "bots" != ch_name != "meme":
            print("Memes from %s are too dank for %s." % (u_name, ch_name))
            return False
    if zote.no_memes and category == "meme":
        print("No memes: ignored from %s in %s" % (u_name, ch_name))
        return False
    elif zote.general_meme_ignore and ch_name == "general":
        print("General mute: ignored from %s in %s" % (u_name, ch_name))
        return False
    elif zote.is_listening:
        if ch_name not in config[category]:
            if u_id in config["ignoreList"]:
                print("IgnoreList: %s with %s ignored in #%s" % (u_name, category, ch_name))
                return False
            return True
        else:
            print("Category: %s command ignored in #%s" % (category, ch_name))
            return False
    else:
        return False


def modonly(ctx):
    if ctx.message.channel.name in config["modonly"]:
        return True
    else:
        return False


@zote.command(pass_context=True, hidden=True)
async def ignore(ctx, *args):
    """Ignore users based on their ID
    """
    if modonly(ctx):
        try:
            a = args[0]
            if a not in config["ignoreList"]:
                config["ignoreList"].append(a)
                print("Now ignoring %s" % a)
                await zote.say("Now ignoring <@%s>" % a)
                save()
            else:
                print("Already ignoring %s" % a)
                await zote.say("Already ignoring <@%s>" % a)
        except discord.NotFound:
            print("Could not find user")
        except discord.HTTPException:
            print("HTTP error of some sort")


@zote.command(pass_context=True, hidden=True)
async def unignore(ctx, *args):
    """ 
    """
    name = "unignore"
    if modonly(ctx):
        log(name, ctx)
        try:
            for a in args:
                if a in config["ignoreList"]:
                    config["ignoreList"].remove(a)
                    save()
                    print("%s removed from ignore list" % a)
                    await zote.say("<@%s> removed from ignore list" % a)
                else:
                    print("<@%s> is not in ignore list" % a)
                    await zote.say("<@%s> is not in ignore list" % a)
        except discord.NotFound:
            print("Could not find user")
        except discord.HTTPException:
            print("HTTP error of some sort")


@zote.command(pass_context=True, hidden=True)
async def ignorelist(ctx):
    name = "Ignore list"
    if modonly(ctx):
        log(name, ctx)
        if len(config["ignoreList"]) > 0:
            out = "**Ignored members**\n"
            for u_id in config["ignoreList"]:
                out += "<@{0}>: {0}\n".format(u_id)
            await zote.say(out)
        else:
            await zote.say("No ignored members. Good!")


@zote.command(pass_context=True, hidden=True, aliases=["modhelp", "modcommands"])
async def mod(ctx):
    if modonly(ctx):
        await zote.say(modtext())


@zote.command(pass_context=True, hidden=True)
async def listen(ctx, *args):
    name = "listen"
    if modonly(ctx):
        log(name, ctx)
        if len(args) > 0:
            zote.is_listening = True if args[0][0] == "y" else False if args[0][0] == "n" else zote.is_listening
        else:
            zote.is_listening = not zote.is_listening
        await zote.say("Command listening is now " + ("on" if zote.is_listening else "off"))


@zote.command(pass_context=True, hidden=True, aliases=["general"])
async def generalmute(ctx, *args):
    name = "General ignore"
    if modonly(ctx):
        log(name, ctx)
        if len(args) > 0:
            zote.general_ignore = True if args[0][0] == "y" else False if args[0][0] == "n" else zote.general_ignore
        else:
            zote.general_ignore = not zote.general_ignore
        await zote.say("General ignore is now " + ("on" if zote.general_ignore else "off"))


@zote.command(pass_context=True, hidden=True)
async def stop(ctx):
    if modonly(ctx):
        await zote.say("Stopping...")
        exit(0)
        await zote.say("It did not work.")


@zote.command(pass_context=True, hidden=True)
async def memes(ctx):
    if modonly(ctx):
        await zote.say("Memes currently: " + ("not " if zote.no_memes else "") + "allowed")


@zote.command(pass_context=True, hidden=True)
async def nomemes(ctx):
    if modonly(ctx):
        zote.no_memes = True
        await zote.say("Memes not allowed")


@zote.command(pass_context=True, hidden=True)
async def yesmemes(ctx):
    if modonly(ctx):
        zote.no_memes = False
        await zote.say("Memes allowed.")


###############################
"""CHANNEL-SPECIFIC COMMANDS"""
###############################


@zote.command(pass_context=True, aliases=["waifu", "<:hornetstand:284210489159057408>"])
async def gitgud(ctx):
    """IMPROVE YOURSELF
    """
    if ctx.message.channel.name == "general":
        await zote.say(improve())
    else:
        category = "meme"
        name = "gitgud"
        if validate(category, ctx):
            log(name, ctx)
            await zote.add_reaction(ctx.message, reactions["zote"])
            chance = random_builtin.randint(0, 10)
            if chance <= 1:
                await zote.upload(dir_reaction + "/gitwoke.jpg")
            else:
                await zote.upload(dir_reaction + "/gitgud.png")


@zote.command(pass_context=True, aliases=["guide"])
async def guides(ctx):
    """Quick link to speedrun.com guides
    """
    category = "speedrunning"
    name = "guides"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.say("https://www.speedrun.com/hollowknight/guides")


@zote.command(pass_context=True, aliases=[])
async def helpchannel(ctx):
    """ help channel text"""
    name = "Help channel text"
    if modonly(ctx) or (ctx.message.author.id in config["mods"] and ctx.message.channel.id == "349116318865424384"):
        log(name, ctx)
        # #help in Hollow Knight
        cha = zote.get_channel("349116318865424384")

        # #test in g a m e
        # cha = zote.get_channel("364490224925147146")
        try:
            while zote.logs_from(cha, limit=1000).__sizeof__() > 0:
                mgs = []
                async for message in zote.logs_from(cha, limit=1000):
                    mgs.append(message)
                if len(mgs) == 1:
                    await zote.delete_message(mgs[0])
                else:
                    await zote.delete_messages(mgs)
        except discord.errors.ClientException as ce:
            pass
        await zote.send_message(cha, helptext())


@zote.command(pass_context=True, aliases=["100", "completion", "💯"])
async def hundred(ctx):
    category = "reference"
    name = "100% completion list"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.say("**100% completion guide**: https://docs.google.com/document/d/1smOruEIYHbPxsPVocX3RR3E5jrzhpq7RrXhOAocfZDE/edit")


@zote.command(pass_context=True, aliases=["nospoilers", "psa", "spoiler", "spoileralert"])
async def spoilers(ctx):
    """ A friendly reminder for #general"""
    category = "general"
    name = "spoilers"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.say(general_psa())


@zote.command(pass_context=True)
async def resources(ctx):
    """Quick link to speedrun.com guides
    """
    category = "speedrunning"
    name = "resources"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.say("https://www.speedrun.com/hollowknight/resources")


@zote.command(pass_context=True, aliases=["askzote", "<:dunq:335555573481472000>"])
async def wiki(ctx, *args):
    category = "reference"
    name = "Wiki search"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
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


@zote.command(pass_context=True, aliases=["wisdom", "<:zote:321038028384632834>"])
async def precept(ctx, at_loc=-1, numbers=config["numbers"], precepts=config["precepts"]):
    """Hear the precepts of Zote!
     
     Specify a number from 1 to 57
     for a specific precept,
     or hear them in order.
    alt: wisdom
    """
    category = "meme"
    name = "precept"
    if validate(category, ctx):
        log(name, ctx)
        if 1 <= at_loc <= 57:
            await zote.say("Precept {0}: {1}".format(numbers[(at_loc - 1) % 57], precepts[(at_loc - 1) % 57]))
        else:
            config["precept#"] = (config["precept#"] + 1) % 57
            await zote.say(
                "Precept {0}: {1}".format(
                    numbers[(config["precept#"] - 1) % 57], precepts[(config["precept#"] - 1) % 57]))
            save()
        await zote.add_reaction(ctx.message, reactions["zote"])


#################
"""ENEMY ICONS"""
#################


@zote.command(pass_context=True, aliases=["monster", "hj", "hunter", "hunterjournal"])
async def enemy(ctx, *args):
    """See enemy icons!
    This will show Zote by default, but specify the enemy name (e.g Primal Aspid) to see its icon. 
    alt: monster, enemy, hunter, hunterjournal
    """
    category = "reference"
    name = "enemy"
    if validate(category, ctx):
        log(name, ctx)
        fname = "hj/{0}.png".format(enemy_name(args))
        if os.path.isfile(fname):
            await zote.add_reaction(ctx.message, reactions["zote"])
            await zote.upload(fname)
        else:
            await zote.add_reaction(ctx.message, reactions["no"])


###########
"""MEMES"""
###########

"""
THE ONE MEME TO RULE THEM ALL
"""
@zote.command(pass_context=True, aliases=["fuckmeupfam", "gimmethatmeme", "<:hollowdab:320735637386821643>", "<:hollowomg:337314365323870209>", "<:hollowlenny:337314901670232064>", "<:corny:309365508682285057>", "<:hollowface:324349140920434690>", "<:hollowwow:343784030828888065>", "<:intenseface:331674362509787136>", "<:hollowwoke:344348211433177088>", "jetfuelcantmeltdankmemes"])
async def meme(ctx):
    category = "supermeme"
    name = "Meme"
    if validate(category, ctx):
        log(name, ctx)
        # selection = random_builtin.randint(0, len(zote.current_iter) - 1)
        # next_img = zote.current_iter.pop(selection)
        # # print(next_img, len(zote.current_iter), ":", zote.current_iter)
        # if len(zote.current_iter) == 0:
        #     zote.current_iter = list(random_folder)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload("{0}/{1}".format(dir_meme, selectmeme()))


@zote.command(pass_context=True, aliases=["mobadis", "bapanada"])
async def absolutelymobadis(ctx):
    """Bapanada.
    Alt: mobadis, bapanada
    """
    category = "safememe"
    name = "absolutelymobadis"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/absolutelymobadis.jpg")


@zote.command(pass_context=True, aliases=["trollaspid", "trolol", "trololol", "<:primalaspid:297708185899499522>"])
async def aspid(ctx):
    """Troll aspid
    alt: trolol, trololol, trolololol, trololololol, trolololololol
    """
    category = "meme"
    name = "Troll aspid"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/trollaspid.png")


@zote.command(pass_context=True, aliases=["ban", "modpoweractivate", "modpowersactivate", "bourgeoisie"])
async def b4n(ctx):
    category = "meme"
    name = "banhammer"
    if ctx.message.author.id in mods:
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["grub"])
        await zote.upload(dir_reaction + "/banhammer.png")


@zote.command(pass_context=True, aliases=["420"])
async def bapanada420(ctx):
    """ Mobadis friendly
    """
    category = "meme"
    name = "bapanada 420"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/420.jpg")


@zote.command(pass_context=True, aliases=["dance"])
async def celebrate(ctx):
    """Like no one is watching
    alt: dance
    """
    category = "safememe"
    name = "Celebrate"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/dancing.gif")


@zote.command(pass_context=True, aliases=["drake", "dashmaster"])
async def dashmasterdrake(ctx):
    category = "meme"
    name = "Dashmaster Drake"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/dashmaster.jpg")


@zote.command(pass_context=True, aliases=[])
async def datvoid(ctx):
    category = "meme"
    name = "Dat Void"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/datvoid.jpg")


@zote.command(pass_context=True, aliases=["emilitia"])
async def disapprove(ctx):
    """Emilitia
    alt: emilitia
    """
    category = "meme"
    name = "Disapproving Emilitia"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/disapprove.png")


@zote.command(pass_context=True, aliases=["guessilldie", "guilttrip", "<:elderbug:337323354589757451>"])
async def elderbug(ctx):
    """Elderbug guilt trip
    alt: guessilldie, guilttrip
    """
    category = "safememe"
    name = "Elderbug"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/elderbug die.png")


@zote.command(pass_context=True, aliases=["whathaveidone"])
async def flukemilf(ctx):
    category = "meme"
    name = "FlukeMILF"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/flukemilf.gif")


@zote.command(pass_context=True, aliases=[])
async def frug(ctx):
    category = "safememe"
    name = "Frug"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/frug.jpg")


@zote.command(pass_context=True, aliases=[])
async def goodmemeplease(ctx):
    category = "meme"
    name = "No country for good memes"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["dunq"])
        await zote.upload("{0}/{1}".format(dir_meme, selectmeme()))



@zote.command(pass_context=True, aliases=["ascend", "ascendbro", "shinygorb"])
async def gorb(ctx):
    """Gorb 
    alt: ascend, ascendbro, shinygorb
    """
    category = "meme"
    name = "Gorb"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/shinygorb.jpg")


@zote.command(pass_context=True, aliases=["onthisthedaymydaughteristobemarried", "myeh", "<:grubfather:291831043386769419>"])
async def grubfather(ctx):
    """No respect
    Alt: onthisthedaymydaughteristobemarried, myeh
    """
    category = "safememe"
    name = "Grubfather"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/grubfather.jpg")


@zote.command(pass_context=True, aliases=["grubme", "grubs", "raregrub", "raregrubs", "<:grub:314011604696170496>", "<:happygrub:291831002874249216>", "<:sadgrub:316743976474509314>"])
async def grublove(ctx):
    category = "meme"
    name = "Grub love"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.add_reaction(ctx.message, reactions["heart"])
        await zote.add_reaction(ctx.message, reactions["grub"])
        selection = random_builtin.randint(0, len(grub_folder) - 1)
        await zote.upload("{0}/{1}".format(dir_grubs, selection))


@zote.command(pass_context=True, aliases=["holo", "holonite", "loog"])
async def hallonite(ctx):
    """is halo nit logo k
    alt: holo, holonite, loog
    """
    category = "safememe"
    name = "Halol nite"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/hallonite.jpg")


@zote.command(pass_context=True, aliases=["doot", "dootdoot"])
async def hollowdoot(ctx):
    """Doot
    Alt: doot, dootdoot
    """
    category = "safememe"
    name = "Hollowdoot"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/hollowdoot.jpg")


@zote.command(pass_context=True, aliases=["bottleopener", "coldone"])
async def hornet(ctx):
    category = "meme"
    name = "Hornet Bottle Open"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/hornet bottle opener.jpg")


@zote.command(pass_context=True, aliases=["spin", "buhhuhhuh"])
async def hornetspin(ctx):
    category = "meme"
    name = "Hornet spin"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/hornetspin.gif")


@zote.command(pass_context=True, aliases=["stabyourself", "stab", "stabfirst", "youfirst", "<:hollowknice:300572689616076801>"])
async def hklogic(ctx):
    category = "meme"
    name = "Hollow Knight Logic"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/stabyourselffirst.jpg")


@zote.command(pass_context=True, aliases=["me", "me_irl", "dead"])
async def meirl(ctx):
    """me_irl
    alt: me, me_irl, dead
    """
    category = "meme"
    name = "me_irl"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/meirl.png")


@zote.command(pass_context=True, aliases=["gittlelirl"])
async def mistake(ctx):
    category = "meme"
    name = "Mistake memes"
    if validate(category, ctx):
        log(name, ctx)
        selection = random_builtin.randint(0, len(mistake_folder) - 1)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload("{0}/{1}".format(dir_mistake, selection))


@zote.command(pass_context=True, aliases=["scuse", "mushroom", "shroom", "mushroomman", "scuze", "mrmush", "excuseme"])
async def mrmushroom(ctx):
    """Nyush oola mumu?
    alt: scuse, mushroom, shroom, mushroomman, scuze, mrmush, excuseme
    """
    category = "meme"
    name = "Mr Mushroom"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/scuse me.png")


@zote.command(pass_context=True, aliases=["noot", "dootnoot"])
async def nootdoot(ctx):
    """I am Noot
    Alt: noot, dootnoot
    """
    category = "safememe"
    name = "Noot Doot"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/nootdoot.png")


@zote.command(pass_context=True, aliases=["<:smugrad:300589495437230080>"])
async def pervertedlight(ctx):
    """Radiance
    """
    category = "meme"
    name = "Perverted Radiance"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/perverted light.gif")


@zote.command(pass_context=True)
async def popcorn(ctx):
    """I'm gonna need some popcorn
    """
    category = "safememe"
    name = "popcorn"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/popcorn.jpg")


@zote.command(pass_context=True, aliases=["praisetillyourehollow", "praisetilyourehollow", "praisetil", "420praiseit"])
async def praise(ctx):
    """Moss Prophet
    alt: praisetillyourehollow, praisetilyourehollow, praisetil, 420praiseit
    """
    category = "meme"
    name = "Praise"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/praise the light.jpg")


@zote.command(pass_context=True, aliases=[])
async def shaw(ctx):
    category = "meme"
    name = "Shaw"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/imgonnashaw.jpg")


@zote.command(pass_context=True, aliases=[])
async def stealyogirl(ctx):
    category = "safememe"
    name = "Steal yo girl"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/stealyogirl.jpg")


@zote.command(pass_context=True, aliases=["squad", "tearsquad"])
async def squadgoals(ctx):
    """Husk sentry squad
    alt: squad, tearsquad
    """
    category = "safememe"
    name = "Squad goals"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/squad goals.png")


@zote.command(pass_context=True, aliases=["darksouls", "danksouls", "defeated", "trialoffools"])
async def steelsoul(ctx):
    """Defeated
    alt: darksouls, danksouls, defeated, trialoffools
    """
    category = "meme"
    name = "steelsoul"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/defeated.jpg")


@zote.command(pass_context=True, aliases=["xero", "fool"])
async def youfool(ctx):
    """Xero
    alt: xero, fool
    """
    category = "meme"
    name = "youfool"
    if validate(category, ctx):
        log(name, ctx)
        await zote.add_reaction(ctx.message, reactions["zote"])
        await zote.upload(dir_reaction + "/you fool.png")


# Replace inf.token() with your application token
zote.run(inf.token())