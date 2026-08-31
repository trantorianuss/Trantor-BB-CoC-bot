import time
print(f">>> adb_utils.py  starting [{time.perf_counter():.3f}]")

import subprocess
import time as t
import cv2
import numpy as np
import random
import os
import math


import config
import coords
from logger import log


def adb(cmd_rest):
    """
    Ejecuta un comando ADB usando ADB_PATH y ADB_PORT del config.
    cmd_rest es la parte del comando que va después de 'shell'.
    Ejemplo: 'input tap 100 200'
    """
    full_cmd = f'{config.ADB_PATH} -s {config.ADB_PORT} shell {cmd_rest}'.strip()
    log(f" {full_cmd}", debug=True, category="adb")

    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        log(f"Error: {result.stderr.strip() or result.stdout.strip()}", debug=True, category="adb")
        return ""

    return result.stdout.strip()

def get_real_resolution():
    out = adb("wm size")
    if not out:
        raise RuntimeError("No se pudo obtener la resolución desde ADB")

    # Ejemplo de salida: "Physical size: 1920x1080"
    size_part = out.split(":")[-1].strip()
    w, h = map(int, size_part.split("x"))

    if w < h:
        w, h = h, w
        
    return w, h

def capture_screenshot():
    """
    Captures a screenshot from the emulator and returns it as an OpenCV image.

    Returns:
        numpy.ndarray: Screenshot in BGR format.
        None: If the capture fails.
    """

    t0 = t.perf_counter()

    cmd = [
        config.ADB_PATH,
        "-s", config.ADB_PORT,
        "exec-out", "screencap", "-p"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        check=True
    )

    image = cv2.imdecode(
        np.frombuffer(result.stdout, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )

    t1 = t.perf_counter()

    log(
        f"screenshot ADB : {(t1 - t0) * 1000:.1f} ms",
        debug=True,
        category="timing",
    )

    return image

def screenshot(
    name: str = None,
    tag: str = None,
    timestamp: bool = True,
    debug_level: int = 1,
):

    """
    Guarda un screenshot del emulador.

    Args:
        name: Nombre base del fichero.
        tag: Etiqueta opcional para añadir al nombre. (for backward compatibility)
        timestamp: Añadir timestamp al nombre.
        debug_level: Nivel de debug requerido (pendiente de implementar).
    """

    # TODO: cuando exista el sistema de niveles
    # if debug_level > config.DEBUG_LEVEL:
    #     return None


    if name is None:
        name = tag or "screen"

    # Crear carpeta si no existe
    os.makedirs("screenshots", exist_ok=True)

    # Construir nombre del fichero
    if timestamp:
        ts = t.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{ts}.png"
    else:
        filename = f"screenshots/{name}.png"


    # Nombre con timestamp
    timestamp = t.strftime("%Y%m%d_%H%M%S")


    # Captura directa del emulador
    t0 = t.perf_counter()
    
    cmd = [
        config.ADB_PATH,
        "-s", config.ADB_PORT,
        "exec-out", "screencap", "-p"
    ]

    with open(filename, "wb") as f_out:
        subprocess.run(cmd, stdout=f_out)

    t1 = t.perf_counter()
    
    log(f"screenshot ADB : {(t1-t0)*1000:.1f} ms", debug=True, category="timing")

    return filename


def tap_scale(x, y, *_args):
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x, y = coords.scale(x, y)

    log(f"[TAP SCALE] x={x}, y={y}", debug=True, category="flow")
    adb(f"input tap {x} {y}")


def tap_absolute(x, y, *_args):
    log(f"[TAP ABSOLUTE] x={x}, y={y}", debug=True, category="flow")
    adb(f"input tap {x} {y}")

def human_tap_scale(x1, y1, x2, y2):
    # Elegir el punto ANTES de escalar
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)

    # Guardar las coordenadas absolutas para devolverlas
    # absolutas -> las del sistema de coordenadas inicial
    absolute_x = x
    absolute_y = y

    # Escalar sólo para el tap
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x, y = coords.scale(x, y)

    log(f"[HUMAN TAP SCALE] x={x}, y={y}", debug=True)
    adb(f"input tap {x} {y}")

    return absolute_x, absolute_y



def human_tap_absolute(x1, y1, x2, y2):
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    log(f"[HUMAN TAP ABSOLUTE] x={x}, y={y}", debug=True)
    adb(f"input tap {x} {y}")

def human_tap_area(area):
    """
    area:
        {
            "mask": ...,
            "point": (x,y)
            "radius": r
        }
    """

    mask = area["mask"]
    cx, cy = area["point"]
    radius = area["radius"]

    for _ in range(100):

        angle = random.uniform(0, 2 * math.pi)

        r = random.uniform(0, radius)

        x = int(cx + math.cos(angle) * r)
        y = int(cy + math.sin(angle) * r)

        # Fuera de la imagen
        if x < 0 or y < 0:
            continue

        if x >= mask.shape[1] or y >= mask.shape[0]:
            continue

        # Debe caer dentro del blob
        if mask[y, x] == 0:
            continue

        tap_absolute(x, y)

        return (x, y)

    # Si no encuentra ninguno, usar el mejor punto
    tap_absolute(cx, cy)

    return (cx, cy)

def swipe(x1, y1, x2, y2, duration_ms):
    """
    Swipe genérico usando ADB.
    x1, y1 = punto inicial
    x2, y2 = punto final
    duration_ms = duración en milisegundos
    """
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x1, y1 = coords.scale(x1, y1)
        x2, y2 = coords.scale(x2, y2)

    log(f"[SWIPE] x1={x1}, y1={y1}, x2={x2}, y2={y2}, dur={duration_ms}ms")
    adb(f"input touchscreen swipe {x1} {y1} {x2} {y2} {duration_ms}")


