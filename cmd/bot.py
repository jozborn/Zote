import requests
import os

from random import randint
from discord import Channel, User, NotFound, HTTPException, DiscordException, PrivateChannel, Forbidden, Emoji, Game, Message
from discord.errors import ClientException
from discord.ext.commands import Bot, check
from data import wiki_str, wiki_search, log_error_message, log_command_usage
from qoid import Property, Qoid, Index, QoidError
from disco import embedify, sanitize
from time import time


def create_bot_instance(cfg: Index, dat: dict):
    inst = Bot(command_prefix=cfg["init"]["pre"], pm_help=True)
    reactions = {}
    for each in cfg["hk emoji"]:
        d = Emoji(
            require_colons=True, managed=False,
            name=each.tag, id=each.val,
            server=cfg["init"]["server"])
        reactions.update({each.tag: d})
    for each in cfg["discord emoji"]:
        reactions.update({each.tag: chr(int(each.val))})
    dat.update({"reactions": reactions})
    initialize_events(inst, cfg, dat)
    initialize_commands(inst, cfg, dat)
    return inst


def initialize_events(zote: Bot, cfg: Index, dat: dict):

    reactions = dat["reactions"]
    blacklist = dat["blacklist"]
    text = dat["text"]
    start = dat["start"]

    @zote.event
    async def on_command_error(exception, context): log_error_message(context.command.name, exception)

    @zote.event
    async def on_member_join(member):
        if member.server.id == cfg["init"]["server"]:
            num = member.server.member_count
            await zote.send_message(destination=zote.get_channel(cfg['ch']['joins-and-leaves']),
                                    content=f"`{num}` members - `{str(member)} ({member.id})` joined.")

    @zote.event
    async def on_member_remove(member):
        if member.server.id == cfg["init"]["server"]:
            num = member.server.member_count
            await zote.send_message(destination=zote.get_channel(cfg['ch']['joins-and-leaves']),
                                    content=f"`{num}` members - `{str(member)} ({member.id})` left.")

    @zote.event
    async def on_message(message):
        raw = message.content.lower()
        message.content = raw
        try:
            await zote.process_commands(message)
            if message.channel.id == cfg["ch"]["meme"]:
                for word in raw.split(" "):
                    if "zote" in word or "<@297840101944459275>" in word:
                        await zote.add_reaction(message, reactions["zote"])
                    if "dab" in word:
                        await zote.add_reaction(message, reactions["hollowdab"])
                    if "whomst" in word:
                        await zote.add_reaction(message, reactions["hollowface"])
            if message.channel.id == cfg["ch"]["general"] or message.channel.id == cfg["ch"]["bots"]:
                bad_word = blacklist(message.content.lower())
                if bad_word:
                    print(f"Deleted spoiler {s} in $general")
                    await zote.delete_message(message)
                    await zote.send_message(
                        message.author,
                        f"{text['short_psa']}\n*(You received this message for saying the spoiler  \"{bad_word}\")*")
        except Forbidden as f:
            pass

    @zote.event
    async def on_message_edit(before, message):
        raw = message.content.lower()
        message.content = raw
        try:
            await zote.process_commands(message)
            if message.channel.id == cfg["ch"]["meme"]:
                for word in raw.split(" "):
                    if "zote" in word or "<@297840101944459275>" in word:
                        await zote.add_reaction(message, reactions["zote"])
                    if "dab" in word:
                        await zote.add_reaction(message, reactions["hollowdab"])
                    if "whomst" in word:
                        await zote.add_reaction(message, reactions["hollowface"])
            if message.channel.id == cfg["ch"]["general"] or message.channel.id == cfg["ch"]["bots"]:
                bad_word = blacklist(message.content.lower())
                if bad_word:
                    print(f"Deleted spoiler {s} in $general")
                    await zote.delete_message(message)
                    await zote.send_message(
                        message.author,
                        f"{text['short_psa']}\n*(You received this message for saying the spoiler  \"{bad_word}\")*")
        except Forbidden as f:
            pass

    @zote.event
    async def on_ready():
        zote.submissions = zote.get_channel(cfg["zdn"]["submissions"])
        zote.delet = zote.get_channel(cfg["zdn"]["delet-this"])
        zote.log = zote.get_channel(cfg["zdn"]["log"])
        await zote.change_presence(game=Game(name="_help  _wherememes", type=0))
        print(f"ZDN initialized in {format(time() - start, '.4f')}s.")

    @zote.event
    async def wait_until_login():
        pass


cooldown = 0
lim = 3


def initialize_commands(zote: Bot, cfg: Index, dat: dict):

    reactions = dat["reactions"]
    text = dat["text"]
    img = dat["img"]
    che = dat["cache"]

    def _validator(category):

        def predicate(ctx):
            global cooldown
            global lim
            ch_name = ctx.message.channel.name if ctx.message.channel else "DM"
            ch_id = ctx.message.channel.id if ctx.message.channel else None
            s_id = ctx.message.server.id if ctx.message.server else None
            u_id = ctx.message.author.id

            if u_id in cfg["permamute"]:
                return False
            elif u_id in cfg["mods"]:
                return True
            elif category == "devplus":
                return u_id in cfg["devs"]
            elif category == "artsquad":
                return u_id in cfg["artsquad"] and s_id == cfg["zdn"]["server"]
            elif u_id in cfg["ignored"] or ch_id in cfg["silenced"]:
                return False
            elif isinstance(ctx.message.channel, PrivateChannel) or ctx.message.server.id != cfg["init"]["server"]:
                return category != "modonly" and cooldown < lim
            elif category != "modonly":
                return ch_name in cfg[category] and cooldown < lim
            else:
                return False

        return check(predicate)

    def logger(category, reaction):

        def wrap(f):

            @_validator(category)
            async def wrapped(ctx, *args):
                nonlocal che
                ch_id = ctx.message.channel.id
                s_id = ctx.message.server.id if ctx.message.server else None
                m_id = ctx.message.id

                global cooldown
                try:
                    try:
                        log_command_usage(f.__name__, ctx)
                    except Exception:
                        print(">>>> log error")
                    cooldown += 1
                    try:
                        if isinstance(reaction, list):
                            for each in reaction:
                                try:
                                    await zote.add_reaction(ctx.message, reactions[each])
                                except Forbidden:
                                    pass
                        else:
                            try:
                                await zote.add_reaction(ctx.message, reactions[reaction])
                            except Forbidden:
                                pass
                    except Exception as e:
                        try:
                            await zote.add_reaction(ctx.message, reactions["no"])
                        except Forbidden:
                            pass
                    args = await sanitize(zote, ctx.message.channel, *args)
                    await f(ctx, *args)
                    if s_id and "_meme" not in f.__name__ and f.__name__ != "meta":
                        record_msg(ctx.message)
                        if len(che[ch_id]) > 6:
                            try:
                                await zote.delete_message(await zote.get_message(ctx.message.channel, che[ch_id].get(index=0).tag))
                            except NotFound: pass
                            except Forbidden: pass
                            che[ch_id].remove(0)
                            try:
                                await zote.delete_message(await zote.get_message(ctx.message.channel, che[ch_id].get(index=0).tag))
                            except NotFound: pass
                            except Forbidden: pass
                            che[ch_id].remove(0)
                        che.save(echo=False)
                    if f.__name__ in cfg["flaggers"]:
                        cfg.save(echo=False)
                    cooldown -= 1
                except Exception as exc:
                    log_error_message(f.__name__, exc)
                    cooldown -= 1
                    try:
                        await zote.add_reaction(ctx.message, reactions["no"])
                    except Forbidden:
                        pass

            return wrapped

        return wrap

    def record_msg(m: Message):
        nonlocal che
        if m.server.id:
            if m.channel.id:
                if m.channel.id in che:
                    if m.id not in che[m.channel.id]:
                        che[m.channel.id] += Property(m.id)
                else:
                    che += Qoid(tag=m.channel.id)
                    che[m.channel.id] += Property(m.id)
                che.save(echo=False)

    @zote.command(name="ignore", pass_context=True, hidden=True)
    @logger("modonly", ["happygrub"])
    async def ignore(ctx, *args):
        """Ignore users based on their ID
        """
        try:
            a = args[0]
            if a.id in cfg["mods"]:
                print("Cannot ignore moderators or administrators")
                await zote.add_reaction(ctx, reactions["no"])
            elif a.id not in cfg["ignored"]:
                cfg["ignored"] += Property(tag=a.id, val=None)
                await zote.say(f"Now ignoring {str(a)}")
            else:
                cfg["ignored"] -= a.id
                await zote.say(f"Stopped ignoring {str(a)}")
        except NotFound:
            print("Could not find user")
        except HTTPException:
            print("HTTP error of some sort")

    @zote.command(name="silence", pass_context=True, hidden=True)
    @logger("modonly", ["happygrub"])
    async def silence(ctx, *args):
        a = args[0]
        if a.id not in cfg["silenced"]:
            cfg["silenced"] += Property(tag=a.id, val=None)
            await zote.add_reaction(ctx.message, reactions["on"])
        else:
            cfg["silenced"] -= a.id
            await zote.add_reaction(ctx.message, reactions["off"])

    @zote.command(name="ignorelist", pass_context=True, hidden=True)
    @logger("modonly", ["happygrub"])
    async def ignorelist(ctx, *args):
        if len(cfg["ignored"]) > 0:
            out = "**Ignored members**\n"
            for u_id in cfg["ignored"]:
                u = await zote.get_user_info(u_id)
                out += f"{u.name}#{u.discriminator}: {u_id}\n"
            await zote.say(out)
        else:
            await zote.say("No ignored members. Good!")

    @zote.command(name="modonly", pass_context=True, hidden=True, aliases=["modhelp", "modcommands"])
    @logger("modonly", ["happygrub"])
    async def modonly(ctx, *args): await zote.say(text["mod_help"])

    @zote.command(name="clear", pass_context=True, hidden=True)
    @logger("modonly", [])
    async def clear(ctx, *args):
        if not args:
            await zote.add_reaction(ctx.message, reactions["dunq"])
            return
        del_cmd = False
        try:
            del_limit = 500
            # Step 0: gather from args
            delcount = 1
            arg1 = arg2 = None
            if args:
                try:
                    delcount = del_limit if args[0] == "all" else int(args[0])
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
            # Note that multiple channels or users will be consumed
            if arg1:
                if isinstance(arg1, Channel):
                    ch = arg1
                elif isinstance(arg1, User):
                    us = arg1.id

                if isinstance(arg2, Channel):
                    ch = arg2
                elif isinstance(arg2, User):
                    us = arg2.id
            if not ch:
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
                        break
                    elif len(marked) == 100:
                        await zote.delete_messages(marked)
                        marked = []
                if prev == bf:
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
        except DiscordException as e:
            print(f">>> >>> {e}")
            if not del_cmd:
                await zote.add_reaction(ctx.message, reactions["dunq"])

    @zote.command(name="members", pass_context=True, hidden=True, aliases=["membercount"])
    @logger("modonly", ["happygrub"])
    async def member_count(ctx, *args):
        m = await zote.say(f"**{ctx.message.server.member_count}** members in the server.")
        record_msg(m)

    ###############################
    """CHANNEL-SPECIFIC COMMANDS"""
    ###############################

    @zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
    @logger("meme", ["zote"])
    async def gitgud(ctx, *args):
        """IMPROVE YOURSELF"""
        chance = randint(0, 10)
        if chance <= 1 or ctx.message.author.id in cfg["mods"] + cfg["woke"] + cfg["devs"] + cfg["hunger"]:
            await zote.add_reaction(ctx.message, reactions["hollowwoke"])
            m = await zote.say(embed=img["reaction"]["gitwoke.jpg"])
            record_msg(m)
        else:
            m = await zote.say(embed=img["reaction"]["gitgud.png"])
            record_msg(m)

    @zote.command(name="guides", pass_context=True, aliases=["guide", "speedrunguide"])
    @logger("speedrunning", ["zote"])
    async def guides(ctx, *args):
        m = await zote.say(text["sr_guides"])
        record_msg(m)

    @zote.command(name="hundred", pass_context=True, aliases=["100", "completion", "💯"])
    @logger("ref", ["happygrub"])
    async def hundred(ctx, *args):
        m = await zote.say(text["100"])
        record_msg(m)

    @zote.command(name="random", pass_context=True, aliases=["randomizer", "seed"])
    @logger("speedrunning", ["primalaspid"])
    async def randomizerseed(ctx, *args):
        seed = [randint(1, 9)]
        seed += [randint(0, 9) for k in range(8)]
        g = ""
        for each in seed:
            g += str(each)
        if len(args) > 0 and args[0] == "m":
            m = await zote.send_message(ctx.message.author, f"Your randomizer seed is {g}. {text['randomizer']()}")
            record_msg(m)
        else:
            m = await zote.say(f"Your randomizer seed is {g}. {text['randomizer']()}")
            record_msg(m)

    @zote.command(name="resources", pass_context=True)
    @logger("speedrunning", ["zote"])
    async def resources(ctx, *args):
        m = await zote.say(text["sr_resources"])
        record_msg(m)

    @zote.command(name="spoilers", pass_context=True, aliases=["nospoilers", "spoiler", "spoileralert"])
    @logger("psa", ["happygrub"])
    async def spoilers(ctx, *args):
        m = await zote.say(text["long_psa"])
        record_msg(m)

    @zote.command(name="splrs", pass_context=True, aliases=["psa"])
    @logger("psa", ["happygrub"])
    async def splrs(ctx, *args):
        m = await zote.say(text["short_psa"])
        record_msg(m)

    @zote.command(name="wiki", pass_context=True, aliases=["askzote", "<:dunq:335555573481472000>"])
    @logger("ref", ["zote"])
    async def wiki(ctx, *args):
        if len(args) == 0:
            await zote.say(f"{wiki_str}Zote, The Mighty")
        else:
            r = args[0]
            for each in args[1:]:
                r = f"{r} {each.lower()}"
            query = wiki_search(r)
            if query == "None found":
                await zote.add_reaction(ctx.message, reactions["no"])
            else:
                m = await zote.say(f"<{query}>")
                record_msg(m)


    #####################
    """ZOTE'S PRECEPTS"""
    #####################

    zote.precept_num = randint(0, 56)

    @zote.command(name="precept", pass_context=True, aliases=["wisdom", "<:zote:371947495330414595>"])
    @logger("meme", ["zote"])
    async def precept(ctx, *args):
        """Hear the precepts of Zote!

         Specify a number from 1 to 57
         for a specific precept,
         or hear them in order.`
        """
        try:
            p = cfg["precepts"].get(index=(int(args[0]) - 1) % 57)
        except Exception as e:
            p = cfg["precepts"].get(index=zote.precept_num)
            zote.precept_num += 1
        m = await zote.say(f"Precept {p}")
        record_msg(m)


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
            get = img["hj"][r + ".png"]
            if get is not None:
                get.description = r.replace("_", " ")
                m = await zote.say(embed=get)
                record_msg(m)
            else:
                await zote.add_reaction(ctx.message, reactions["primalaspid"])

    @zote.command(name="meta", pass_context=True, hidden=True, aliases=[])
    @logger("meme", [])
    async def meta_command(ctx, *args):
        await zote.delete_message(ctx.message)

    ##################
    # IMAGE COMMANDS #
    ##################

    def get_kind(data):

        if data["kind"] == "multi":
            async def multi(ctx, *args):
                em = img.r(data["loc"])
                m = await zote.send_message(destination=ctx.message.channel, embed=em)
                record_msg(m)
            return multi

        if data["kind"] == "single":
            async def single(ctx, *args):
                em = img[data["loc"]][data["img"]]
                m = await zote.send_message(destination=ctx.message.channel, embed=em)
                record_msg(m)
            return single

    @zote.command(name="broke", hidden=False, pass_context=True, aliases=["badlink"])
    @logger("meme", ["sadgrub"])
    async def broke_meme_link(ctx, *args):
        await zote.send_message(await zote.get_user_info(151542934892707840), str(args[0].embeds[0]["image"]["url"]))

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
        except ClientException as dece:
            print(f"Issue adding command {e.tag}, check aliases", dece)


    #####################
    # IMAGE SUBMISSIONS #
    #####################

    async def clone_img_loc(ctx_message, msg_from, ch_to, del_old=False):
        e = msg_from.attachments[0]
        u = e["url"]
        u_ext = u.rsplit('.', 1)[-1]
        img_data = requests.get(u).content
        with open(f"data/t-{msg_from.id}.{u_ext}", 'wb+') as img_file:
            img_file.write(img_data)
        ref = await zote.send_file(destination=ch_to, fp=f"data/t-{msg_from.id}.{u_ext}",
                                   filename=f"{msg_from.id}.{u_ext}")
        if ch_to.id != cfg["zdn"]["artist-exclusions"]:
            img.add_image(ch_to.name, ref.attachments[0]["url"])
        await zote.delete_message(ctx_message)
        if del_old:
            ch_from = ctx_message.channel.name
            img.remove_image(ch_from, u.rsplit("/", 1)[0] if eval(img[ch_from]["tagged"]) else u)
            await zote.delete_message(msg_from)
        os.remove(f"data/t-{msg_from.id}.{u_ext}")

    @zote.command(name="accept", hidden=True, pass_context=True, aliases=["a"])
    @logger("modonly", ["zote"])
    async def accept_meme(ctx, *args):
        msg = args[0]
        repo = args[1] if len(args) > 1 else zote.get_channel(cfg["zdn"]["meme"])
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
            with open(f"data/t-{msg.id}.{u_ext}", 'wb+') as img_file:
                img_file.write(img_data)
            ref = await zote.send_file(destination=repo, fp=f"data/t-{msg.id}.{u_ext}", filename=f"{msg.id}.{u_ext}")
            await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Accepted to #{repo.name}"))
            img.add_image(repo.name, ref.attachments[0]["url"])
            await zote.delete_message(msg)
            await zote.delete_message(ctx.message)
            os.remove(f"data/t-{msg.id}.{u_ext}")
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="exclude", hidden=True, pass_context=True, aliases=[])
    @logger("artsquad", ["zote"])
    async def exclude_meme(ctx, *args):
        if args[0]:
            await clone_img_loc(ctx.message, args[0], zote.get_channel(cfg["zdn"]["artist-exclusions"]), del_old=True)
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="clone", hidden=True, pass_context=True, aliases=["c"])
    @logger("modonly", ["zote"])
    async def clone_meme(ctx, *args):
        if args[0]:
            await clone_img_loc(ctx.message, args[0], args[1])
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="delete", hidden=True, pass_context=True, aliases=["d"])
    @logger("modonly", ["zote"])
    async def delete_meme(ctx, *args):
        n = ctx.message.channel.name
        a = args[0].attachments[0]["url"]
        img.remove_image(n, a.rsplit("/", 1)[0] if eval(img[n]["tagged"]) else a)
        await zote.delete_message(ctx.message)
        await zote.delete_message(args[0])

    @zote.command(name="deletelink", hidden=True, pass_context=True, aliases=["dl"])
    @logger("modonly", ["zote"])
    async def delete_by_link(ctx, *args):
        bf = ctx.message
        if ctx.message.server.id == cfg["zdn"]["server"]:
            found = False
            while not found:
                prev = bf
                async for msg in zote.logs_from(channel=ctx.message.channel, limit=100, before=bf, after=None):
                    for e in msg.attachments:
                        if args[0] == e['url']:
                            await zote.delete_message(msg)
                            img.remove_image(ctx.message.channel.name, args[0])
                            img.save_source(echo=False)
                            found = True
                            break
                    bf = msg
                if prev == bf:
                    await zote.delete_message(ctx.message)
                    break

    @zote.command(name="deletthis", hidden=True, pass_context=True, aliases=[])
    @logger("meme", ["zote"])
    async def delet_this(ctx, *args):
        if len(ctx.message.embeds) > 0:
            for each in ctx.message.embeds:
                e = each["url"]
                await zote.send_message(zote.delet, content=e)

    @zote.command(name="move", hidden=True, pass_context=True, aliases=["m"])
    @logger("modonly", ["zote"])
    async def move_meme(ctx, *args):
        if args[0]:
            await clone_img_loc(ctx.message, args[0], args[1], del_old=True)
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="reject", hidden=True, pass_context=True, aliases=["r"])
    @logger("modonly", ["zote"])
    async def reject_meme(ctx, *args):
        msg = args[0]
        reason = ctx.message.content.split(" ", 2)[2] if len(args) >= 2 else "bad meme"
        if msg:
            e = msg.embeds[0]
            u = e["image"]["url"]
            await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Rejected: {reason}"))
            await zote.delete_message(msg)
            await zote.delete_message(ctx.message)
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="submit", hidden=True, pass_context=True, aliases=[])
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

    @zote.command(name="zdn", hidden=False, pass_context=True, aliases=["wherememes"])
    @logger("meme", ["zote"])
    async def where_memes(ctx, *args):
        await zote.say("https://discord.gg/kqdCYZE")

    @zote.command(name="embed", hidden=False, pass_context=True, aliases=["em"])
    @logger("modonly", ["zote"])
    async def get_embed(ctx, *args):
        m = args[0]
        for e in m.embeds:
            await zote.say(f"```\n{e}\n```")

    @zote.command(name="jonnypls", hidden=False, pass_context=True, aliases=["gng"])
    @logger("meme", ["teamcherry"])
    async def jonnypls(ctx, *args):
        await zote.say("Gods and Glory has not yet been announced.")

