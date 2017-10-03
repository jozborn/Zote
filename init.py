from discord.ext.commands import Bot
from data import *
from stuff import *
from wiki import *
import discord

print("########################")
print("    Zote, The Mighty")
print("by Conrad @the_complexor")
print("########################\n")


pre = "_"
zote = Bot(command_prefix=pre)
zote.remove_command("help")
config = load()
