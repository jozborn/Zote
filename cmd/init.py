from data import *
from discord.ext.commands import Bot
from stuff import *

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")

zote = Bot(command_prefix=pre)
zote.id = "297840101944459275"
zote.remove_command("help")

with open("data/en.zote", "r") as f:
    for each in f.readlines():
        ENTRIES.append(each[:len(each) - 1])
with open("data/win.zote", "r") as f:
    for each in f.readlines():
        WINNERS.append(each[:len(each) - 1])
config = load()
