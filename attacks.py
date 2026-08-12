from shapely import area

import screen_layout as layout  
import func as f
import time as t
import config
import random
import drop_finder as df
from logger import log

#import coords #  para remover cuando quite el escalado


def Slot(n):  # tap on slot n
    x = layout.FIRST_SLOT_CENTER[0] + layout.SLOT_STEP * (n - 1)
    y = layout.FIRST_SLOT_CENTER[1]
    f.tap_scale(x, y)


def BB():
    print(">>> entro en BB <<<")
    log("[BB] Iniciando ataque BB()")
    f.swipe2()
    log("[BB] Slot 1")
    Slot(1)
    log("[BB] Tap inicial")
    f.tap_scale(*layout.DROP_POINT)
    t.sleep(0.5)

    log("[BB] Slot 2")
    Slot(2)
    for x in range(6):
        log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
        f.tap_scale(*layout.DROP_POINT)
        t.sleep(0.5)  # mio... quitar

    for x in range(2,8):
        log(f"[BB] Seleccionando slot {x}")
        Slot(x)

        for x in range(6):
            log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
            f.tap_scale(*layout.DROP_POINT)
            t.sleep(0.5)  # mio... quitar

def BB2():
    log("[BB2] Iniciando ataque BB()")
    f.swipe2()
    Slot(1)
    f.tap_scale(*layout.DROP_POINT)
    Slot(9)
    for x in range(8):
        f.tap_scale(*layout.DROP_POINT)
    for x in range(2,10):
        Slot(x)


def BBFarm():
    log("Iniciando ataque BBF()", category="BB Farm")
    f.swipe2()

    log("Buscando punto de drop", category="BB Farm")


    area = df.find_drop_point()

    if area is None:
        log("No se encontró zona de despliegue", color="red")
        return

    f.human_tap_area(area)

    log("Slot 1", category="BB Farm")
    Slot(1)
    log("Tap inicial", category="BB Farm")

    f.human_tap_area(area)
    t.sleep(0.35)

    tropas = random.randint(0, 4)
    log(f"Soltando {tropas} tropa(s) extra", category="BB Farm")

    if tropas > 0:
        log("Cambiando a slot 2 para el resto", category="BB Farm")
        Slot(2)

    for _ in range(tropas - 1):
        f.human_tap_area(area)
        t.sleep(0.35)

    t.sleep(0.5)