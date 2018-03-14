from cfg import start, reactions, blacklist, text
from log import log_error_message
from discord import Forbidden, HTTPException
from discord.ext.commands import Bot
from qoid import Index, Qoid, Property
from zdn import ImgChannel, ImgServer
from time import time


def initialize_events(zote: Bot, cfg: Index, zdn: ImgServer):

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
                if message.author.id == "312125463952883712":
                    await zote.add_reaction(message, reactions["hollowwow"])
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
        zote.log = zote.get_channel(cfg["zdn"]["log"])
        if not zdn.ready:
            print("Gathering command images...")
            for ch in cfg["img"]:
                zdn.add(ImgChannel.open(ch))
            for ch in cfg["tagged img"]:
                zdn.add(ImgChannel.open(ch, tagged=True))
            zdn.ready = True
        print(f"ZDN initialized in {format(time() - start(), '.4f')}s.")

    return zote


async def qoidify_server_channels(client, s_id: str, tag=None):
    server = client.get_server(s_id)
    out = Qoid(tag=tag if tag else server.name)
    for ch in server.channels:
        out += Property(ch.name, ch)
    return out


async def sanitize_arguments(client, ctx_ch, *args):
    """
    Convert valid discord ID numbers into messages

    :param client: the discord.Client which will retrieve info from the API
    :param ctx_ch: the channel in which the command was executed
    :param args: the original arguments passed in the message
    :return: the
    """
    out = []
    for a in args:
        # Test argument for Server
        serv_a = client.get_server(a)
        # print(f"serv: {type(serv_a)}")
        if serv_a:
            try:
                out.append(await serv_a)
                continue
            except HTTPException:
                pass

        # Test argument for Channel
        ch_a = client.get_channel(a[2:-1] if a.startswith("<#") and a.endswith(">") else a)
        # print(f"ch: {type(ch_a)}")
        if ch_a:
            out.append(ch_a)
            continue

        # Test argument for Message
        msg_a = client.get_message(ctx_ch, a)
        # print(f"msg: {type(msg_a)}")
        if msg_a:
            try:
                out.append(await msg_a)
                continue
            except HTTPException:
                pass

        # Test argument for User
        if a.startswith(("<@", "<@!")) and a.endswith(">"):
            i = 2 if a.startswith("<@") else 3
            usr_a = client.get_user_info(a[i:-1])
            # print(f"ch: {type(ch_a)}")
            if usr_a:
                try:
                    out.append(await usr_a)
                    continue
                except HTTPException:
                    pass
        out.append(a)
    return tuple(out)
