"""TH bot command-line entry point."""

import botstate

from TH_Bot import th_strategies
from TH_Bot.gameflow_th import th_game_flow


def menu():
    """Run the TH command-line menu."""
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
            return False
        elif choice == "0":
            if th_strategies.TH_SLOT_1_CENTER is None or th_strategies.TH_SLOT_2_CENTER is None:
                print("Falta calibrar el centro del Slot 1 y del Slot 2.")
                continue
            return True
        else:
            print("Opción no válida")


if __name__ == "__main__":
    th_strategies.initialize()
    if menu():
        botstate.start()
        th_game_flow(th_strategies.build_context())
