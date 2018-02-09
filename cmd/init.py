from data import *
from discord.ext.commands import Bot
import discord
from zdn import *

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")


zote = Bot(command_prefix=config["init"]["pre"])
zote.id = config["init"]["clientID"]
zote.ZDN = ImgServer()
zote.ZDN_server = ""
zote.remove_command("help")

# multi_frame = [e.tag for e in config["img"]]
# img = ImgDir(multi_frame)


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


# async def get_images(ch: discord.Channel, tagged=False):
#     i = []
#     bf = None
#     done = False
#     while not done:
#         prev = bf
#         async for m in zote.logs_from(channel=ch, limit=100, before=bf):
#             if len(m.attachments) == 1:
#                 i.append(m.attachments[0]["url"])
#             bf = m
#         if prev == bf:
#             done = True
#     zote.ZDN.add(ImgChannel(name=ch.name, links=i, tagged=tagged))


@zote.event
async def on_ready():
    print("Initializing...")
    start = time.time()
    zote.ZDN = ImgServer()
    for ch in config["img"]:
        with open("img/{0}.cxr".format(ch), "r") as f:
            o = []
            for e in f.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=False))
    for ch in config["tagged img"]:
        with open("img/{0}.cxr".format(ch), "r") as f:
            o = []
            for e in f.readlines():
                o.append(e.replace("\n", ""))
            zote.ZDN.add(ImgChannel(name=ch, links=o, tagged=True))

    # with open("data/img.cxr", "r") as f:
    #     o = []
    #     for e in f.readlines():
    #         o.append(e.replace("\n", ""))
    #     B = Bill(tag="img", source=o)
    #     for e in B:
    #         print(e)
    #         zote.ZDN.add(ImgChannel(name=e.tag, ser=e))

    # zote.ZDN_server = zote.get_server(config["init"]["zdn"])
    # for ch in zote.ZDN_server.channels:
    #     if ch.name in config["img"]:
    #         await get_images(ch, False)
    #     elif ch.name in config["tagged img"]:
    #         await get_images(ch, True)
    # for e in zote.ZDN.channels:
    #     print(e.val.get_qoid())
    print("ZDN initialized in {0}s.".format(format(time.time() - start, '.4f')))


def zdn(category: str, image=None):
    if image is None:
        return zote.ZDN[category].r()
    image = image.replace(" ", "_")
    return zote.ZDN[category][image]
