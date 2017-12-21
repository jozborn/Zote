from data import *
from discord.ext.commands import Bot

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")

zote = Bot(command_prefix=pre)
zote.id = hk_qoid["init"]["clientID"]
zote.remove_command("help")

config = Config()
