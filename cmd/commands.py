import random as random_builtin
import discord
import requests
import traceback
from life_ender import discord_sanitize_arguments, embedify
from discord.ext import commands
from zdn import dir_logs
from init import zote, reactions, zdn
from data import *
from qoid import *

# This line references the application token
# without revealing it on Github.
import inf

cooldown = 0


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
            return category != "modonly" and cooldown < 5
        elif u_id in config["ignored"] or ch_id in config["silenced"]:
            return False
        elif category != "modonly":
            return ch_name in config[category] and cooldown < 5
        else:
            return False

    return commands.check(predicate)


def logger(category, reaction):

    def wrap(f):

        @validator(category)
        async def wrapped(ctx, *args):
            global cooldown
            try:
                try:
                    log(f.__name__, ctx)
                except Exception:
                    print("log error")
                cooldown += 1
                try:
                    if isinstance(reaction, list):
                        for each in reaction:
                            try:
                                await zote.add_reaction(ctx.message, reactions[each])
                            except discord.errors.Forbidden:
                                pass
                    else:
                        try:
                            await zote.add_reaction(ctx.message, reactions[reaction])
                        except discord.errors.Forbidden:
                            pass
                except Exception as e:
                    try:
                        await zote.add_reaction(ctx.message, reactions["no"])
                    except discord.errors.Forbidden:
                        pass
                args = await discord_sanitize_arguments(zote, ctx.message.channel, *args)
                await f(ctx, *args)
                cooldown -= 1
            except Exception as exc:
                with open(dir_logs + "error.zote", "a") as file:
                    file.write(str(type(exc)) + ":" + str(exc) + "\n")
                print(">>>>>", type(exc), str(exc))
                cooldown -= 1
                try:
                    await zote.add_reaction(ctx.message, reactions["no"])
                except discord.errors.Forbidden:
                    pass
        return wrapped

    return wrap


@zote.command(name="help", pass_context=True, hidden=True)
async def help(ctx):
    await zote.say(f"See the pins in <#{config['ch']['meme']}> for a list of commands! (contains spoilers)")

##############
"""MOD-ONLY"""
##############


@zote.command(name="ignore", pass_context=True, hidden=True)
@logger("modonly", ["happygrub"])
async def ignore(ctx, *args):
    """Ignore users based on their ID
    """
    try:
        a = args[0].id
        if a in config["mods"]:
            print("Cannot ignore moderators or administrators")
            await zote.say("Cannot ignore mods or admins!")
        elif a not in config["ignored"]:
            config["ignored"] += Property(tag=a, val=None)
            config.save()
            print(f"Now ignoring {a}")
            await zote.say(f"Now ignoring <@{a}>")
        else:
            config["ignored"] -= a
            config.save()
            print(f"{a} removed from ignore list")
            await zote.say(f"Stopped ignoring <@{a}>")
    except discord.NotFound:
        print("Could not find user")
    except discord.HTTPException:
        print("HTTP error of some sort")


@zote.command(name="silence", pass_context=True, hidden=True)
@logger("modonly", ["happygrub"])
async def silence(ctx, *args):
    a = args[0].id
    if a not in config["silenced"]:
        config["silenced"] += Property(tag=a, val=None)
        config.save()
        print(f"Silenced #{a}")
        await zote.say(f"Silenced <#{a}>")
    else:
        config["silenced"] -= a
        config.save()
        print(f"Unsilenced {a}")
        await zote.say(f"Unsilenced <#{a}>")


@zote.command(name="ignorelist", pass_context=True, hidden=True)
@logger("modonly", ["happygrub"])
async def ignorelist(ctx, *args):
    if len(config["ignored"]) > 0:
        out = "**Ignored members**\n"
        for u_id in config["ignored"]:
            out += f"<@{u_id}>: {u_id}\n"
        await zote.say(out)
    else:
        await zote.say("No ignored members. Good!")


@zote.command(name="modonly", pass_context=True, hidden=True, aliases=["modhelp", "modcommands"])
@logger("modonly", ["happygrub"])
async def modonly(ctx, *args):
    await zote.say(modtext())


@zote.command(name="clear", pass_context=True, hidden=True)
@logger("modonly", [])
async def clear(ctx, *args):
    if not args:
        await zote.add_reaction(ctx.message, reactions["dunq"])
        return
    del_cmd = False
    try:
        del_limit = 250
        # Step 0: gather from args
        delcount = 1
        arg1 = arg2 = None
        if args:
            try:
                delcount = int(args[0])
                if delcount > del_limit:
                    print(f"Delete count limited to {del_limit}")
                    delcount = del_limit
            except ValueError:
                pass
            if len(args) > 1:
                arg1 = args[1]
                if len(args) > 2:
                    arg2 = args[2]

        ch = ctx.message.channel
        us = None
        # Step 1: Guarantee parameter submission is appropriate
        if arg1:
            if isinstance(arg1, discord.Channel):
                ch = arg1
            elif isinstance(arg1, discord.User):
                us = arg1.id

            if isinstance(arg2, discord.Channel):
                ch = arg2
            elif isinstance(arg2, discord.User):
                us = arg2.id
        if not ch:
            print("Detected NoneType channel")
            ch = zote.get_channel(ctx.message.channel.id)

        bf = None
        counter = 0
        marked = []
        while counter < delcount:
            prev = bf
            async for msg in zote.logs_from(channel=ch, limit=100, before=bf, after=None):
                if not msg.pinned:
                    if us:
                        if msg.author.id == us:
                            if ctx.message.id == msg.id:
                                del_cmd = True
                            marked.append(msg)
                            counter += 1
                    else:
                        if ctx.message.id == msg.id:
                            del_cmd = True
                        marked.append(msg)
                        counter += 1
                bf = msg
                if counter == delcount:
                    # print("Limit reached. ", end="")
                    break
                elif len(marked) == 100:
                    print(len(marked))
                    await zote.delete_messages(marked)
                    marked = []
            if prev == bf:
                # print("End of channel reached. ", end="")
                break
        if not marked:
            pass
        elif len(marked) == 1:
            await zote.delete_message(marked[0])
        else:
            await zote.delete_messages(marked)
        print(f"{counter} messages cleared")
        if not del_cmd:
            await zote.add_reaction(ctx.message, reactions["yes"])
    except discord.DiscordException as e:
        print(f">>> >>> {e}")
        traceback.print_exc()
        if not del_cmd:
            await zote.add_reaction(ctx.message, reactions["dunq"])


@zote.command(name="helpchannel", pass_context=True, hidden=True, aliases=[])
@logger("modonly", [])
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
@logger("modonly", ["happygrub"])
async def member_count(ctx, *args):
    await zote.say(f"There are **{ctx.message.server.member_count}** members in the Hollow Knight server.")

###############################
"""CHANNEL-SPECIFIC COMMANDS"""
###############################


@zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
@logger("meme", ["zote"])
async def gitgud(ctx, *args):
    """IMPROVE YOURSELF"""
    chance = random_builtin.randint(0, 10)
    if ctx.message.author.id == "312125463952883712":
        await zote.say(embed=embedify("https://cdn.discordapp.com/attachments/417908285405134849/421784416113917954/421784116028243978.png"))
    elif chance <= 1 or ctx.message.author.id in config["mods"] + config["woke"] + config["devs"]:
        await zote.add_reaction(ctx.message, reactions["hollowwoke"])
        await zote.say(embed=embedify(zdn("reaction", "gitwoke.jpg")))
    else:
        await zote.say(embed=embedify(zdn("reaction", "gitgud.png")))


@zote.command(name="guides", pass_context=True, aliases=["guide", "speedrunguide"])
@logger("speedrunning", ["zote"])
async def guides(ctx, *args):
    """Quick link to speedrun.com guides"""
    await zote.say("https://www.speedrun.com/hollowknight/guides")


@zote.command(name="hundred", pass_context=True, aliases=["100", "completion", "💯"])
@logger("ref", ["happygrub"])
async def hundred(ctx, *args):
    await zote.say("**100% guide**: https://docs.google.com/document/d/1smOruEIYHbPxsPVocX3RR3E5jrzhpq7RrXhOAocfZDE")


@zote.command(name="random", pass_context=True, aliases=["randomizer", "seed"])
@logger("speedrunning", ["primalaspid"])
async def randomizerseed(ctx, *args):
    seed = [random_builtin.randint(1, 9)]
    seed += [random_builtin.randint(0, 9) for k in range(8)]
    g = ""
    for each in seed:
        g += str(each)
    if len(args) > 0 and args[0] == "m":
        await zote.send_message(ctx.message.author, f"Your randomizer seed is {g}. {randomizer_taunt()}")
    else:
        await zote.say(f"Your randomizer seed is {g}. {randomizer_taunt()}")


@zote.command(name="resources", pass_context=True)
@logger("speedrunning", ["zote"])
async def resources(ctx, *args):
    """Quick link to speedrun.com guides"""
    await zote.say("https://www.speedrun.com/hollowknight/resources")


@zote.command(name="spoilers", pass_context=True, aliases=["nospoilers", "spoiler", "spoileralert"])
@logger("psa", ["happygrub"])
async def spoilers(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(general_psa())


@zote.command(name="splrs", pass_context=True, aliases=["psa"])
@logger("psa", ["happygrub"])
async def splrs(ctx, *args):
    """ A friendly reminder for #general"""
    await zote.say(splr_lrt())


@zote.command(name="wiki", pass_context=True, aliases=["askzote", "<:dunq:335555573481472000>"])
@logger("ref", ["zote"])
async def wiki(ctx, *args):
    if len(args) == 0:
        await zote.say(f"{wiki_str}Zote, The Mighty")
        return -1
    r = args[0]
    for each in args[1:]:
        r = f"{r} {each.lower()}"
    query = wiki_search(r)
    if query == "None found":
        await zote.add_reaction(ctx.message, reactions["no"])
        return -1
    await zote.say(f"<{query}>")


#####################
"""ZOTE'S PRECEPTS"""
#####################


@zote.command(name="precept", pass_context=True, aliases=["wisdom", "<:zote:371947495330414595>"])
@logger("meme", ["zote"])
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
    await zote.say(f"Precept {p}")


#################
"""ENEMY ICONS"""
#################


@zote.command(name="enemy", pass_context=True, aliases=["monster", "hj", "hunter", "hunterjournal"])
@logger("ref", ["zote"])
async def enemy(ctx, *args):
    """See enemy icons! Shows Zote by default, but specify the enemy name (e.g Primal Aspid) to see its icon."""
    if len(args) == 0:
        await zote.add_reaction(ctx.message, reactions["zote"])
    else:
        r = args[0].capitalize()
        for each in args[1:]:
            r = f"{r}_{each.capitalize()}"
        get = zdn("hj", r + ".png")
        if get is not None:
            await zote.say(embed=embedify(get, r.replace("_", " ")))
        else:
            await zote.add_reaction(ctx.message, reactions["primalaspid"])

##################
# IMAGE COMMANDS #
##################


def get_kind(data):

    if data["kind"] == "multi":
        async def multi(ctx, *args): await zote.say(embed=embedify(zdn(data["loc"])))
        return multi

    if data["kind"] == "single":
        async def single(ctx, *args): await zote.say(embed=embedify(zdn(data["loc"], data["img"])))
        return single


print("Loading commands...")
COG = Index.open("data/cog.cxr")

for e in COG:
    # print(e.tag)
    try:
        if e.tag:
            # retrieve appropriate function from data
            cmd = get_kind(e)
            cmd.__name__ = e.tag

            # apply parameterized wrapper from logger
            cmd = logger(e["category"], e.all_of("reaction"))(cmd)

            # submit command to client
            zote.command(name=e.tag, pass_context=True, aliases=e.all_of("alias"))(cmd)
    except QoidError:
        print(f"Ignoring read exception in #{e.tag}")
    except discord.errors.ClientException as dece:
        print(f"Issue adding command {e.tag}, check aliases", dece)


#######################
## IMAGE SUBMISSIONS ##
#######################


@zote.command(name="submit", pass_context=True, aliases=[])
@logger("meme", ["zote"])
async def submit_meme(ctx, *args):
    u_name = ctx.message.author.name
    u_id = ctx.message.author.id
    if len(ctx.message.attachments) > 0:
        for each in ctx.message.attachments:
            e = embedify(each["url"], f"{u_name}: {u_id}")
            m = await zote.send_message(zote.submissions, embed=e)
            await zote.edit_message(m, new_content=f"{m.id}", embed=e)
    elif len(ctx.message.embeds) > 0:
        for each in ctx.message.embeds:
            e = embedify(each["url"], f"{u_name}: {u_id}")
            m = await zote.send_message(zote.submissions, embed=e)
            await zote.edit_message(m, new_content=f"{m.id}", embed=e)


@zote.command(name="accept", pass_context=True, aliases=["a"])
@logger("modonly", ["zote"])
async def accept_meme(ctx, *args):
    msg = args[0]
    repo = args[1] if len(args) > 1 else zote.get_channel(config["init"]["zdn_meme"])
    if msg and repo:
        e = msg.embeds[0]
        u = e["image"]["url"]
        if "imgur.com" in u:
            u.replace("imgur.com", "i.imgur.com")
            u += ".png"
        if "gfycat.com" in u:
            u.replace("gfycat.com", "thumbs.gfycat.com")
            u += "-size_restricted.gif"
        u_ext = u.rsplit('.', 1)[-1]
        img_data = requests.get(u).content
        with open(f"img/t-{msg.id}.{u_ext}", 'wb+') as img_file:
            img_file.write(img_data)
        ref = await zote.send_file(destination=repo, fp=f"img/t-{msg.id}.{u_ext}", filename=f"{msg.id}.{u_ext}")
        await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Accepted to #{repo.name}"))
        zote.ZDN[repo.name].add(ref.attachments[0]["url"])
        await zote.delete_message(msg)
        await zote.delete_message(ctx.message)
        os.remove(f"img/t-{msg.id}.{u_ext}")
    else:
        await zote.add_reaction(ctx.message, reactions["no"])


@zote.command(name="reject", pass_context=True, aliases=["r"])
@logger("modonly", ["zote"])
async def reject_meme(ctx, *args):
    msg = args[0]
    reason = ctx.message.content.split(" ", 2)[2]
    if msg:
        e = msg.embeds[0]
        u = e["image"]["url"]
        u_ext = u.rsplit('.', 1)[-1]
        await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Rejected: {reason}"))
        await zote.delete_message(msg)
        await zote.delete_message(ctx.message)
    else:
        await zote.add_reaction(ctx.message, reactions["no"])


@zote.command(name="move", pass_context=True, aliases=["m"])
@logger("modonly", ["zote"])
async def move_meme(ctx, *args):
    # move msgID #channel
    # download image from message, remove from ImgChannel
    # upload to #channel, add to ImgChannel
    # delete command call
    msg_from = args[0]
    ch_from = ctx.message.channel.name
    ch_to = args[1]
    if msg_from:
        e = msg_from.attachments[0]
        u = e["url"]
        u_ext = u.rsplit('.', 1)[-1]
        img_data = requests.get(u).content
        with open(f"img/t-{msg_from.id}.{u_ext}", 'wb+') as img_file:
            img_file.write(img_data)
        ref = await zote.send_file(destination=ch_to, fp=f"img/t-{msg_from.id}.{u_ext}", filename=f"{msg_from.id}.{u_ext}")
        zote.ZDN[ch_from].remove(u if ch_from in config["img"] else u.rsplit("/", 1)[0])  # change, rmeove "tagged img"
        zote.ZDN[ch_to.name].add(ref.attachments[0]["url"])
        await zote.delete_message(msg_from)
        await zote.delete_message(ctx.message)
        os.remove(f"img/t-{msg_from.id}.{u_ext}")
    else:
        await zote.add_reaction(ctx.message, reactions["no"])


@zote.command(name="delete", pass_context=True, aliases=["d"])
@logger("modonly", ["zote"])
async def delete_meme(ctx, *args):
    # _delete [msgID]
    # remove from ImgChannel
    # delete msgID
    n = ctx.message.channel.name
    a = args[0].attachments[0]["url"]
    zote.ZDN[n].remove(a if n in config["img"] else a.rsplit("/", 1)[0])
    await zote.delete_message(ctx.message)
    await zote.delete_message(args[0])


@zote.command(name="clone", pass_context=True, aliases=["c"])
@logger("modonly", ["zote"])
async def clone(ctx, *args):
    # clone msgID #channel
    # download image from message
    # upload to #channel, add to ImgChannel
    msg_from = args[0]
    ch_from = ctx.message.channel.name
    ch_to = args[1]
    if msg_from:
        e = msg_from.attachments[0]
        u = e["url"]
        u_ext = u.rsplit('.', 1)[-1]
        img_data = requests.get(u).content
        with open(f"img/t-{msg_from.id}.{u_ext}", 'wb+') as img_file:
            img_file.write(img_data)
        ref = await zote.send_file(destination=ch_to, fp=f"img/t-{msg_from.id}.{u_ext}",
                                   filename=f"{msg_from.id}.{u_ext}")
        zote.ZDN[ch_to.name].add(ref.attachments[0]["url"])
        await zote.delete_message(ctx.message)
        os.remove(f"img/t-{msg_from.id}.{u_ext}")
    else:
        await zote.add_reaction(ctx.message, reactions["no"])


##########
# EVENTS #
##########

@zote.event
async def on_message(message):
    raw = message.content.lower()
    message.content = raw
    try:
        await zote.process_commands(message)
    except discord.ext.commands.CheckFailure as e:
        print("Check failed")
    except discord.ext.commands.CommandNotFound as e:
        print("Command not Found")
    try:
        if message.channel.id == config["ch"]["meme"]:
            if message.author.id == "312125463952883712":
                await zote.add_reaction(message, reactions["hollowwow"])
            for word in raw.split(" "):
                if "zote" in word or "<@297840101944459275>" in word:
                    await zote.add_reaction(message, reactions["zote"])
                if "dab" in word:
                    await zote.add_reaction(message, reactions["hollowdab"])
                if "whomst" in word:
                    await zote.add_reaction(message, reactions["hollowface"])
        if message.channel.id == config["ch"]["general"] or message.channel.id == config["ch"]["bots"]:
            pass
            # for s in blacklist:
            #     if s in message.content.lower():
            #         print(f"Deleted spoiler {s} in $general")
            #         await zote.delete_message(message)
            #         await zote.send_message(
            #             message.author, f"{splr_lrt()}\n*(You received this message for saying the spoiler  \"{s}\")*")
            #         break
    except discord.errors.Forbidden as f:
        pass

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
