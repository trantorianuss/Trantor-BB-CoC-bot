import cv2
import numpy as np
import time as t

import func as f


def save_debug_image(name, image, timestamp=True):

    if timestamp:
        ts = t.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{ts}.png"
    else:
        filename = f"screenshots/{name}.png"

    cv2.imwrite(filename, image)

    return filename

def find_drop_point():

    screenshot = f.screenshot("DropAnalyzer")

    img = cv2.imread(screenshot)

    if img is None:
        return None

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # -------------------------------------------------------
    # Máscara verde
    # -------------------------------------------------------

    lower_green = np.array([84, 80, 70])
    upper_green = np.array([92, 100, 95])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # -------------------------------------------------------
    # Buscar blobs
    # -------------------------------------------------------

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    # Blob más grande

    best = None
    best_idx = -1
    best_area = 0

    for i, contour in enumerate(contours):

        area = cv2.contourArea(contour)

        if area > best_area:

            best_area = area
            best = contour
            best_idx = i

    x, y, w, h = cv2.boundingRect(best)


    blob_mask = np.zeros((h, w), dtype=np.uint8)

    shifted = best.copy()
    shifted[:, :, 0] -= x
    shifted[:, :, 1] -= y

    cv2.drawContours(
        blob_mask,
        [shifted],
        -1,
        255,
        thickness=-1
    )

    # Dibujar agujeros

    if hierarchy is not None:

        hierarchy = hierarchy[0]

        idx = best_idx

        child = hierarchy[idx][2]

        while child != -1:

            hole = contours[child].copy()

            hole[:, :, 0] -= x
            hole[:, :, 1] -= y

            cv2.drawContours(
                blob_mask,
                [hole],
                -1,
                0,
                thickness=-1
            )

            child = hierarchy[child][0]

    # -------------------------------------------------------
    # Punto más seguro
    # -------------------------------------------------------

    save_debug_image("blob_mask", blob_mask)

    dist = cv2.distanceTransform(
        blob_mask,
        cv2.DIST_L2,
        5
    )

    _, _, _, maxLoc = cv2.minMaxLoc(dist)

    debug = cv2.cvtColor(blob_mask, cv2.COLOR_GRAY2BGR)

    cv2.circle(
        debug,
        maxLoc,
        6,
        (0, 0, 255),
        -1
    )

    save_debug_image("blob_distance", debug)

    best_x = x + maxLoc[0]
    best_y = y + maxLoc[1]

    best_x = x + w // 2
    best_y = y + h // 2

    print("BoundingRect:", x, y, w, h)
    print("MaxLoc:", maxLoc)
    print("Best:", best_x, best_y)

    # -------------------------------------------------------
    # Imagen de depuración
    # -------------------------------------------------------

    debug = img.copy()

    # Contorno exterior
    cv2.drawContours(
        debug,
        [best],
        -1,
        (0,255,0),
        2
    )

    # Agujeros

    if hierarchy is not None:

        child = hierarchy[idx][2]

        while child != -1:

            cv2.drawContours(
                debug,
                contours,
                child,
                (0,0,255),
                2
            )

            child = hierarchy[child][0]

    cv2.circle(
        debug,
        (best_x,best_y),
        8,
        (255,0,0),
        -1
    )

    save_debug_image("green_analysis", debug)

    return {
        "mask": blob_mask,
        "bbox": (x, y, w, h),
        "point": (best_x, best_y)
    }
