import os
import random
import discord
import qoid

except_message = "Bah! There is no such thing!"

with open("data\server.cxr", "r") as f:
    s = [x.strip("\n") for x in f.readlines()]
    hk_qoid = qoid.Bill("server", s)

pre = hk_qoid["init"]["pre"]
hk_server = hk_qoid["init"]["server"]

img_root = "img/"
dir_logs = "data/log/"


class ImgFolder(object):

    def __init__(self, loc: str):
        self.dir = loc
        self.folder = [name for name in os.listdir(loc) if os.path.isfile(os.path.join(loc, name))]
        self.current = list(self.folder)

    def __getitem__(self, item):
        return "{0}/{1}".format(self.dir, item)

    def r(self):
        selection = random.randint(0, len(self.current) - 1)
        next_img = self.current.pop(selection)
        if len(self.current) == 0:
            self.current = list(self.folder)
        return "{0}/{1}".format(self.dir, next_img)


class ImgDir(object):

    def __init__(self, frame):
        self.all = {each: ImgFolder(img_root + each) for each in frame}

    def __getitem__(self, item):
        return self.all[item]

    def r(self, item):
        return self.all[item].r()


reactions = {}

for each in hk_qoid["hk emoji"]:
    d = discord.Emoji(
        require_colons=True, managed=False,
        name=each.tag, id=each.val,
        server=hk_server
    )
    reactions.update({each.tag: d})

for each in hk_qoid["discord emoji"]:
    reactions.update({each.tag: chr(int(each.val))})

multi_frame = [e.tag for e in hk_qoid["img folders"]]
img = ImgDir(multi_frame)
