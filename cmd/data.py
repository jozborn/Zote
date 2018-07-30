"""
Just anything that needs to be placed
"""
import datetime
from random import randint
from urllib import request
from time import time
from os import path, mkdir

import sys

_dir_logs = "data/log/"
if not path.exists(_dir_logs):
    mkdir(_dir_logs)


def log_message(name, ctx):
    # logs metadata on messages across all servers in which it is present
    pass


def log_command_usage(name, ctx):
    try:
        u_name = ctx.message.author.name
        u_id = ctx.message.author.id
        if ctx.message.server:
            server = ctx.message.server.name
            s_id = ctx.message.server.id
        else:
            server = "DM"
            s_id = ctx.message.author.id
        if ctx.message.channel:
            ch_name = ctx.message.channel.name
            ch_id = ctx.message.channel.id
        else:
            ch_name = f"{ctx.message.author.name}"
            ch_id = "0"
        dayf = datetime.datetime.fromtimestamp(time()).strftime('%m/%d')
        timef = datetime.datetime.fromtimestamp(time()).strftime('%H:%M:%S')
        print_log = f"{dayf} {timef}  {u_name}, {name}, {server}-#{ch_name}"
        s = f"{dayf},{timef},{u_id},{name},{s_id},{ch_id}"
        print(print_log)
        with open('data/log/cmd.zote', 'a') as cmd_log:
            cmd_log.write(s)
            cmd_log.write("\n")
    except UnicodeEncodeError:
        s = f"{timef} DANKNAME420, {name}, {server}({s_id})-#{ch_name}"
        with open('data/log/cmd.zote', 'a') as cmd_log:
            cmd_log.write(s)
            cmd_log.write("\n")
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def log_error_message(f_name, exc):
    exc_type, exc_obj, exc_tb = sys.exc_info()[:3]
    with open(_dir_logs + "error.zote", "a") as file:
        file.write(f"{f_name}: {str(type(exc))} : {str(exc)}\n")
    print(f"{f_name}: {type(exc)} {str(exc)}")


wiki_str = "http://hollowknight.wikia.com/wiki/"
base = wiki_str + "Special:Search"
search = base + "?query="
no_results = base.encode()


def wiki_search(query):
    try:
        query = query.replace(" ", "+")
        page = request.urlopen(f"{search}{query}").readlines()
        flag = "class=\"result-link\"".encode()
        for line in page:
            if flag in line:
                out = line.split('\"'.encode())
                return out[1].decode("utf-8")
        return "None found"
    except Exception:
        return "None found"


_blacklist = []
_blacklist_is_on = False
if _blacklist_is_on:
    with open("data/blacklist.zote", 'r+') as f:
        for each in f.readlines():
            _blacklist.append(each.replace("\n", ""))


def blacklist(s: str):
    if _blacklist_is_on:
        for b in _blacklist:
            if b in s.lower():
                return b
    return None


_general_psa = """PSA: <#283467363729408000> is a spoiler-free channel.\n
This means no discussions past Crossroads.\n
If it requires progressing past Crossroads to unlock inside Crossroads, don't talk about it here.\n
If you need help with a specific portion of the game, ask in <#349116318865424384> and someone will answer.\n
If you wish to talk about the rest of the game or the lore or such, <#283680756159741953>\n
If you've drawn something or would like to talk about the art, <#301227786658381825>."""
_completion_guide = "**107% guide**: http://hollowknight.wikia.com/wiki/Completion"
_modtext = """**MOD-ONLY COMMANDS:**\n
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


_splr_lrt = """**Reminder**: Please avoid any discussion of content past the Forgotten Crossroads! Discuss details
in <#349116318865424384> or <#283680756159741953>"""
_sr_guides = "https://www.speedrun.com/hollowknight/guides"
_sr_resources = "https://www.speedrun.com/hollowknight/resources"

_where_memes = "https://discord.gg/kqdCYZE"

_gng_not_announced = f"Gods and Glory will be released on August 23rd."

_invite_link = "<https://discordapp.com/api/oauth2/authorize?client_id=297840101944459275&permissions=346176&scope=bot>"

text = {
    "sr_guides": _sr_guides,
    "sr_resources": _sr_resources,
    "long_psa": _general_psa,
    "107": _completion_guide,
    "mod_help": _modtext,
    "randomizer": _randomizer_taunt,
    "short_psa": _splr_lrt,
    "where_memes": _where_memes,
    "gng_not_announced": _gng_not_announced,
    "invite_link": _invite_link
}
