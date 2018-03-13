from random import randint
from qoid import Index
from time import time
from zdn import ImgServer
from discord import Emoji
from discord.ext.commands import Bot

cfg = Index.open("data/config.cxr")

inst = Bot(command_prefix=cfg["init"]["pre"], pm_help=True)
reactions = {}
for each in cfg["hk emoji"]:
    d = Emoji(
        require_colons=True, managed=False,
        name=each.tag, id=each.val,
        server=cfg["init"]["server"])
    reactions.update({each.tag: d})
for each in cfg["discord emoji"]:
    reactions.update({each.tag: chr(int(each.val))})
_start = time()
_zdn = ImgServer()


_blacklist = []
_blacklist_is_on = False
if _blacklist_is_on:
    with open("data/blacklist.zote", 'r+') as f:
        for each in f.readlines():
            _blacklist.append(each.replace("\n", ""))


def start(v=None):
    global _start
    if v:
        _start = v
    else:
        return _start


def blacklist(s: str):
    if _blacklist_is_on:
        for b in _blacklist:
            if b in s.lower():
                return b
    return None

#############
# MISC TEXT #
#############


_general_psa = f"""PSA: <#{cfg['ch']['general']}> is a spoiler-free channel.\n
This means no discussions past Crossroads.\n
If it requires progressing past Crossroads to unlock inside Crossroads, don't talk about it here.\n
If you need help with a specific portion of the game, ask in <#{cfg['ch']['help']}> and someone will answer.\n
If you wish to talk about the rest of the game or the lore or such, <#{cfg['ch']['discussion']}>\n
If you've drawn something or would like to talk about the art, <#{cfg['ch']['art']}>."""

_hundred_guide = "**100% guide**: https://docs.google.com/document/d/1smOruEIYHbPxsPVocX3RR3E5jrzhpq7RrXhOAocfZDE"

_modtext = f"""**MOD-ONLY COMMANDS:**\n
**ignore** [user id]: prevents the user from accessing Zote commands, or takes them off the ignore list.\n
**ignorelist** shows all users being ignored and their ID.\n
**silence** [#tag channel]: stops/starts Zote responding to commands in a channel\n
**clear** [x] or **clear** [@tag user] [x]: deletes X messages from a channel (or a user in that channel)\n
**clearzotes** [optional amount x]: deletes all _commands and posts from Zote, or the X most recent ones\n
**helpchannel**: clears all messages in the help channel and reposts the opening help message.\n
**ban**: reaction image of the False Knight's Banhammer (not an actual ban!)"""

_taunt_list = [
    "May you find Mantis Claw in King's Pass.",
    "If all else fails, just shade skip.",
    "If it takes more than 5 hours you should probably reset.",
    "You'll never find the Crystal Heart.",
    "It's impossible to softlock, just gitgud."]


def _randomizer_taunt(): return _taunt_list[randint(0, len(_taunt_list) - 1)]


_splr_lrt = f"""**Reminder**: Please avoid any discussion of content past the Forgotten Crossroads! Discuss details
in <#{cfg['ch']['help']}> or <#{cfg['ch']['discussion']}>"""

_sr_guides = "https://www.speedrun.com/hollowknight/guides"

_sr_resources = "https://www.speedrun.com/hollowknight/resources"

text = {
    "sr_guides": _sr_guides,
    "sr_resources": _sr_resources,
    "long_psa": _general_psa,
    "100": _hundred_guide,
    "mod_help": _modtext,
    "randomizer": _randomizer_taunt,
    "short_psa": _splr_lrt
}
