from qoid import *
import random


dir_logs = "data/log/"


class Config(object):

    def __init__(self):
        self.data = {}
        with open('data/config.cxr', 'r', encoding='utf-8') as f:
            self.data = Bill("Config", [x.strip("\n") for x in f.readlines()])

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self):
        return str(self.data)

    def save(self):
        self.data.save('data', echo=False)


class ImgChannel:

    def __init__(self, name: str, links: list, tagged: bool):
        self.q = Qoid(tag=name)
        if tagged:
            for e in links:
                sp = e.split(":", 1)
                self.q.add(Property(tag=sp[0], val=sp[1].strip()))
        else:
            for e in links:
                self.q.add(Property(tag=e))
        self.current = Qoid(tag=name, val=list(self.q.val))

    def __getitem__(self, item):
        out = self.q[item]
        if out is PROPERTY_ABSENT:
            print("Property Absent: {0}".format(item))
        return out

    def __len__(self):
        return len(self.q)

    def add(self, item):
        if isinstance(item, Property):
            self.q.add(item)
        elif isinstance(item, str):
            self.q.add(Property(tag=item, val=None))

    def get_qoid(self):
        return self.q

    def r(self):
        if len(self.current) == 0:
            self.current = Qoid(tag=self.q.tag, val=list(self.q.val))
        elif len(self.current) == 1:
            next_img = self.current.pop(0)
            return next_img
        selection = random.randint(0, len(self.current) - 1)
        next_img = self.current.pop(selection)
        return next_img

    def tag(self):
        return self.q.tag


class ImgServer:

    def __init__(self):
        self.channels = Qoid(tag="img")

    def add(self, ch: ImgChannel):
        self.channels.add(Property(tag=ch.tag(), val=ch))

    def add_to(self, ch: str, to_add):
        if isinstance(to_add, Property):
            self[ch].add(to_add)
        elif isinstance(to_add, str):
            self[ch].add(Property(tag=to_add, val=None))

    def __getitem__(self, tag: str):
        return self.channels.get(tag=tag)

    def __len__(self):
        return len(self.channels)


config = Config()

blacklist = []
with open("data/blacklist.zote", 'r+') as f:
    for each in f.readlines():
        blacklist.append(each.replace("\n", ""))