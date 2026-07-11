import func as f
import time as t
import config
import random


def Slot(n):  # tap on slot n
    xccord = 225-150
    for x in range(0,n):
        xccord += 150
    f.tap(xccord, 925)


def BB():
    print(">>> entro en BB <<<")
    f.log("[BB] Iniciando ataque BB()")
    f.swipe2()
    f.log("[BB] Slot 1")
    Slot(1)
    f.log("[BB] Tap inicial")
    f.tap(1535,585)
    t.sleep(0.5)

    f.log("[BB] Slot 2")
    Slot(2)
    for x in range(6):
        f.log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
        f.tap(1535,585,p)
        t.sleep(0.5)  # mio... quitar

    for x in range(2,8):
        f.log(f"[BB] Seleccionando slot {x}")
        Slot(x)

        for x in range(6):
            f.log(f"[BB] Soltando tropa {x+1}/6 en slot 2")
            f.tap(1535,585,p)
            t.sleep(0.5)  # mio... quitar

def BB2():
    f.log("[BB2] Iniciando ataque BB()")
    f.swipe2(p)
    Slot(1)
    f.tap(1535,585,p)
    Slot(9)
    for x in range(8):
        f.tap(1535,585,p)
    for x in range(2,10):
        Slot(x)


def BBFarm():
    print(">>> entro en BBFarm <<<")
    f.log("[BBF] Iniciando ataque BBF()")
    f.swipe2()
    f.log("[BBF] Slot 1")
    Slot(1)
    f.log("[BBF] Tap inicial")
    tropas = random.randint(1, 4)
    f.log(f"[BBF] Soltando {tropas} tropa(s)")

    f.human_tap(1400, 500, 1600, 700)
    t.sleep(0.35)

    if tropas > 1:
        f.log("[BBF] Cambiando a slot 2 para el resto")
        Slot(2)

    for _ in range(tropas - 1):
        f.human_tap(1400, 500, 1600, 700)
        t.sleep(0.35)

#    f.tap(1535,585,p)

    t.sleep(0.5)
