import time
print(f">>> screen_utils.py  starting [{time.perf_counter():.3f}]")

import time as t
import cv2
import numpy as np

from adb_utils import screenshot, swipe
from logger import log


def wait_for_stable_screen(timeout=5):
    start = t.time()
    last = screenshot("stable_check")

    while t.time() - start < timeout:
        t.sleep(0.3)
        current = screenshot("stable_check2")

        img1 = cv2.imread(last)
        img2 = cv2.imread(current)

        if img1 is None or img2 is None:
            last = current
            continue

        diff = cv2.absdiff(img1, img2)
        nonzero = np.count_nonzero(diff)

        if nonzero < 500:  # pantalla estable
            return current  # DEVUELVE LA CAPTURA ESTABLE

        last = current

    return last  # aunque no esté perfecta, devolvemos la última

def stable_swipe(x1, y1, x2, y2, duration=500):
    log("[STABLE SWIPE] esperando pantalla estable...")
    before = wait_for_stable_screen()  # solo 1 captura

    swipe(x1, y1, x2, y2, duration)
    t.sleep(0.5)

    after = screenshot("after_swipe")  # solo 1 captura

    img1 = cv2.imread(before)
    img2 = cv2.imread(after)

    diff = cv2.absdiff(img1, img2)
    nonzero = np.count_nonzero(diff)

    if nonzero < 500:
        log("[STABLE SWIPE] swipe NO ejecutado, reintentando...")
        t.sleep(0.5)
        swipe(x1, y1, x2, y2, duration)
    else:
        log("[STABLE SWIPE] swipe ejecutado correctamente")