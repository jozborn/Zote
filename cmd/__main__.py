from cfg import _zdn, cfg, inst, start
from zote import initialize_events
from commands import initialize_commands
from log import log_error_message
from inf import token

from time import time, sleep
from asyncio import get_event_loop, Task, gather

initialize_events(inst, cfg, _zdn)
initialize_commands(inst, cfg, _zdn)

fail_delay = 25
loop = get_event_loop()
while True:
    try:
        start(time())
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
