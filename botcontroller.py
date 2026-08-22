import threading
import time as t

import func as f
import attacks as a
import gameflow as gf
import botstate
import machine_state

Bbot_thread = None


def start_farm(attacks_per_cycle=None):
    global Bbot_thread
    if not botstate.should_run():
        botstate.start()
        Bbot_thread = threading.Thread(target=lambda: farm_loop(attacks_per_cycle), daemon=True)
        Bbot_thread.start()
        if attacks_per_cycle is None:
            f.log("Farm started with random attacks per cycle.")
        else:
            f.log(f"Farm started with {attacks_per_cycle} attacks per cycle.")


def stop():
    botstate.stop()
    f.log("Stopping bot...")


def farm_loop(attacks_per_cycle=None):
    while botstate.should_run():
        full = gf.farm_until_full(attacks_per_cycle)

        if full:
            f.log("Storage full. Stopping bot.")
            botstate.stop()
            break

    botstate.set_stopped()
    machine_state.set_state(machine_state.IDLE)

    f.log(">>>>>  Bot stopped.  <<<<<", color="red")
