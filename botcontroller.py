import threading
import time as t

import func as f
import attacks as a
import gameflow as gf
import botstate
import machine_state
import settings

from TH_Bot import gameflow_th as gf_th
from TH_Bot import th_strategies


Bbot_thread = None


def start_farm(attacks_per_cycle=None):
    global Bbot_thread

    if not botstate.should_run():
        botstate.start()

        if settings.get_bot_type() == "TH":
            target = lambda: farm_loop_th()
        else:
            target = lambda: farm_loop(attacks_per_cycle)

        Bbot_thread = threading.Thread(target=target, daemon=True)
        Bbot_thread.start()

        if settings.get_bot_type() == "TH":
            f.log("TH Farm started.")
        elif attacks_per_cycle is None:
            f.log("BB Farm started with random attacks per cycle.")
        else:
            f.log(f"BB Farm started with {attacks_per_cycle} attacks per cycle.")


def stop():
    botstate.stop()
    f.log("Stopping bot...")


def farm_loop(attacks_per_cycle=None):
    gf.farm_until_full(attacks_per_cycle)

    botstate.set_stopped()
    machine_state.set_state(machine_state.IDLE)

    f.log(">>>>>  Bot stopped.  <<<<<", color="red", telegram=True)


def farm_loop_th():
    ctx = th_strategies.build_context()
    gf_th.th_game_flow(ctx)

    botstate.set_stopped()
    machine_state.set_state(machine_state.IDLE)

    f.log(">>>>>  Bot stopped.  <<<<<", color="red")