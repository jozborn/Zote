import json
import datetime
import time

ENTRIES = []
WINNERS = []
# config = {}


def load():
    _frame = [
        "n",
        "general",
        "ref",
        "meme",
        "supermeme",
        "speedrunning",
        "hollowmas",
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


def save(cfg: str):
    with open('data/config.json', 'w') as f:
        json.dump(cfg, f, ensure_ascii=True, indent=4)


def add_report(report: str, n: int=0):
    try:
        with open('data/reports/{0}.zote'.format(n), 'a+') as f:
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
        with open('data/log/cmd.zote', 'a') as f:
            f.write(s)
            f.write("\n")
    except UnicodeEncodeError as e:
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def enter_contest(u_id: str):
    try:
        if u_id not in ENTRIES:
            ENTRIES.append(u_id)
            with open("data/en.zote", "a") as f:
                f.write(u_id + "\n")
            return "added"
        else:
            return "already"
    except Exception as e:
        return "error"


def save_entries():
    with open("data/en.zote", "w") as f:
        for each in ENTRIES:
            f.write(each + "\n")


def win_contest(u_id: str):
    WINNERS.append(u_id)
    with open("data/win.zote", "a") as f:
        f.write(u_id + "\n")
    save_entries()
    return True
