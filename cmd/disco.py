"""
Some happy little helper methods for discord.py
"""

from discord import Embed, HTTPException
from qoid import Qoid, Property


def embedify(url, desc=None):
    out = Embed()
    out.set_image(url=url)
    if desc is not None:
        out.description = desc
    return out


def qoidify_server_channels(zote, s_id: str, tag=None):
    server = zote.get_server(s_id)
    out = Qoid(tag=tag if tag else server.name)
    for ch in server.channels:
        out += Property(ch.name, ch)
    return out


async def sanitize(zote, ctx_ch, *args):
    """
    Convert valid discord ID numbers into messages

    :param zote: the discord.Client which will retrieve info from the API
    :param ctx_ch: the channel in which the command was executed
    :param args: the original arguments passed in the message
    :return: the
    """
    out = []
    for a in args:
        # Test argument for Server
        serv_a = zote.get_server(a)
        # print(f"serv: {type(serv_a)}")
        if serv_a:
            try:
                out.append(await serv_a)
                continue
            except HTTPException:
                pass

        # Test argument for Channel
        ch_a = zote.get_channel(a[2:-1] if a.startswith("<#") and a.endswith(">") else a)
        # print(f"ch: {type(ch_a)}")
        if ch_a:
            out.append(ch_a)
            continue

        # Test argument for Message
        msg_a = zote.get_message(ctx_ch, a)
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
            usr_a = zote.get_user_info(a[i:-1])
            # print(f"ch: {type(ch_a)}")
            if usr_a:
                try:
                    out.append(await usr_a)
                    continue
                except HTTPException:
                    pass
        out.append(a)
    return tuple(out)
