from disco import embedify
from qoid import Property, Qoid
from random import randint


class ImgChannel:

    @staticmethod
    def open(ch: str, tagged=False):
        with open(f"img/{ch}.cxr", "r") as img_file:
            o = []
            for e in img_file.readlines():
                o.append(e.replace("\n", ""))
        return ImgChannel(name=ch, links=o, tagged=tagged)

    def __init__(self, name: str, links: list, tagged: bool):
        self.name = name
        self.tagged = tagged
        self.q = Qoid(tag=name)
        if tagged:
            for e in links:
                sp = e.split(":", 1)
                self.q.append(Property(tag=sp[0], val=embedify(url=sp[1].strip(), desc=None)))
        else:
            for e in links:
                self.q.append(Property(tag=e, val=embedify(url=e, desc=None)))
        self.current = Qoid(tag=name, val=list(self.q.val))

    def __getitem__(self, item):
        return self.q[item]

    def __len__(self):
        return len(self.q)

    def add(self, item):
        if isinstance(item, (Property, str)):
            to_add = item if isinstance(item, Property) else Property(tag=item, val=embedify(url=item, desc=None))
            self.q.append(to_add)
            self.current.append(to_add)
            with open(f"img/{self.name}.cxr", "a") as f:
                f.write(str(to_add))
                f.write("\n")

    def remove(self, item):
        out = self.q.remove(item)
        with open(f"img/{self.name}.cxr", "w") as f:
            for e in self.q:
                f.write(f"{e}\n")
        return out

    def get_qoid(self):
        return self.q

    def r(self):
        if len(self.current) == 0:
            self.current = Qoid(tag=self.q.tag, val=list(self.q.val))
        elif len(self.current) == 1:
            next_img = self.current.pop(0)
            return next_img
        selection = randint(0, len(self.current) - 1)
        next_img = self.current.pop(selection)
        return next_img.val

    def tag(self):
        return self.q.tag


class ImgServer:

    def __init__(self):
        self.ready = False
        self.channels = Qoid(tag="img")

    def __getitem__(self, q):
        if isinstance(q, str):
            return self.channels.get(q).val
        elif isinstance(q, tuple):
            image = q[1].replace(" ", "_")
            return self.channels.get(q[0])[image]

    def __len__(self):
        return len(self.channels)

    def add(self, ch: str, tagged: bool):
        self.channels.append(Property(tag=ch, val=ImgChannel.open(ch, tagged=tagged)))

    def add_to(self, ch: str, to_add):
        if isinstance(to_add, Property):
            self[ch].add(to_add)
        elif isinstance(to_add, str):
            self[ch].add(Property(tag=to_add, val=None))
