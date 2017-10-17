import urllib.request

from discord.ext.commands.errors import CommandInvokeError

from stuff import *

ch_general = "<#283467363729408000>"
ch_spoilers = "<#283680756159741953>"
ch_art = "<#301227786658381825>"
ch_meme = "<#297468195026239489>"
ch_help = "<#349116318865424384>"


def general_psa():
    s = "PSA: {0} is a spoiler-free channel.\n\n"
    s += "This means no discussions past Crossroads.\n\n"
    s += "If it requires progressing past Crossroads to unlock inside Crossroads, don't talk about it here.\n\n"
    s += "If you need help with a specific portion of the game, ask in {1} and someone will answer.\n\n"
    s += "If you wish to talk about the rest of the game or the lore or such, {2}\n\n"
    s += "If you've drawn something or would like to talk about the art, {3}.\n\n"
    return s.format(ch_general, ch_help, ch_spoilers, ch_art)


def improve():
    s = "If you are stuck on a boss or don't know where to go, you can ask for tips in {0} and {1}! "
    s += "Members of the server can offer tips on charms, upgrades, and strategies for "
    s += "any part of the game.\n\n For *spoiler-lite* help, see {0}.\n\n"
    s += "For spoiler-heavy details, see {1} (you have been warned!)"
    return s.format("#help", ch_spoilers)


def modtext():
    s = "**MOD-ONLY COMMANDS:**\n\n"
    s += "**ignore** [user id]: prevents the user from accessing Zote commands, or takes them off the ignore list.\n\n"
    s += "**ignorelist** shows all users being ignored and their ID.\n\n"
    s += "**silence** [#tag channel]: prevents Zote from responding to commands in a channel (or take it off that list)\n\n"
    s += "**clear** [x] or **clear** [@tag user] [x]: deletes X messages from a channel (or a user in that channel)\n\n"
    s += "**clearzotes** [optional amount x]: deletes all _commands and posts from Zote, or the X most recent ones\n\n"
    s += "**helpchannel**: clears all messages in the help channel and reposts the opening help message.\n\n"
    s += "**ban**: reaction image of the False Knight's Banhammer (not an actual ban!)\n\n"
    return s.format(pre)


def helptext():
    help_text = "**Come one, come all! Come ask your game progression related questions here without fear of unnecessary or unrelated spoilers!**\n\n"
    help_text += "The channel is cleared every so often or upon request to further reduce any chance of unwanted spoilers. Tag @ Mods if the channel needs to be cleared.\n\n"
    help_text += "If you're interested in spoiler-free information about the final boss/ending or the Hidden Dreams update, check the Google Drive link in the channel description.\n\n"
    help_text += "If you just need more information about a particular enemy, boss, or charm, Zote has a built-in wiki search command. For example, try:\n\n"
    help_text += "_wiki Dirtmouth"
    return help_text


def enemy_name(*args):
    if len(args[0]) == 0:
        return "Zote"
    r = args[0][0].capitalize()
    for each in args[0][1:]:
        r = "{0} {1}".format(r, each.capitalize())
    return "{0}{1}.png".format(dir_hj, r)

search = "http://hollowknight.wikia.com/wiki/Special:Search?query="
no_results = "http://hollowknight.wikia.com/wiki/Special:Search".encode()
wiki_str = "http://hollowknight.wikia.com/wiki/"


def wiki_search(query):
    try:
        loc = 12
        query = query.replace(" ", "+")
        page = urllib.request.urlopen("{0}{1}".format(search, query)).readlines()
        t = wiki_str.encode()
        links = list([])
        for each in page:
            if t in each:
                links.append(each)
                # print(each)
        if no_results in links[loc]:
            return "None found"
        else:
            out = links[loc].split('\"'.encode())[1]
            return out.decode('utf-8')
    except CommandInvokeError as e:
        return "None found"
