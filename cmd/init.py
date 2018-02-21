from data import *
from discord.ext.commands import Bot
import discord

zote = Bot(command_prefix=config["init"]["pre"])
zote.remove_command("help")
zote.id = config["init"]["clientID"]
zote.ZDN = ImgServer()
zote.ZDN_server = ""
reactions = {}


for each in config["hk emoji"]:
    d = discord.Emoji(
        require_colons=True, managed=False,
        name=each.tag, id=each.val,
        server=config["init"]["server"]
    )
    reactions.update({each.tag: d})

for each in config["discord emoji"]:
    reactions.update({each.tag: chr(int(each.val))})


@zote.event
async def on_ready():
    zote.ZDN = ImgServer()
    for ch in config["img"]:
        with open(f"img/{ch}.cxr", "r") as img_file:
            o = []
            for e in img_file.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=False))
    for ch in config["tagged img"]:
        with open(f"img/{ch}.cxr", "r") as img_file:
            o = []
            for e in img_file.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=True))
    print(f"ZDN initialized in {format(time.time() - start, '.4f')}s.")


def zdn(category: str, image=None):
    if image is None:
        return zote.ZDN[category].val.r()
    image = image.replace(" ", "_")
    return zote.ZDN[category][image]
