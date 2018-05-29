import requests
import os

from random import randint
from discord import Channel, User, NotFound, HTTPException, DiscordException,\
    PrivateChannel, Forbidden, Emoji, Game, Message
from discord.errors import ClientException
from discord.ext.commands import Bot, check
from data import wiki_str, wiki_search, log_error_message, log_command_usage
from qoid import Property, Qoid, Index, QoidError
from disco import sanitize
from time import time

from zutils import accept_and_log_meme, reject_and_log_meme, add_reactions, submit_and_mark_meme, check_message


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
    img = dat["img"]

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
        await check_message(zote, message, cfg, reactions, blacklist)

    @zote.event
    async def on_message_edit(before, message):
        del before  # ignored parameters
        await check_message(zote, message, cfg, reactions, blacklist)

    @zote.event
    async def on_ready():
        zote.submissions = zote.get_channel(cfg["zdn"]["submissions"])
        zote.delet = zote.get_channel(cfg["zdn"]["delet-this"])
        zote.log = zote.get_channel(cfg["zdn"]["log"])
        await zote.change_presence(game=Game(name=f"{cfg['init']['pre']}help {cfg['init']['pre']}wherememes", type=0))
        print(f"ZDN initialized in {format(time() - start, '.4f')}s.")

    @zote.event
    async def on_reaction_add(reaction, user):
        # verifies that non-zote reaction occurred in submissions
        msg = reaction.message
        if msg.channel.id == cfg["zdn"]["submissions"] and user.id != cfg["init"]["zote"]:
            # No vote
            if reaction.emoji == "❌":
                # Submitting user
                if msg.embeds[0]["description"].split(": ")[1] == user.id:
                    reason = "Cancelled by user"
                    await reject_and_log_meme(zote, msg, reason)
                # Mod or reject vote
                elif reaction.count > 6 or user.id in cfg["mods"]:
                    reason = "rejected by mod" if user.id in cfg["mods"] else "community voted no"
                    await reject_and_log_meme(zote, msg, reason)
            # Yes vote
            elif reaction.emoji == "✅":
                # Mod or accept vote
                if reaction.count > 10 or user.id in cfg["mods"]:
                    repo = zote.get_channel(cfg["zdn"]["meme"])
                    await accept_and_log_meme(zote, img, msg, repo)


cooldown = 0
lim = 3


def initialize_commands(zote: Bot, cfg: Index, dat: dict):

    reactions = dat["reactions"]
    text = dat["text"]
    img = dat["img"]
    che = dat["cache"]
    cogs = dat["cog"]

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
                ch_id = ctx.message.channel.id if ctx.message.channel else None
                s_id = ctx.message.server.id if ctx.message.server else None

                global cooldown
                try:
                    try:
                        log_command_usage(f.__name__, ctx)
                    except Exception:
                        # Yes I know, I'm sorry
                        print(">>>> log error")
                    cooldown += 1
                    await add_reactions(zote, ctx.message, reactions, reaction)
                    args = await sanitize(zote, ctx.message.channel, *args)
                    await f(ctx, *args)
                    if s_id and "_meme" not in f.__name__ and f.__name__ != "meta":
                        record_msg(ctx.message)
                        while len(che[ch_id]) > 6:
                            try:
                                m = await zote.get_message(ctx.message.channel, che[ch_id].get(index=0).tag)
                                await zote.delete_message(m)
                            except NotFound:
                                pass
                            except Forbidden:
                                pass
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
        if not m.server:
            return
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

    def add_bot_cogs():

        @zote.group(pass_context=True)
        async def cog(ctx):
            pass

        @cog.command(name="test", pass_context=True)
        @logger("modonly", ["zote"])
        async def cog_test(ctx, *args):
            await zote.say("Yup")

        @cog.command(name="view", pass_context=True)
        @logger("modonly", ["zote"])
        async def cog_view(ctx, *args):
            cog_name = args[0]
            try:
                ret = cogs[cog_name]
                await zote.say(f"```{str(ret)}```")
            except QoidError:
                await zote.add_reaction(ctx.message, reactions["no"])

        @cog.command(name="create", pass_context=True)
        @logger("modonly", ["zote"])
        async def cog_create(ctx, *args):
            nonlocal cogs
            cog_name = args[0]
            if cog_name not in cogs:
                cogs += Qoid(cog_name)
                cogs.save(echo=False)
                await zote.say("Done")
            else:
                await zote.say("Already exists")
            pass

        @cog.command(name="add", pass_context=True)
        @logger("modonly", ["zote"])
        async def cog_add(ctx, *args):
            nonlocal cogs
            try:
                cog_name = args[0]
                cog_tag = args[1]
                cog_val = args[2]
                cogs[cog_name] += Property(cog_tag, cog_val)
                cogs.save(echo=False)
            except IndexError:
                await zote.add_reaction(ctx.message, reactions["no"])

    add_bot_cogs()

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
        del ctx, args  # ignored parameters
        if len(cfg["ignored"]) > 0:
            out = "**Ignored members**\n"
            for u_id in cfg["ignored"]:
                u = await zote.get_user_info(u_id)
                out += f"{u.name}#{u.discriminator}: {u_id}\n"
            await zote.say(out)
        else:
            await zote.say("No ignored members. Good!")

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
        except DiscordException as de:
            print(f">>> >>> {de}")
            if not del_cmd:
                await zote.add_reaction(ctx.message, reactions["dunq"])

    @zote.command(name="members", pass_context=True, hidden=True, aliases=["membercount"])
    @logger("modonly", ["happygrub"])
    async def member_count(ctx, *args):
        del args  # ignored parameters
        m = await zote.say(f"**{ctx.message.server.member_count}** members in the server.")
        record_msg(m)

    ###############################
    """CHANNEL-SPECIFIC COMMANDS"""
    ###############################

    @zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
    @logger("meme", ["zote"])
    async def gitgud(ctx, *args):
        del args  # ignored parameters
        chance = randint(0, 10)
        if chance <= 1 or ctx.message.author.id in cfg["mods"] + cfg["woke"] + cfg["devs"] + cfg["hunger"]:
            await zote.add_reaction(ctx.message, reactions["hollowwoke"])
            m = await zote.say(embed=img["reaction"]["gitwoke.jpg"])
            record_msg(m)
        else:
            m = await zote.say(embed=img["reaction"]["gitgud.png"])
            record_msg(m)

    @zote.command(name="random", pass_context=True, aliases=["randomizer", "seed"])
    @logger("speedrunning", ["primalaspid"])
    async def randomizerseed(ctx, *args):
        seed = [randint(1, 9)]
        for k in range(8):
            seed.append(randint(0, 9))
        g = ""
        for each in seed:
            g += str(each)
        if len(args) > 0 and args[0] == "m":
            m = await zote.send_message(ctx.message.author, f"Your randomizer seed is {g}. {text['randomizer']()}")
            record_msg(m)
        else:
            m = await zote.say(f"Your randomizer seed is {g}. {text['randomizer']()}")
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
        del ctx  # ignored parameters
        if len(args) > 0 and isinstance(args[0], int):
            p = cfg["precepts"].get(index=(int(args[0]) - 1) % 57)
        else:
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
        del args  # ignored parameters
        await zote.delete_message(ctx.message)

    ##################
    # IMAGE COMMANDS #
    ##################

    def get_kind(data):

        async def multi_cmd(ctx, *args):
            del args  # ignored parameters
            em = img.r(data["loc"])
            m = await zote.send_message(destination=ctx.message.channel, embed=em)
            record_msg(m)

        async def single_cmd(ctx, *args):
            del args  # ignored parameters
            em = img[data["loc"]][data["img"]]
            m = await zote.send_message(destination=ctx.message.channel, embed=em)
            record_msg(m)

        async def text_cmd(ctx, *args):
            del args  # ignored parameters
            cnt = text[data["loc"]]
            m = await zote.send_message(destination=ctx.message.channel, content=cnt)
            record_msg(m)

        if data["kind"] == "multi":
            return multi_cmd
        elif data["kind"] == "single":
            return single_cmd
        elif data["kind"] == "text":
            return text_cmd

    for e in cogs:
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
            print(f"Ignoring read exception in #{e.tag}, command was not completed")
        except ClientException as dece:
            print(f"Issue adding command {e.tag}, check aliases", dece)

    #####################
    # IMAGE SUBMISSIONS #
    #####################

    async def clone_img_loc(ctx_message, msg_from, ch_to, del_old=False):
        atch = msg_from.attachments[0]
        u = atch["url"]
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
            await accept_and_log_meme(zote, img, msg, repo)
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
                    for each in msg.attachments:
                        if args[0] == each['url']:
                            await zote.delete_message(msg)
                            img.remove_image(ctx.message.channel.name, args[0])
                            img.save_source(echo=False)
                            found = True
                            break
                    bf = msg
                if prev == bf:
                    try:
                        img.remove_image(ctx.message.channel.name, args[0])
                    except QoidError:
                        pass
                    await zote.delete_message(ctx.message)
                    break

    @zote.command(name="deletthis", hidden=True, pass_context=True, aliases=[])
    @logger("meme", ["zote"])
    async def delet_this(ctx, *args):
        del args  # ignored parameters
        if len(ctx.message.embeds) > 0:
            for each in ctx.message.embeds:
                em = each["url"]
                await zote.send_message(zote.delet, content=em)

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
        reason = ctx.message.content.split(" ", 2)[2] if len(args) >= 2 else "Rejected by moderator"
        if msg:
            await reject_and_log_meme(zote, msg, reason)
            await zote.delete_message(ctx.message)
        else:
            await zote.add_reaction(ctx.message, reactions["no"])

    @zote.command(name="submit", hidden=True, pass_context=True, aliases=[])
    @logger("meme", ["zote"])
    async def submit_meme(ctx, *args):
        del args  # ignored parameters
        if ctx.message.server.id == cfg["zdn"]["server"] or ctx.message.author.id in cfg["mods"]:
            u_name = ctx.message.author.name
            u_id = ctx.message.author.id
            if len(ctx.message.attachments) > 0:
                for each in ctx.message.attachments:
                    await submit_and_mark_meme(zote, each, f"{u_name}: {u_id}", reactions)
            elif len(ctx.message.embeds) > 0:
                for each in ctx.message.embeds:
                    await submit_and_mark_meme(zote, each, f"{u_name}: {u_id}", reactions)
        else:
            await zote.add_reaction(ctx.message, reactions(["dunq"]))

    @zote.command(name="embed", hidden=False, pass_context=True, aliases=["em"])
    @logger("modonly", ["zote"])
    async def get_embed(ctx, *args):
        del ctx  # ignored parameters
        m = args[0]
        for em in m.embeds:
            await zote.say(f"```\n{em}\n```")

