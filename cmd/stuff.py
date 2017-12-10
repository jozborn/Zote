import os
import random
import discord

pre = "_"
except_message = "Bah! There is no such thing!"
hk_server = "283467363729408000"


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

##################
# REACTIONS INIT #
##################

heart = "❤"
bee = "🐝"
zote_emoji = discord.Emoji(
    require_colons="True",
    managed=False,
    id="371947495330414595",
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
    name="happygrub",
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
dabright = discord.Emoji(
    require_colons="True",
    managed=False,
    id="320735637386821643",
    name="hollowdab",
    roles=[],
    server=hk_server
)
dableft = discord.Emoji(
    require_colons="True",
    managed=False,
    id="369966711648026624",
    name="hollowdabreverse",
    roles=[],
    server=hk_server
)
maggot = discord.Emoji(
    require_colons="True",
    managed=False,
    id="313428664576376832",
    name="maggot",
    roles=[],
    server=hk_server
)
cherry = discord.Emoji(
    require_colons="True",
    managed=False,
    id="284210478450868224",
    name="teamcherry",
    roles=[],
    server=hk_server
)


reactions = {}
reactions.update({
    "zote": zote_emoji,
    "aspid": aspid,
    "bee": bee,
    "grub": grub,
    "heart": heart,
    "dunq": dunq,
    "corny": corny,
    "dableft": dableft,
    "dabright": dabright,
    "maggot": maggot,
    "cherry": cherry})


##############
# MULTI INIT #
##############

dir_img = "img/"
dir_reaction = dir_img + "reaction/"
dir_hj = dir_img + "hj/"

dir_mistake = dir_img + "mistake"
mistakes = Multi(dir_mistake)

dir_goodgrubs = dir_img + "grublove"
goodgrubs = Multi(dir_goodgrubs)

dir_badgrubs = dir_img + "grubhate"
badgrubs = Multi(dir_badgrubs)

dir_memes = dir_img + "meme"
memes = Multi(dir_memes)

dir_grimm = dir_img + "grimm"
grimmfaces = Multi(dir_grimm)

dir_goodbees = dir_img + "beelove"
goodbees = Multi(dir_goodbees)

dir_badmaggots = dir_img + "maggothate"
badmaggots = Multi(dir_badmaggots)
