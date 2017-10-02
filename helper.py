import json
import datetime
import time


pre = "_"
ch_general = "<#283467363729408000>"
ch_spoilers = "<#283680756159741953>"
ch_art = "<#301227786658381825>"
ch_meme = "<#297468195026239489>"
ch_bots = "<#283470827738103810>"


mods = ["127426811150860288", "151542934892707840", "210715103631245312", "135255524114563072", "142962897344004096"]

def load():
    _newframe = [
        "mods",
        "user ignore list",
        "channel ignore list",
        "precept#",
        "numbers",
        "precepts"
    ]
    _frame = [
        "general",
        "meme",
        "safememe",
        "supermeme",
        "reference",
        "speedrunning",
        "modonly",
        "mods",
        "ignoreList",
        "precept#",
        "numbers",
        "precepts"
    ]
    out = {}

    with open('config.json', 'r') as f:
        data = json.load(f)
        for key in _frame:
            out[key] = data[key]
    return out


def save():
    with open('config.json', 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def log(name, ctx):
    try:
        u_name = ctx.message.author.name
        ch_name = ctx.message.channel.name
        time_formatted = datetime.datetime.fromtimestamp(time.time()).strftime('%c')
        s = "{0}, {1}, #{2}, {3}".format(u_name, name, ch_name, time_formatted)
        print(s)
        with open('log.zote', 'a') as f:
            f.write(s)
            f.write("\n")
    except UnicodeEncodeError as e:
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def enemy_name(*args):
    if len(args[0]) == 0:
        return "Zote"
    r = args[0][0]
    for each in args[0][1:]:
        r = "{0} {1}".format(r, each.capitalize())
    return r


def general_psa():
    s = "PSA: **{0} is a spoiler-free channel.**\n\n"
    s += "If it happens after the Forgotten Crossroads, take it to another channel (like {1} or {2}).\n\n"
    return s.format(ch_general, "#help", ch_spoilers, ch_art)


def improve():
    s = "If you are stuck on a boss or don't know where to go, you can ask for tips in {0} and {1}! "
    s += "Members of the server can offer tips on charms, upgrades, and strategies for "
    s += "any part of the game.\n\n For *spoiler-lite* help, see {0}.\n\n"
    s += "For spoiler-heavy details, see {1} (you have been warned!)"
    return s.format("#help", ch_spoilers)


def modtext():
    s = "**MOD-ONLY COMMANDS:**\n\n"
    s += "**ignore** / **unignore** [user id]: prevents the user from accessing Zote commands.\n"
    s += "It can be used with multiple IDs eg {0}ignore [id1] [id2] [id3] ...\n\n"
    s += "**ignorelist** shows all users being ignored and their ID.\n\n"
    s += "**nomemes** and **yesmemes** will cause zote to ignore all meme category requests.\n\n"
    s += "**listen** [y/n] toggles Zote ignoring all commands except for mod-only ones.\n\n"
    s += "**generalmute** [y/n] toggles Zote ignoring memes in general"
    s += "**stop** shuts down Zote so he must be restarted manually."
    return s.format(pre)

def helptext():
    help_text = "**Come one, come all! Come ask your game progression related questions here without fear of unnecessary or unrelated spoilers!**\n\n"
    help_text += "The channel is cleared every so often or upon request to further reduce any chance of unwanted spoilers. Tag @ Mods if the channel needs to be cleared.\n\n"
    help_text += "If you're interested in spoiler-free information about the final boss/ending or the Hidden Dreams update, check the Google Drive link in the channel description.\n\n"
    help_text += "If you just need more information about a particular enemy, boss, or charm, Zote has a built-in wiki search command. For example, try:\n\n"
    help_text += "_wiki Dirtmouth"
    return help_text

config = load()
