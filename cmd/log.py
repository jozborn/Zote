import datetime
from urllib import request
from time import time
from os import path, mkdir

_dir_logs = "data/log/"
if not path.exists(_dir_logs):
    mkdir(_dir_logs)


def log_command_usage(name, ctx):
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
        time_formatted = datetime.datetime.fromtimestamp(time()).strftime('%H:%M:%S')
        s = f"{time_formatted} {u_name}, {name}, {server}({s_id})-#{ch_name}"
        print(s)
        with open('data/log/cmd.zote', 'a') as f:
            f.write(s)
            f.write("\n")
    except UnicodeEncodeError:
        print("ERROR CODE 420. Unable to log command due to super dank name.")


def log_error_message(f_name, exc):
    with open(_dir_logs + "error.zote", "a") as file:
        file.write(f"{f_name}: {str(type(exc))} + : + {str(exc)} + \n")
    print(">>>>>", type(exc), str(exc))


wiki_str = "http://hollowknight.wikia.com/wiki/"
base = wiki_str + "Special:Search"
search = base + "?query="
no_results = base.encode()


def wiki_search(query):
    try:
        query = query.replace(" ", "+")
        page = request.urlopen(f"{search}{query}").readlines()
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
