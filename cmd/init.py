from data import *
from discord.ext.commands import Bot
import discord
from zdn import *

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")


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
    print("Initializing...")
    start = time.time()
    zote.ZDN = ImgServer()
    for ch in config["img"]:
        with open("img/{0}.cxr".format(ch), "r") as img_file:
            o = []
            for e in img_file.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=False))
    for ch in config["tagged img"]:
        with open("img/{0}.cxr".format(ch), "r") as img_file:
            o = []
            for e in img_file.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=True))
    print("ZDN initialized in {0}s.".format(format(time.time() - start, '.4f')))


def zdn(category: str, image=None):
    if image is None:
        return zote.ZDN[category].r()
    image = image.replace(" ", "_")
    return zote.ZDN[category][image]
