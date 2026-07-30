import screen_layout as layout  
import func as f
import time as t
import config
import random
import drop_analyzer
import coords #  para remover cuando quite el escalado


def Slot(n):  # tap on slot n
    xccord = 225-150
    for x in range(0,n):
        xccord += 150
    f.tap_scale(xccord, 925)


def BB():
    print(">>> entro en BB <<<")
    f.log("[BB] Iniciando ataque BB()")
    f.swipe2()
    f.log("[BB] Slot 1")
    Slot(1)
    f.log("[BB] Tap inicial")
    f.tap_scale(1535,585)
    t.sleep(0.5)

    f.log("[BB] Slot 2")
    Slot(2)
    for x in range(6):
        f.log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
        f.tap_scale(1535, 585)
        t.sleep(0.5)  # mio... quitar

    for x in range(2,8):
        f.log(f"[BB] Seleccionando slot {x}")
        Slot(x)

        for x in range(6):
            f.log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
            f.tap_scale(1535, 585)
            t.sleep(0.5)  # mio... quitar

def BB2():
    f.log("[BB2] Iniciando ataque BB()")
    f.swipe2()
    Slot(1)
    f.tap_scale(1535, 585)
    Slot(9)
    for x in range(8):
        f.tap_scale(1535, 585)
    for x in range(2,10):
        Slot(x)


def BBFarm():
    print(">>> entro en BBFarm <<<")
    f.log("Iniciando ataque BBF()", category="BB Farm")
    f.swipe2()
    f.log("Slot 1", category="BB Farm")
    Slot(1)
    f.log("Tap inicial", category="BB Farm")
    tropas = random.randint(1, 4)
    f.log(f"Soltando {tropas} tropa(s)", category="BB Farm")

    absolute_x, absolute_y = f.human_tap_scale(*layout.DROP_AREA)
    scaled_x, scaled_y = coords.scale(absolute_x, absolute_y)


    t.sleep(0.35)

    if config.DROP_ANALYZER:
        screenshot = f.screenshot("DropAnalyzer")

        drop_analyzer.analyze_drop(
            screenshot,
            scaled_x,
            scaled_y
        )

    if tropas > 1:
        f.log("Cambiando a slot 2 para el resto", category="BB Farm")
        Slot(2)

    for _ in range(tropas - 1):
        f.human_tap_scale(*layout.DROP_AREA)
        t.sleep(0.35)

#    f.tap(1535,585,p)

    t.sleep(0.5)
