import requests
import os

from random import randint
from discord import Channel, User, NotFound, HTTPException, DiscordException, PrivateChannel, Forbidden
from discord.errors import ClientException
from discord.ext.commands import Bot, check

# These should all be passed in to initialize_commands
from cfg import text, reactions

from log import wiki_str, wiki_search, log_command_usage, log_error_message
from qoid import Property, Index, QoidError
from zdn import ImgServer, embedify
from zote import sanitize_arguments


cooldown = 0
_lim = 3


def initialize_commands(zote: Bot, cfg: Index, img: ImgServer):

    def _validator(category):

        def predicate(ctx):
            global cooldown
            global _lim
            ch_name = ctx.message.channel.name
            ch_id = ctx.message.channel.id
            u_id = ctx.message.author.id

            if u_id in cfg["mods"]:
                return True
            elif category == "devplus":
                return u_id in cfg["devs"]
            elif isinstance(ctx.message.channel, PrivateChannel) or ctx.message.server.id != cfg["init"]["server"]:
                return category != "modonly" and cooldown < _lim
            elif u_id in cfg["ignored"] or ch_id in cfg["silenced"]:
                return False
            elif category != "modonly":
                return ch_name in cfg[category] and cooldown < _lim
            else:
                return False

        return check(predicate)

    def logger(category, reaction):

        def wrap(f):

            @_validator(category)
            async def wrapped(ctx, *args):
                global cooldown
                try:
                    try:
                        log_command_usage(f.__name__, ctx)
                    except Exception:
                        print("log error")
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
                    args = await sanitize_arguments(zote, ctx.message.channel, *args)
                    await f(ctx, *args)
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
                cfg["ignored"] -= a
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
                out += f"{u.name}#{u.id}: {u_id}\n"
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
                        print(len(marked))
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
        await zote.say(f"**{ctx.message.server.member_count}** members in the server.")

    ###############################
    """CHANNEL-SPECIFIC COMMANDS"""
    ###############################

    @zote.command(name="gitgud", pass_context=True, aliases=["waifu"])
    @logger("meme", ["zote"])
    async def gitgud(ctx, *args):
        """IMPROVE YOURSELF"""
        chance = randint(0, 10)
        if ctx.message.author.id == "312125463952883712":  # To mess with FuzzyD
            await zote.say(embed=embedify("https://cdn.discordapp.com/attachments/417908285405134849/421784416113917954/421784116028243978.png"))
        elif chance <= 1 or ctx.message.author.id in cfg["mods"] + cfg["woke"] + cfg["devs"]:
            await zote.add_reaction(ctx.message, reactions["hollowwoke"])
            await zote.say(embed=img["reaction", "gitwoke.jpg"])
        else:
            await zote.say(embed=img["reaction", "gitgud.png"])

    @zote.command(name="guides", pass_context=True, aliases=["guide", "speedrunguide"])
    @logger("speedrunning", ["zote"])
    async def guides(ctx, *args): await zote.say(text["sr_guides"])

    @zote.command(name="hundred", pass_context=True, aliases=["100", "completion", "💯"])
    @logger("ref", ["happygrub"])
    async def hundred(ctx, *args): await zote.say(text["100"])

    @zote.command(name="random", pass_context=True, aliases=["randomizer", "seed"])
    @logger("speedrunning", ["primalaspid"])
    async def randomizerseed(ctx, *args):
        seed = [randint(1, 9)]
        seed += [randint(0, 9) for k in range(8)]
        g = ""
        for each in seed:
            g += str(each)
        if len(args) > 0 and args[0] == "m":
            await zote.send_message(ctx.message.author, f"Your randomizer seed is {g}. {text['randomizer']()}")
        else:
            await zote.say(f"Your randomizer seed is {g}. {text['randomizer']()}")

    @zote.command(name="resources", pass_context=True)
    @logger("speedrunning", ["zote"])
    async def resources(ctx, *args): await zote.say(text["sr_resources"])

    @zote.command(name="spoilers", pass_context=True, aliases=["nospoilers", "spoiler", "spoileralert"])
    @logger("psa", ["happygrub"])
    async def spoilers(ctx, *args): await zote.say(text["long_psa"])

    @zote.command(name="splrs", pass_context=True, aliases=["psa"])
    @logger("psa", ["happygrub"])
    async def splrs(ctx, *args): await zote.say(text["short_psa"])

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
            p = cfg["precepts"].get(index=(int(args[0]) - 1) % 57)
        except Exception as e:
            p = cfg["precepts"].get(index=int(cfg["init"]["precept#"]))
            cfg["init"].set(tag="precept#", val=str((int(cfg["init"]["precept#"]) + 1) % 57))
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
            get = img["hj", r + ".png"]
            if get is not None:
                get.description = r.replace("_", " ")
                await zote.say(embed=get)
            else:
                await zote.add_reaction(ctx.message, reactions["primalaspid"])

    ##################
    # IMAGE COMMANDS #
    ##################

    def get_kind(data):

        if data["kind"] == "multi":
            async def multi(ctx, *args): await zote.say(embed=img[data["loc"]])
            return multi

        if data["kind"] == "single":
            async def single(ctx, *args): await zote.say(embed=img[data["loc"], data["img"]])
            return single

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
        with open(f"img/t-{msg_from.id}.{u_ext}", 'wb+') as img_file:
            img_file.write(img_data)
        ref = await zote.send_file(destination=ch_to, fp=f"img/t-{msg_from.id}.{u_ext}",
                                   filename=f"{msg_from.id}.{u_ext}")
        img[ch_to.name].add(ref.attachments[0]["url"])
        await zote.delete_message(ctx_message)
        if del_old:
            ch_from = ctx_message.channel.name
            img[ch_from].remove(u if ch_from in cfg["img"] else u.rsplit("/", 1)[0])
            await zote.delete_message(msg_from)
        os.remove(f"img/t-{msg_from.id}.{u_ext}")

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
            with open(f"img/t-{msg.id}.{u_ext}", 'wb+') as img_file:
                img_file.write(img_data)
            ref = await zote.send_file(destination=repo, fp=f"img/t-{msg.id}.{u_ext}", filename=f"{msg.id}.{u_ext}")
            await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Accepted to #{repo.name}"))
            img[repo.name].add(ref.attachments[0]["url"])
            await zote.delete_messages([msg, ctx.message])
            os.remove(f"img/t-{msg.id}.{u_ext}")
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
        img[n].remove(a if n in cfg["img"] else a.rsplit("/", 1)[0])
        await zote.delete_messages([ctx.message, args[0]])

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
        reason = ctx.message.content.split(" ", 2)[2]
        if msg:
            e = msg.embeds[0]
            u = e["image"]["url"]
            await zote.send_message(destination=zote.log, embed=embedify(e['image']['url'], f"Rejected: {reason}"))
            await zote.delete_messages([msg, ctx.message])
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
