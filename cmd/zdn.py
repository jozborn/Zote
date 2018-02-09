from qoid import *
import random


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
        self.current = Qoid(tag=name, val=self.q.val)

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
        selection = random.randint(0, len(self.current) - 1)
        next_img = self.current.pop(selection)
        if len(self.current) == 0:
            self.current = Qoid(tag=self.q.tag, val=self.q.val)
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
