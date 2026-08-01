import os
import math
import time as t

import cv2
import numpy as np


SEARCH_RADIUS = 250
OFFSET = 40

import cv2
import time as t


def save_debug_image(name, image, timestamp=True):
    """
    Guarda una imagen de depuración en la carpeta screenshots.

    name      -> nombre base del fichero
    image     -> imagen OpenCV
    timestamp -> True/False
    """

    if timestamp:
        ts = t.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{ts}.png"
    else:
        filename = f"screenshots/{name}.png"

    cv2.imwrite(filename, image)

    return filename

def analyze_drop(image_file, drop_x, drop_y):

    img = cv2.imread(image_file)

    if img is None:
        print(f"No se pudo abrir {image_file}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ============================================================
    # DETECCIÓN DE ZONAS VERDES (PRUEBA)
    # ============================================================

    lower_green = np.array([84, 80, 70])
    upper_green = np.array([92, 100, 95])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Un poco de limpieza para unir pequeñas zonas
    kernel_green = np.ones((5, 5), np.uint8)

    green_mask = cv2.morphologyEx(
        green_mask,
        cv2.MORPH_CLOSE,
        kernel_green
    )

    save_debug_image("mask_green", green_mask)

    green_result = img.copy()
    green_result[green_mask > 0] = (0, 255, 0)
    save_debug_image("green_overlay", green_result)

    # ============================================================
    # DETECCIÓN DE linea roja (PRUEBA)
    # ============================================================



    lower_red1 = np.array([0, 60, 60])
    upper_red1 = np.array([15, 255, 255])

    lower_red2 = np.array([165, 60, 60])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = cv2.bitwise_or(mask1, mask2)

    # ============================================================
    # PRUEBA: RESTAR LA EROSIÓN
    # ============================================================

    kernel = np.ones((3, 3), np.uint8)

    eroded = cv2.erode(mask, kernel, iterations=1)

    thin = cv2.subtract(mask, eroded)


    #cv2.imwrite("screenshots/debug_eroded.png", eroded)
    #v2.imwrite("screenshots/debug_thin.png", thin)

    save_debug_image("mask", mask)
    save_debug_image("mask_eroded", eroded)
    save_debug_image("mask_thin", thin)
    #save_debug_image("mask_contours", result)

    # -----------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidate = None
    best_point = None
    best_dist = 999999999

    for contour in contours:

        for p in contour:

            px, py = p[0]

            if abs(px - drop_x) > SEARCH_RADIUS:
                continue

            if abs(py - drop_y) > SEARCH_RADIUS:
                continue

            d = (px - drop_x) ** 2 + (py - drop_y) ** 2

            if d < best_dist:

                best_dist = d
                best_point = (px, py)
                candidate = contour

    result = img.copy()

    cv2.rectangle(
        result,
        (drop_x - SEARCH_RADIUS, drop_y - SEARCH_RADIUS),
        (drop_x + SEARCH_RADIUS, drop_y + SEARCH_RADIUS),
        (255, 0, 0),
        2
    )

    cv2.circle(
        result,
        (drop_x, drop_y),
        8,
        (0, 0, 255),
        -1
    )

    if candidate is not None:

        cv2.drawContours(
            result,
            [candidate],
            -1,
            (0, 255, 0),
            2
        )

        cv2.circle(
            result,
            best_point,
            8,
            (255, 0, 0),
            -1
        )

        cv2.line(
            result,
            (drop_x, drop_y),
            best_point,
            (255, 255, 0),
            2
        )

        vx = drop_x - best_point[0]
        vy = drop_y - best_point[1]

        norm = math.hypot(vx, vy)

        if norm > 0:

            vx /= norm
            vy /= norm

            new_x = int(best_point[0] + vx * OFFSET)
            new_y = int(best_point[1] + vy * OFFSET)

            cv2.circle(
                result,
                (new_x, new_y),
                8,
                (0, 255, 255),
                -1
            )

    base = os.path.splitext(image_file)[0]

    cv2.imwrite(base + "_mask.png", mask)
    cv2.imwrite(base + "_analysis.png", result)

    