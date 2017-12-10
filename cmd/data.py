import json
import datetime
import time


def load():
    _frame = [
        "n",
        "general",
        "ref",
        "meme",
        "supermeme",
        "speedrunning",
        "mods",
        "ignored",
        "silenced",
        "precept#",
        "precepts"
    ]
    out = {}

    with open('data/config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for key in _frame:
            out[key] = data[key]
    return out

config = load()


def save():
    with open('data/config.json', 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def add_report(report: str, n: int=0):
    try:
        with open('data/reports{0}.txt'.format(n), 'a') as f:
            f.write(report)
            f.write("\n")
    except UnicodeEncodeError as e:
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def log(name, ctx):
    try:
        u_name = ctx.message.author.name
        ch_name = ctx.message.channel.name
        time_formatted = datetime.datetime.fromtimestamp(time.time()).strftime('%c')
        s = "{0}, {1}, #{2}, {3}".format(u_name, name, ch_name, time_formatted)
        print(s)
        with open('data/log.zote', 'a') as f:
            f.write(s)
            f.write("\n")
    except UnicodeEncodeError as e:
        print("ERROR CODE 420. Unable to log command due to super dank name.")
