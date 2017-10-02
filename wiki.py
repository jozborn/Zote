import urllib.request
from discord.ext.commands.errors import CommandInvokeError

search = "http://hollowknight.wikia.com/wiki/Special:Search?query="
no_results = "http://hollowknight.wikia.com/wiki/Special:Search".encode()
wiki_str = "http://hollowknight.wikia.com/wiki/"


def wiki_search(query):
    try:
        LOC = 12
        query = query.replace(" ", "+")
        page = urllib.request.urlopen("{0}{1}".format(search, query)).readlines()
        t = wiki_str.encode()
        links = list([])
        for each in page:
            if t in each:
                links.append(each)
                # print(each)
        if no_results in links[LOC]:
            return "None found"
        else:
            out = links[LOC].split('\"'.encode())[1]
            return out.decode('utf-8')
    except CommandInvokeError as e:
        return "None found"
