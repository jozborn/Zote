from disco import embedify
from qoid import Property, Qoid, Index
from random import randint
import copy


class EmbedIndex(Index):

    def __init__(self, source: str, path=None, mode=None):
        self.source = Index.open(source)
        super().__init__(tag="Images", val=copy.deepcopy(self.source.val), path=path, mode=mode)
        for ch in self:
            self.tagged = eval(ch[0])
            for k in range(1, len(ch)):
                p = ch.get(index=k)
                if self.tagged:
                    p.set(val=embedify(url="https://" + p.val))
                else:
                    p.set(val=embedify(url="https://" + p.tag))
        self.current = self.refresh()

    def refresh(self):
        out = Index(tag="Current Images", val=copy.deepcopy(self.val))
        for e in out:
            e.remove("tagged")
        return out

    def add_image(self, tag, this):
        to_add = Property(tag=this.replace("https://", ""), val=embedify(url=this))
        self[tag].append(to_add)
        self.current[tag].append(to_add)
        self.source[tag].append(Property(tag=to_add.tag))
        self.source.save(echo=False)

    def save_source(self, echo=False):
        self.source.save(echo)

    def r(self, tag):
        if len(self.current[tag]) == 0:
            self.current[tag] = Qoid(tag, copy.deepcopy(self[tag].val))
            self.current[tag].remove("tagged")
        elif len(self.current[tag]) == 1:
            next_img = self.current[tag].pop(0).val
            return next_img
        selection = randint(0, len(self.current[tag]) - 1)
        next_img = self.current[tag].pop(selection)
        return next_img.val

    def remove_image(self, tag, this):
        this = this.replace("https://", "")
        cnd = False
        if this in self[tag]:
            self[tag].remove(this)
            cnd = True
        if this in self.current[tag]:
            self.current[tag].remove(this)
            cnd = True
        if this in self.source[tag]:
            self.source[tag].remove(this)
            cnd = True
        if cnd:
            self.source.save(echo=False)
