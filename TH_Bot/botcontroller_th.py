import threading

from TH_Bot import gameflow_th as gf
from TH_Bot import th_strategies

import func as f

import botstate
import machine_state


Bbot_thread = None


def start_farm(strategy_name=th_strategies.DEFAULT_STRATEGY):
    global Bbot_thread
    if not botstate.should_run():
        botstate.start()
        Bbot_thread = threading.Thread(
            target=lambda: farm_loop(strategy_name),
            daemon=True,
        )
        Bbot_thread.start()
        f.log(f"Farm started with TH strategy: {strategy_name}.")


def farm_loop(strategy_name=th_strategies.DEFAULT_STRATEGY):
    ctx = th_strategies.build_context(strategy_name)
    gf.th_game_flow(ctx)

    botstate.set_stopped()
    machine_state.set_state(machine_state.IDLE)

    f.log(">>>>>  Bot stopped.  <<<<<", color="red")

def stop():
    botstate.stop()
    f.log("Stopping bot...")


