import os
import random
import discord


class Multi(object):

    def __init__(self, _dir: str):
        self._dir = _dir
        self.folder = [name for name in os.listdir(_dir) if os.path.isfile(os.path.join(_dir, name))]
        self.current = list(self.folder)

    def next(self):
        selection = random.randint(0, len(self.current) - 1)
        next_img = self.current.pop(selection)
        if len(self.current) == 0:
            self.current = list(self.folder)
        return "{0}/{1}".format(self._dir, next_img)

pre = "_"

except_message = "Bah! There is no such thing!"
dir_img = "img/"
dir_reaction = dir_img + "reaction"
dir_hj = dir_img + "hj/"

hk_server = "283467363729408000"

heart = "❤"
zote_head = discord.Emoji(
    require_colons="True",
    managed=False,
    id="321038028384632834",
    name="zote",
    roles=[],
    server=hk_server)
aspid = discord.Emoji(
    require_colons="True",
    managed=False,
    id="297708185899499522",
    name="primalaspid",
    roles=[],
    server=hk_server
)
grub = discord.Emoji(
    require_colons="True",
    managed=False,
    id="291831002874249216",
    name="grub",
    roles=[],
    server=hk_server
)
dunq = discord.Emoji(
    require_colons="True",
    managed=False,
    id="335555573481472000",
    name="dunq",
    roles=[],
    server=hk_server
)
corny = discord.Emoji(
    require_colons="True",
    managed=False,
    id="309365508682285057",
    name="corny",
    roles=[],
    server=hk_server
)

reactions = {}
reactions.update({"zote": zote_head, "yes": "", "aspid": aspid, "grub": grub, "heart": heart, "dunq": dunq, "corny": corny})


##############
# MULTI INIT #
##############

dir_mistake = dir_img + "mistake"
mistakes = Multi(dir_mistake)

dir_grubs = dir_img + "rare grubs"
grubs = Multi(dir_grubs)

dir_memes = dir_img + "meme"
memes = Multi(dir_memes)

dir_grimm = dir_img + "grimm"
grimmfaces = Multi(dir_grimm)
