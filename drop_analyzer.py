import os
import math

import cv2
import numpy as np


SEARCH_RADIUS = 250
OFFSET = 40


def analyze_drop(image_file, drop_x, drop_y):

    img = cv2.imread(image_file)

    if img is None:
        print(f"No se pudo abrir {image_file}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 60, 60])
    upper_red1 = np.array([15, 255, 255])

    lower_red2 = np.array([165, 60, 60])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = cv2.bitwise_or(mask1, mask2)

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

    