from data import *
from discord.ext.commands import Bot
import discord

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")


zote = Bot(command_prefix=config["init"]["pre"])
zote.id = config["init"]["clientID"]
zote.remove_command("help")

multi_frame = [e.tag for e in config["img"]]
img = ImgDir(multi_frame)

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
