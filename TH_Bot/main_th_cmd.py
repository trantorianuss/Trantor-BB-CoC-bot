"""TH bot command-line entry point and calibration menu."""

import botstate
import coords
import func as f

from TH_Bot import th_strategies
from TH_Bot.gameflow_th import th_game_flow


def menu():
    """Run the command-line calibration menu and return whether to start the bot."""
    while True:
        print()
        print("1. Marcar zona de despliegue EDGE")
        print("2. Marcar centro del Slot 1 y centro del Slot 2")
        print("X. Exit")
        print("0. Ejecutar")
        choice = input("> ").strip()
        if choice == "1":
            th_strategies.select_edge_zone()
        elif choice == "2":
            th_strategies.select_slot_centers()
        elif choice.lower() == "x":
            f.log("[TH] X. Exit -> saliendo del menú", color="yellow")
            return False
        elif choice == "0":
            if th_strategies.TH_SLOT_1_CENTER is None or th_strategies.TH_SLOT_2_CENTER is None:
                f.log("[TH] No se puede ejecutar: faltan los centros de los slots. Usa la opción 2.", color="yellow")
                continue
            return True
        else:
            print("Opción no válida")


if __name__ == "__main__":
    coords.initialize()
    th_strategies.load_attack_config()
    if menu():
        botstate.start()
        ctx = th_strategies.build_context()
        th_game_flow(ctx)
