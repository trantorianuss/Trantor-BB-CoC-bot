# coords.py
# -----------------------------------------
# Gestión de resoluciones, escalado
# -----------------------------------------

import time
print(f">>> coords.py  starting [{time.perf_counter():.3f}]")

from logger import log

# Resolución base (la que usaste para medir tus taps)
BASE_W = 1920
BASE_H = 1080

# Variables globales (se rellenan en init_resolution)
REAL_W = None
REAL_H = None
SX = 1.0
SY = 1.0


def init_resolution(real_w, real_h):
    """Inicializa la resolución real y calcula los factores de escalado."""
    global REAL_W, REAL_H, SX, SY

    REAL_W = real_w
    REAL_H = real_h

    SX = REAL_W / BASE_W
    SY = REAL_H / BASE_H

    log(f"[coords] Real resolution: {REAL_W}x{REAL_H}", category="coords")
    log(f"[coords] Scale SX={SX:.3f}, SY={SY:.3f}", category="coords")


def initialize():
    """Obtiene la resolución real del emulador e inicializa el escalado."""
    log("[coords] Initializing resolution...", category="coords")

    # Import local para evitar el ciclo: adb_utils importa coords.
    from adb_utils import get_real_resolution

    try:
        real_w, real_h = get_real_resolution()
        init_resolution(real_w, real_h)
        log(f"[coords] Resolution initialized: {real_w}x{real_h}", category="coords")
    except Exception as exc:
        log(f"[coords] Could not obtain actual resolution: {exc}", category="coords")
        init_resolution(BASE_W, BASE_H)
        log(f"[coords] Using default resolution: {BASE_W}x{BASE_H}", category="coords")


def scale(x, y):
    """Devuelve las coordenadas escaladas según SX/SY."""
    return int(x * SX), int(y * SY)


# -----------------------------------------
# TAPS DEFINIDOS (siempre en resolución base)
# -----------------------------------------

# Ejemplos (pon aquí todos tus taps)
# TAP_ATTACK = (1700, 900)
# TAP_OPEN_TROOPS = (1500, 300)
# TAP_COLLECT = (300, 850)

# Puedes añadir todos los que quieras:
# TAP_BUILDER = (x, y)
# TAP_TRAIN = (x, y)
# TAP_END_BATTLE = (x, y)
# TAP_SURRENDER = (x, y)
# TAP_ZOOM_OUT = (x, y)
# TAP_ZOOM_IN = (x, y)

# -----------------------------------------
# Funciones auxiliares para taps
# -----------------------------------------

def get_tap_scaled(tap_tuple):
    """Recibe un tap definido como (x, y) y devuelve el tap escalado."""
    x, y = tap_tuple
    return scale(x, y)
