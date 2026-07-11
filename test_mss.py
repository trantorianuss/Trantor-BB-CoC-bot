import time
import cv2
import numpy as np
import mss

with mss.mss() as sct:

    # Pantalla principal
    monitor = sct.monitors[1]

    t0 = time.perf_counter()

    img = np.array(sct.grab(monitor))

    t1 = time.perf_counter()

    print(f"Captura: {(t1-t0)*1000:.1f} ms")

    # MSS devuelve BGRA
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    cv2.imwrite("captura.png", img)

    