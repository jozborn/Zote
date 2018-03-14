from qoid import Index
from bot import create_bot_instance
from data import log_error_message, blacklist, text
from inf import token
from img import ImgServer
from time import time, sleep
from asyncio import get_event_loop, Task, gather

print("""
 ##########################
 #                        #
 # Zote.discord by Conrad #
 #                        #
 # patreon.com/complexor  #
 #                        #
 ##########################
""")

cfg = Index.open("data/config.cxr")
zdn = ImgServer()

start = time()
_dat = {"img": zdn, "blacklist": blacklist, "text": text, "start": start}

inst = create_bot_instance(cfg, _dat)

fail_delay = 25
loop = get_event_loop()
while True:
    try:
        start = time()
        print("Initializing...")
        loop.run_until_complete(inst.start(token()))
    except Exception as exc:
        log_error_message("Event Loop", exc)
        pending = Task.all_tasks(loop=inst.loop)
        gathered = gather(*pending, loop=inst.loop)
        try:
            gathered.cancel()
            inst.loop.run_until_complete(gathered)
            gathered.exception()
        except Exception:  # This could be better
            pass
    print(f"Attempting restart in {fail_delay} seconds...")
    sleep(fail_delay)
