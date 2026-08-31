"""Debug helpers for the Town Hall bot."""

import cv2

import coords
import func as f

from TH_Bot import screen_layout_th

_EDGE_ZONE_START = None
_EDGE_ZONE_END = None
_EDGE_ZONE_POINTS = []
_SLOT_1_CENTER = None
_SLOT_2_CENTER = None


def configure(edge_zone_start=None, edge_zone_end=None, edge_zone_points=None, slot_1_center=None, slot_2_center=None):
    """Set the current TH geometry used by deployment debug screenshots."""
    global _EDGE_ZONE_START, _EDGE_ZONE_END, _EDGE_ZONE_POINTS
    global _SLOT_1_CENTER, _SLOT_2_CENTER
    _EDGE_ZONE_START = edge_zone_start
    _EDGE_ZONE_END = edge_zone_end
    _EDGE_ZONE_POINTS = edge_zone_points or []
    _SLOT_1_CENTER = slot_1_center
    _SLOT_2_CENTER = slot_2_center


def save_deployment_debug(image):
    """Save a deployment screenshot with the configured TH debug geometry."""
    if image is None:
        f.log("[TH DEBUG] No se pudo usar screenshot del mapa de despliegue", color="red")
        return

    def to_real(point):
        x, y = point
        if coords.REAL_W is not None and coords.REAL_H is not None:
            return tuple(int(v) for v in coords.scale(x, y))
        return int(x), int(y)

    center = to_real(screen_layout_th.DROP_DIAMOND_CENTER)
    diamond = [
        to_real((screen_layout_th.DROP_DIAMOND_CENTER[0], screen_layout_th.DROP_DIAMOND_CENTER[1] - screen_layout_th.DROP_DIAMOND_HALF_HEIGHT)),
        to_real((screen_layout_th.DROP_DIAMOND_CENTER[0] + screen_layout_th.DROP_DIAMOND_HALF_WIDTH, screen_layout_th.DROP_DIAMOND_CENTER[1])),
        to_real((screen_layout_th.DROP_DIAMOND_CENTER[0], screen_layout_th.DROP_DIAMOND_CENTER[1] + screen_layout_th.DROP_DIAMOND_HALF_HEIGHT)),
        to_real((screen_layout_th.DROP_DIAMOND_CENTER[0] - screen_layout_th.DROP_DIAMOND_HALF_WIDTH, screen_layout_th.DROP_DIAMOND_CENTER[1])),
    ]
    for p1, p2 in zip(diamond, diamond[1:] + diamond[:1]):
        cv2.line(image, p1, p2, (0, 255, 255), 3)
    cv2.circle(image, center, 10, (0, 255, 255), -1)

    if _EDGE_ZONE_START is not None and _EDGE_ZONE_END is not None:
        start = to_real(_EDGE_ZONE_START)
        end = to_real(_EDGE_ZONE_END)
        cv2.line(image, start, end, (255, 0, 255), 4)
        cv2.circle(image, start, 10, (255, 0, 255), -1)
        cv2.circle(image, end, 10, (255, 0, 255), -1)
        for point in _EDGE_ZONE_POINTS:
            cv2.circle(image, to_real(point), 6, (255, 0, 0), -1)

    if _SLOT_1_CENTER is not None and _SLOT_2_CENTER is not None:
        step_x = _SLOT_2_CENTER[0] - _SLOT_1_CENTER[0]
        fixed_y = (_SLOT_1_CENTER[1] + _SLOT_2_CENTER[1]) / 2
        for slot_number in range(1, 11):
            point = (_SLOT_1_CENTER[0] + step_x * (slot_number - 1), fixed_y)
            x, y = to_real(point)
            cv2.circle(image, (x, y), 18, (0, 255, 0), 2)
            cv2.putText(image, str(slot_number), (x - 8, y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    filename = f.save_image("th_deployment_debug", image)
    f.log(f"[TH DEBUG] Mapa despliegue guardado: {filename}")
