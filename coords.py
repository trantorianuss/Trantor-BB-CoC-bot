# coords.py
# -----------------------------------------
# Gestión de resoluciones, escalado y taps
# -----------------------------------------

import func as f

# Resolución base (la que usaste para medir tus taps)
BASE_W = 1920
BASE_H = 1080

# Variables globales (se rellenan en init_resolution)
REAL_W = None
REAL_H = None
SX = 1.0
SY = 1.0


def init_resolution(real_w, real_h):
    """
    Inicializa la resolución real del emulador y calcula SX/SY.
    Esta función se llama UNA sola vez desde main.py.
    """
    global REAL_W, REAL_H, SX, SY

    REAL_W = real_w
    REAL_H = real_h

    SX = REAL_W / BASE_W
    SY = REAL_H / BASE_H

    f.log(f"[coords] Resolución real: {REAL_W}x{REAL_H}")
    f.log(f"[coords] Escala SX={SX:.3f}, SY={SY:.3f}")


def scale(x, y):
    """
    Devuelve las coordenadas escaladas según SX/SY.
    """
    return int(x * SX), int(y * SY)


# -----------------------------------------
# TAPS DEFINIDOS (siempre en resolución base)
# -----------------------------------------

# Ejemplos (pon aquí todos tus taps)
#TAP_ATTACK = (1700, 900)
#TAP_OPEN_TROOPS = (1500, 300)
#TAP_COLLECT = (300, 850)

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
    """
    Recibe un tap definido como (x, y) y devuelve el tap escalado.
    """
    x, y = tap_tuple
    return scale(x, y)
