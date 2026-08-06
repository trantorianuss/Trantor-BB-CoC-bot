import cv2
import numpy as np
import time as t

import func as f
import config


def find_drop_point():

    img = f.capture_screenshot()

    if img is None:
        return None

    if config.DROP_ANALYZER_DEBUG >= 3:
        f.save_image("DropAnalyzer", img)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # -------------------------------------------------------
    # Máscara verde
    # -------------------------------------------------------

    lower_green = np.array([84, 80, 70])
    upper_green = np.array([92, 100, 140])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    if config.DROP_ANALYZER_DEBUG >= 2:
        f.save_image("mask_green", mask)

    # -------------------------------------------------------
    # Componentes conectadas (blobs)
    # -------------------------------------------------------

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    if num_labels <= 1:
        return None

    best_label = -1
    best_area = 0

    for label in range(1, num_labels):

        area = stats[label, cv2.CC_STAT_AREA]

        if area > best_area:

            best_area = area
            best_label = label

    blob_mask = np.zeros_like(mask)

    blob_mask[labels == best_label] = 255

    # para obtener el bounding box del blob, por ahora solo por si acaso
    ys, xs = np.where(blob_mask > 0)

    x = np.min(xs)
    y = np.min(ys)
    w = np.max(xs) - x + 1
    h = np.max(ys) - y + 1

    if config.DROP_ANALYZER_DEBUG >= 2:
        f.save_image("blob_mask", blob_mask)

    # -------------------------------------------------------
    # Punto más seguro
    # -------------------------------------------------------

    dist = cv2.distanceTransform(
        blob_mask,
        cv2.DIST_L2,
        5
    )

    _, maxDist, _, maxLoc = cv2.minMaxLoc(dist)

    best_x = maxLoc[0]
    best_y = maxLoc[1]
    radius = int(maxDist * config.DROP_RADIUS_FACTOR)
    

    # -------------------------------------------------------
    # Imagen de depuración
    # -------------------------------------------------------

    debug = img.copy()

    # Contorno del blob

    contours, _ = cv2.findContours(
        blob_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    cv2.drawContours(
        debug,
        contours,
        -1,
        (0,255,0),
        2
    )

    cv2.circle(
        debug,
        (best_x, best_y),
        8,
        (255,0,0),
        -1
    )

    cv2.circle(
        debug,
        (best_x, best_y),
        radius,
        (0,255,255),
        2
    )

    # -------------------------------------------------------
    # Dibujar agujeros (solo depuración)
    # -------------------------------------------------------

    contours, hierarchy = cv2.findContours(
        blob_mask,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if hierarchy is not None:

        hierarchy = hierarchy[0]

        for i in range(len(contours)):

            # Contorno exterior
            if hierarchy[i][3] == -1:

                cv2.drawContours(
                    debug,
                    contours,
                    i,
                    (0, 255, 0),
                    2
                )

            # Agujero
            else:

                # Ignorar agujeros muy pequeños (ruido)
                if cv2.contourArea(contours[i]) < 150:
                    continue

                cv2.drawContours(
                    debug,
                    contours,
                    i,
                    (0, 0, 255),
                    2
                )

    # -------------------------------------------------------
    # salvar imagen de depuración
    # -------------------------------------------------------

    if config.DROP_ANALYZER_DEBUG >= 1:
        f.save_image("green_analysis", debug)

    return {
        "mask": blob_mask,
        "point": (best_x, best_y),
        "radius": radius
    }