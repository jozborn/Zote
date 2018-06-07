"""

Some happy little helper methods to reduce code duplication in meme submissions
as well as on_reaction_add

"""

import os

import requests
from disco import embedify
from discord.ext.commands import Bot
from discord import Forbidden, NotFound


async def accept_and_log_meme(zote: Bot, img, msg, repo, reason):
    u = msg.embeds[0]["image"]["url"]
    if "imgur.com" in u:
        u.replace("imgur.com", "i.imgur.com")
        u += ".png"
    if "gfycat.com" in u:
        u.replace("gfycat.com", "thumbs.gfycat.com")
        u += "-size_restricted.gif"
    u_ext = u.rsplit('.', 1)[-1]
    img_data = requests.get(u).content
    with open(f"data/t-{msg.id}.{u_ext}", 'wb+') as img_file:
        img_file.write(img_data)
    ref = await zote.send_file(destination=repo, fp=f"data/t-{msg.id}.{u_ext}",
                               filename=f"{msg.id}.{u_ext}")
    await zote.send_message(destination=zote.log,
                            embed=embedify(u, reason))
    img.add_image(repo.name, ref.attachments[0]["url"])
    await zote.delete_message(msg)
    os.remove(f"data/t-{msg.id}.{u_ext}")


async def reject_and_log_meme(zote: Bot, msg, reason):
    u = msg.embeds[0]["image"]["url"]
    await zote.send_message(destination=zote.log, embed=embedify(u, f"Rejected: {reason}"))
    await zote.delete_message(msg)


async def add_reactions(zote: Bot, message, reactions, r):
    for e in r:
        try:
            await zote.add_reaction(message, reactions[e])
        except Forbidden:
            pass


async def submit_and_mark_meme(zote: Bot, a, desc, reactions):
    em = embedify(a["url"], desc)
    m = await zote.send_message(zote.submissions, embed=em)
    await zote.edit_message(m, new_content=f"{m.id}", embed=em)
    await add_reactions(zote, m, reactions, ["yes", "no"])


async def check_message(zote: Bot, message, cfg, reactions, blacklist):
    # raw_list = message.content.replace("_", ";").split(" ")
    raw_list = message.content.split(" ")
    raw_list[0] = raw_list[0].lower()
    raw = ' '.join(raw_list)
    message.content = raw
    await zote.process_commands(message)
    if message.channel.id == cfg["ch"]["message-changelog"] and message.author.name == "Dyno":
        if message.embeds[0]["author"]["name"] == "Hollow Knight":
            try:
                await zote.delete_message(message)
            except NotFound:
                pass
    if message.channel.id == cfg["ch"]["meme"]:
        try:
            for word in raw.split(" "):
                if "zote" in word or "<@297840101944459275>" in word:
                    await zote.add_reaction(message, reactions["zote"])
                if "dab" in word:
                    await zote.add_reaction(message, reactions["hollowdab"])
                if "whomst" in word:
                    await zote.add_reaction(message, reactions["hollowface"])
        except Forbidden:
            # When users do not permit reactions to be added
            pass
    if message.channel.id == cfg["ch"]["general"] or message.channel.id == cfg["ch"]["bots"]:
        bad_word = blacklist(message.content.lower())
        if bad_word:
            print(f"Deleted spoiler {bad_word} in $general")
            await zote.delete_message(message)
            try:
                await zote.send_message(
                    message.author,
                    f"{text['short_psa']}\n*(You received this message for saying the spoiler  \"{bad_word}\")*")
            except Forbidden:
                # When users do not permit messages to be sent
                pass
