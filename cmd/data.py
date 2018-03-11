import datetime
import urllib.request
from zdn import config
import time
import random


def log(name, ctx):
    try:
        u_name = ctx.message.author.name
        if ctx.message.server:
            server = ctx.message.server.name
            s_id = ctx.message.server.id
        else:
            server = "DM"
            s_id = ctx.message.author.id
        if ctx.message.channel:
            ch_name = ctx.message.channel.name
        else:
            ch_name = f"{ctx.message.author.name}"
        time_formatted = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
        s = f"{time_formatted} {u_name}, {name}, {server}({s_id})-#{ch_name}"
        print(s)
        with open('data/log/cmd.zote', 'a') as f:
            f.write(s)
            f.write("\n")
    except UnicodeEncodeError:
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def submit(name, id, meme):
    with open('data/memes.zote', 'a') as f:
        f.write(f"{meme}\n")
    print(f"Meme submitted by {name}({id}) at {meme}")


wiki_str = "http://hollowknight.wikia.com/wiki/"
base = wiki_str + "Special:Search"
search = base + "?query="
no_results = base.encode()


def wiki_search(query):
    try:
        query = query.replace(" ", "+")
        page = urllib.request.urlopen(f"{search}{query}").readlines()
        flag = "class=\"result-link\"".encode()
        # print(page)
        for line in page:
            if flag in line:
                # print(line)
                out = line.split('\"'.encode())
                return out[1].decode("utf-8")
        return "None found"
    except Exception:
        return "None found"


def general_psa():
    s = f"PSA: <#{config['ch']['general']}> is a spoiler-free channel.\n\n"
    s += "This means no discussions past Crossroads.\n\n"
    s += "If it requires progressing past Crossroads to unlock inside Crossroads, don't talk about it here.\n\n"
    s += f"If you need help with a specific portion of the game, ask in <#{config['ch']['help']}> and someone will answer.\n\n"
    s += f"If you wish to talk about the rest of the game or the lore or such, <#{config['ch']['discussion']}>\n\n"
    s += f"If you've drawn something or would like to talk about the art, <#{config['ch']['art']}>.\n\n"
    return s


def splr_lrt():
    s = "**Reminder**: Please avoid any discussion of content past the Forgotten Crossroads! Discuss details"
    s += f" in <#{config['ch']['help']}> or <#{config['ch']['discussion']}>"
    return s


def modtext():
    s = "**MOD-ONLY COMMANDS:**\n\n"
    s += "**ignore** [user id]: prevents the user from accessing Zote commands, or takes them off the ignore list.\n\n"
    s += "**ignorelist** shows all users being ignored and their ID.\n\n"
    s += "**silence** [#tag channel]: stops/starts Zote responding to commands in a channel\n\n"
    s += "**clear** [x] or **clear** [@tag user] [x]: deletes X messages from a channel (or a user in that channel)\n\n"
    s += "**clearzotes** [optional amount x]: deletes all _commands and posts from Zote, or the X most recent ones\n\n"
    s += "**helpchannel**: clears all messages in the help channel and reposts the opening help message.\n\n"
    s += "**ban**: reaction image of the False Knight's Banhammer (not an actual ban!)\n\n"
    return s


def randomizer_taunt():
    possible = ["May you find Mantis Claw in King's Pass.",
                "If all else fails, just shade skip.",
                "If it takes more than 5 hours you should probably reset.",
                "You'll never find the Crystal Heart.",
                "It's impossible to softlock, just gitgud."
                ]
    return possible[random.randint(0, len(possible)-1)]
