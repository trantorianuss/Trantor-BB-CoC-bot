import cv2
import numpy as np
import time as t
import os

import func as f
import config
from logger import log


DROP_HISTORY_FILE = "logs/drop_finder_history.log"
MIN_GREEN_AREA = 1000
MIN_DROP_RADIUS = 5


def _write_drop_history(**data):
    """Append one diagnostic record to the drop finder history file."""
    if not config.DEBUG_FILE_LOGS.get("drop_finder", False):
        return

    os.makedirs(os.path.dirname(DROP_HISTORY_FILE), exist_ok=True)

    timestamp = t.strftime("%Y-%m-%d %H:%M:%S")
    fields = [f"{timestamp}"]
    fields.extend(f"{key}={value}" for key, value in data.items())

    with open(DROP_HISTORY_FILE, "a", encoding="utf-8") as history:
        history.write(" | ".join(fields) + "\n")


def find_drop_point():

    img = f.capture_screenshot()

    if img is None:
        _write_drop_history(result="NO_SCREENSHOT", image_file="N/A")
        log("No se pudo capturar la pantalla", category="Drop", color="red")
        return None

    height, width = img.shape[:2]
    image_file = "N/A (captura en memoria)"

    if config.DROP_ANALYZER_DEBUG >= 3:
        image_file = f.save_image("DropAnalyzer", img)

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
    component_count = max(0, num_labels - 1)

    if num_labels <= 1:
        _write_drop_history(
            result="NO_POINT",
            image_file=image_file,
            image=f"{width}x{height}",
            components=component_count,
            best_area=0,
            green_ratio="0.000%",
        )
        log(
            f"No se encontró zona verde: components={component_count}",
            color="red",
            category="Drop"
        )
        return None

    best_label = -1
    best_area = 0

    for label in range(1, num_labels):

        area = stats[label, cv2.CC_STAT_AREA]

        if area > best_area:

            best_area = area
            best_label = label

    # Rechazar falsos positivos diminutos antes de calcular el punto de drop.
    if best_area < MIN_GREEN_AREA:
        green_ratio = (best_area / (width * height)) * 100
        _write_drop_history(
            result="NO_POINT",
            image_file=image_file,
            image=f"{width}x{height}",
            components=component_count,
            best_area=best_area,
            green_ratio=f"{green_ratio:.3f}%",
            reason=f"area<{MIN_GREEN_AREA}",
        )
        log(
            f"Zona rechazada: area={best_area} < {MIN_GREEN_AREA}",
            debug=True,
            color="red",
            category="Drop",
        )
        return None

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
    green_ratio = (best_area / (width * height)) * 100

    # Rechazar zonas demasiado estrechas para generar un drop útil.
    if radius < MIN_DROP_RADIUS:
        _write_drop_history(
            result="NO_POINT",
            image_file=image_file,
            image=f"{width}x{height}",
            components=component_count,
            best_area=best_area,
            green_ratio=f"{green_ratio:.3f}%",
            bbox=f"{x},{y},{w},{h}",
            point=f"{best_x},{best_y}",
            max_dist=f"{maxDist:.2f}",
            radius=radius,
            reason=f"radius<{MIN_DROP_RADIUS}",
        )
        log(
            f"Zona rechazada: radius={radius} < {MIN_DROP_RADIUS}",
            color="red",
            category="Drop",
        )
        return None

    _write_drop_history(
        result="OK",
        image_file=image_file,
        image=f"{width}x{height}",
        components=component_count,
        best_area=best_area,
        green_ratio=f"{green_ratio:.3f}%",
        bbox=f"{x},{y},{w},{h}",
        point=f"{best_x},{best_y}",
        max_dist=f"{maxDist:.2f}",
        radius=radius,
    )

    log(
        f"Zona encontrada: area={best_area}, "
        f"ratio={green_ratio:.3f}%, components={component_count}, "
        f"radius={radius}",
        category="Drop",
        color="green" if radius >= MIN_DROP_RADIUS else "red"
    )

    # -------------------------------------------------------
    # Imagen de depuración
    # -------------------------------------------------------

    debug = img.copy()

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

    contours, hierarchy = cv2.findContours(
        blob_mask,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if hierarchy is not None:

        hierarchy = hierarchy[0]

        for i in range(len(contours)):

            if hierarchy[i][3] == -1:

                cv2.drawContours(
                    debug,
                    contours,
                    i,
                    (0, 255, 0),
                    2
                )

            else:

                if cv2.contourArea(contours[i]) < 150:
                    continue

                cv2.drawContours(
                    debug,
                    contours,
                    i,
                    (0, 0, 255),
                    2
                )

    if config.DROP_ANALYZER_DEBUG >= 1:
        f.save_image("green_analysis", debug)

    return {
        "mask": blob_mask,
        "point": (best_x, best_y),
        "radius": radius
    }
