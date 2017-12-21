import json
import datetime
import time
from auxiliary import *

_frame = [e.tag for e in hk_qoid["cfg frame"]]


class Config(object):

    def __init__(self):
        self.data = {}
        with open('data/config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in _frame:
                self.data[key] = data[key]

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        out = ""
        for each in self.data.keys():
            out += each + ": " + str(self.data.get(each)) + "\n"
        return out

    def save(self):
        with open('data/config.json', 'w') as f:
            json.dump(self.data, f, ensure_ascii=True, indent=4)


def read_from_data(file_name: str):
    out = []
    with open("data/" + file_name, "r") as f:
        for each in f.readlines():
            out.append(each.strip("\n"))
    return out


ENTRIES = read_from_data("en.zote")
WINNERS = read_from_data("win.zote")
WINNERS2 = read_from_data("win2.zote")


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


def win_contest(u_id: str):
    WINNERS.append(u_id)
    with open("data/win.zote", "a") as f:
        f.write(u_id + "\n")
        print(len(WINNERS), len(ENTRIES))
    return True


def win_contest2(u_id: str):
    WINNERS2.append(u_id)
    with open("data/win2.zote", "a") as f:
        f.write(u_id + "\n")
    print(len(WINNERS2), len(ENTRIES))
    return True
