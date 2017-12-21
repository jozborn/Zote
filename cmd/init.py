from data import *
from discord.ext.commands import Bot

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")

zote = Bot(command_prefix=hkq["init"]["pre"])
zote.id = hkq["init"]["clientID"]
zote.remove_command("help")

config = Config()

multi_frame = [e.tag for e in hkq["img"]]
img = ImgDir(multi_frame)
