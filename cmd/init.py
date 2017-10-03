from data import *
from discord.ext.commands import Bot
from stuff import *

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")


zote = Bot(command_prefix=pre)
zote.remove_command("help")
config = load()
