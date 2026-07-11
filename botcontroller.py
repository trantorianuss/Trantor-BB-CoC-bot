import threading
import time as t

import func as f
import attacks as a
import gameflow as gf
import botstate

Bbot_thread = None


def start_farm(attacks_per_cycle=2):
    global Bbot_thread
    if not botstate.is_running():
        botstate.start()
        Bbot_thread = threading.Thread(target=lambda: farm_loop(attacks_per_cycle), daemon=True)
        Bbot_thread.start()
        f.log(f"Farm started with {attacks_per_cycle} attacks per cycle.")


def stop():
    botstate.stop()
    f.log("Stopping bot...")


def farm_loop(attacks_per_cycle=2):
    while botstate.is_running():
        full = gf.farm_until_full(attacks_per_cycle)

        if full:
            f.log("Storage full. Stopping bot.")
            botstate.stop()
            break
