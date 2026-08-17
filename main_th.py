"""
Standalone game flow for the Town Hall (main village).

This file is intentionally independent from gameflow.py / Builder Base flow.
It can be executed directly from the command line:

    python main_th.py
"""

import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2

import func as f
import coords
import screen_layout as layout


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

ELIXIR_FULL_PIXEL = (1530, 182)
ELIXIR_FULL_COLOR = (192, 39, 192)
BATTLE_END_PIXEL = (960, 960)
BATTLE_END_COLOR = (108, 187, 31)

ATTACK_BUTTON_1 = (125, 995)
FIND_BUTTON = (320, 800)
ATTACK_BUTTON_2 = (1700, 960)

# Maximum number of taps sent in one fast multitap batch.
MULTITAP_MAX = 4

# Each entry: (slot, number of troops, drop area, delay before action, multitap).
# count=0 means: press the slot only, without dropping troops.
# multitap=True sends drops in batches of up to MULTITAP_MAX.
# multitap=False sends drops one by one using the normal tap method.
# Drop areas: "edge", "center" and "random".
DEPLOY_SEQUENCE = [
    (1,  6, "edge",   0,   True),
    (2, 12, "edge",   0,   True),
    (3,  3, "edge",   0,   False),
    (4,  1, "edge",   0,   False),
    (5,  1, "edge",   0.1, False),
    (6,  1, "edge",   0.1, False),
    (7,  1, "edge",   0.1, False),
    (8,  1, "edge",   0.1, False),
    (5,  0, "edge",   0.1, False),
    (6,  0, "edge",   0.1, False),
    (7,  0, "edge",   0.1, False),
    (8,  0, "edge",   0.1, False),
    (9, 10, "random", 0,   True),
    (10, 1, "random", 0,   True),
]

DROP_POINTS_EDGE = [
    (80, 440),
    (120, 400),
    (160, 360),
    (200, 320),
]
DROP_POINT_CENTER = (960, 540)

DROP_DIAMOND_CENTER = (960, 540)
DROP_DIAMOND_HALF_WIDTH = 450
DROP_DIAMOND_HALF_HEIGHT = 450

ATTACK_CONFIG_FILE = Path(__file__).with_name("attack_th.json")

EDGE_ZONE_START = None
EDGE_ZONE_END = None
EDGE_ZONE_POINTS = []

ZONE_WINDOW_MAX_WIDTH = 1000
ZONE_WINDOW_MAX_HEIGHT = 700
PIXEL_TOLERANCE = 10


# -----------------------------------------------------------------------------
# Persistent TH configuration
# -----------------------------------------------------------------------------

def load_attack_config():
    global EDGE_ZONE_START, EDGE_ZONE_END, EDGE_ZONE_POINTS

    if not ATTACK_CONFIG_FILE.exists():
        f.log("[TH] No existe attack_th.json; será necesario definir la zona EDGE")
        return False

    try:
        with ATTACK_CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)

        start = config.get("edge_zone_start")
        end = config.get("edge_zone_end")

        if not start or not end:
            f.log("[TH] attack_th.json no contiene una zona EDGE válida")
            return False

        EDGE_ZONE_START = tuple(start)
        EDGE_ZONE_END = tuple(end)
        build_edge_zone_points()

        f.log(
            f"[TH] Zona EDGE cargada: {EDGE_ZONE_START} -> {EDGE_ZONE_END} "
            f"({len(EDGE_ZONE_POINTS)} puntos)"
        )
        return True

    except Exception as exc:
        f.log(f"[TH] No se pudo cargar attack_th.json: {exc}", color="red")
        return False


def save_attack_config():
    config = {
        "edge_zone_start": list(EDGE_ZONE_START),
        "edge_zone_end": list(EDGE_ZONE_END),
    }

    try:
        with ATTACK_CONFIG_FILE.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)
        f.log(f"[TH] Configuración guardada en {ATTACK_CONFIG_FILE.name}")
    except Exception as exc:
        f.log(f"[TH] No se pudo guardar attack_th.json: {exc}", color="red")


def build_edge_zone_points():
    """Generate points along the selected edge line in BASE coordinates."""
    global EDGE_ZONE_POINTS

    distance = (
        (EDGE_ZONE_END[0] - EDGE_ZONE_START[0]) ** 2
        + (EDGE_ZONE_END[1] - EDGE_ZONE_START[1]) ** 2
    ) ** 0.5
    point_count = max(2, int(distance / 40) + 1)

    EDGE_ZONE_POINTS = []
    for i in range(point_count):
        t = i / (point_count - 1)
        x = int(EDGE_ZONE_START[0] + t * (EDGE_ZONE_END[0] - EDGE_ZONE_START[0]))
        y = int(EDGE_ZONE_START[1] + t * (EDGE_ZONE_END[1] - EDGE_ZONE_START[1]))
        EDGE_ZONE_POINTS.append((x, y))


# -----------------------------------------------------------------------------
# Debug: screenshot + mark tap_scale position
# -----------------------------------------------------------------------------

def debug_tap_scale(x, y, name, color):
    image = f.capture_screenshot()

    if image is None:
        f.log(f"[TH DEBUG] No se pudo capturar screenshot para {name}", color="red")
        f.tap_scale(x, y)
        return

    marked_x, marked_y = x, y
    if coords.REAL_W is not None and coords.REAL_H is not None:
        marked_x, marked_y = coords.scale(x, y)

    f.log(
        f"[TH DEBUG] {name}: coordenadas iniciales=({x},{y}) | "
        f"coordenadas convertidas=({marked_x},{marked_y})"
    )

    image_h, image_w = image.shape[:2]
    cv2.circle(image, (image_w // 2, image_h // 2), 50, (0, 255, 255), 5)
    cv2.circle(image, (int(marked_x), int(marked_y)), 25, color, 4)
    cv2.drawMarker(
        image,
        (int(marked_x), int(marked_y)),
        color,
        markerType=cv2.MARKER_CROSS,
        markerSize=40,
        thickness=3,
    )

    filename = f.save_image(f"th_debug_{name}", image)
    f.log(f"[TH DEBUG] Screenshot guardado: {filename}")
    f.tap_scale(x, y)


# -----------------------------------------------------------------------------
# Interactive deployment zone selection
# -----------------------------------------------------------------------------

def select_edge_zone():
    global EDGE_ZONE_START, EDGE_ZONE_END

    image = f.capture_screenshot()
    if image is None:
        f.log("[TH] No se pudo capturar screenshot para definir la zona", color="red")
        return False

    image_h, image_w = image.shape[:2]
    display_scale = min(
        1.0,
        ZONE_WINDOW_MAX_WIDTH / image_w,
        ZONE_WINDOW_MAX_HEIGHT / image_h,
    )
    display_w = int(image_w * display_scale)
    display_h = int(image_h * display_scale)
    display_image = cv2.resize(image, (display_w, display_h))

    window_name = "TH - Selecciona zona EDGE (2 puntos)"
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN or len(points) >= 2:
            return
        points.append((int(x / display_scale), int(y / display_scale)))
        cv2.circle(display_image, (x, y), 7, (0, 255, 0), -1)
        if len(points) == 2:
            p1 = tuple(int(v * display_scale) for v in points[0])
            p2 = tuple(int(v * display_scale) for v in points[1])
            cv2.line(display_image, p1, p2, (0, 255, 255), 3)
        cv2.imshow(window_name, display_image)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouse_callback)
    f.log("[TH] Haz click en los DOS extremos de la zona EDGE")
    f.log("[TH] Pulsa ESC para cancelar")

    while len(points) < 2:
        cv2.imshow(window_name, display_image)
        key = cv2.waitKey(50) & 0xFF
        if key == 27:
            cv2.destroyWindow(window_name)
            f.log("[TH] Selección de zona EDGE cancelada")
            return False

    cv2.imshow(window_name, display_image)
    cv2.waitKey(500)
    cv2.destroyWindow(window_name)

    # Clicks are in REAL screenshot coordinates. Convert to BASE before saving.
    EDGE_ZONE_START = (
        int(points[0][0] / coords.SX),
        int(points[0][1] / coords.SY),
    )
    EDGE_ZONE_END = (
        int(points[1][0] / coords.SX),
        int(points[1][1] / coords.SY),
    )

    build_edge_zone_points()
    save_attack_config()

    f.log(
        f"[TH] Zona EDGE real: {points[0]} -> {points[1]} | "
        f"base: {EDGE_ZONE_START} -> {EDGE_ZONE_END} | "
        f"({len(EDGE_ZONE_POINTS)} puntos)"
    )
    return True


def prepare_th_run():
    """Initialize resolution, load config and wait for the next action."""
    initialize_coords()
    load_attack_config()

    while True:
        print()
        print("Pulsa 1 para indicar/redefinir zona de despliegue EDGE")
        print("Pulsa 2 para atacar")
        choice = input("> ").strip()

        if choice == "1":
            select_edge_zone()
        elif choice == "2":
            if not EDGE_ZONE_POINTS:
                f.log("[TH] No se ha definido zona EDGE; se usarán los puntos de fallback", color="yellow")
            return
        else:
            print("Opción no válida")


# -----------------------------------------------------------------------------
# TH game flow
# -----------------------------------------------------------------------------

def th_game_flow():
    f.log("[TH] Starting standalone TH game flow")

    while not is_elixir_full():
        f.log("[TH] Elixir not full -> starting attack")
        start_attack()
        deploy_troops()

        if not wait_for_battle_end():
            f.log("[TH] Battle did not finish. Leaving flow.")
            return

        f.log("[TH] Battle finished -> checking elixir again")

    f.log("[TH] Elixir is full -> flow finished")


# -----------------------------------------------------------------------------
# Individual TH steps
# -----------------------------------------------------------------------------

def is_elixir_full():
    image = f.capture_screenshot()
    x, y = ELIXIR_FULL_PIXEL
    return f.check_pixel_from_image(
        image, x, y, ELIXIR_FULL_COLOR, tol=PIXEL_TOLERANCE
    )


def start_attack():
    f.log("[TH] Pressing first attack button")
    f.tap_scale(*ATTACK_BUTTON_1)
    time.sleep(0.5)

    f.log("[TH] Pressing Find")
    f.tap_scale(*FIND_BUTTON)
    time.sleep(0.5)

    f.log("[TH] Pressing second attack button")
    f.tap_scale(*ATTACK_BUTTON_2)
    time.sleep(2)


def slot(n):
    x = layout.FIRST_SLOT_CENTER[0] + layout.SLOT_STEP * (n - 1)
    y = layout.FIRST_SLOT_CENTER[1]
    f.tap_scale(x, y)


def multi_tap_scale(points):
    """Fast burst of scaled taps, up to the configured batch size."""
    if not points:
        return

    scaled_points = [
        coords.scale(x, y)
        if coords.REAL_W is not None and coords.REAL_H is not None
        else (x, y)
        for x, y in points
    ]

    f.log(f"[TH MULTI TAP] {len(scaled_points)} taps: {scaled_points}")

    def send(point):
        x, y = point
        f.adb(f"input tap {x} {y}")

    with ThreadPoolExecutor(max_workers=len(scaled_points)) as executor:
        list(executor.map(send, scaled_points))


def random_drop_point():
    center_x, center_y = DROP_DIAMOND_CENTER
    half_width = DROP_DIAMOND_HALF_WIDTH
    half_height = DROP_DIAMOND_HALF_HEIGHT

    while True:
        x = random.uniform(center_x - half_width, center_x + half_width)
        y = random.uniform(center_y - half_height, center_y + half_height)
        if abs(x - center_x) / half_width + abs(y - center_y) / half_height <= 1:
            return int(x), int(y)


def deploy_troops():
    edge_index = 0

    for slot_number, count, drop_area, delay, use_multitap in DEPLOY_SEQUENCE:
        if delay > 0:
            time.sleep(delay)

        f.log(
            f"[TH] Slot {slot_number} | cantidad={count} | "
            f"zona={drop_area} | delay={delay}s | multitap={use_multitap}"
        )
        slot(slot_number)

        if count == 0:
            continue

        if drop_area == "center":
            drop_points = [DROP_POINT_CENTER]
        elif drop_area == "edge":
            drop_points = EDGE_ZONE_POINTS if EDGE_ZONE_POINTS else DROP_POINTS_EDGE
        elif drop_area == "random":
            drop_points = None
        else:
            f.log(f"[TH] Zona de despliegue desconocida: {drop_area}", color="red")
            continue

        points_to_drop = []
        for _ in range(count):
            if drop_area == "edge":
                drop_point = drop_points[edge_index % len(drop_points)]
                edge_index += 1
            elif drop_area == "random":
                drop_point = random_drop_point()
                f.log(f"[TH] Random drop -> {drop_point}")
            else:
                drop_point = drop_points[0]
            points_to_drop.append(drop_point)

        if use_multitap:
            for start in range(0, len(points_to_drop), MULTITAP_MAX):
                batch = points_to_drop[start:start + MULTITAP_MAX]
                multi_tap_scale(batch)
        else:
            for point in points_to_drop:
                f.tap_scale(*point)
                time.sleep(0.5)

    f.log("[TH] Despliegue terminado")


def wait_for_battle_end():
    f.log("[TH] Waiting for battle to finish")
    elapsed = 0

    while True:
        image = f.capture_screenshot()
        x, y = BATTLE_END_PIXEL

        if f.check_pixel_from_image(image, x, y, BATTLE_END_COLOR, tol=PIXEL_TOLERANCE):
            f.log(f"[TH] Battle end button detected after {elapsed}s -> tapping")
            f.tap_scale(*BATTLE_END_PIXEL)
            time.sleep(1)
            f.log("[TH] Battle end button tapped")
            return True

        elapsed += 1
        if elapsed % 5 == 0:
            f.log(f"[TH] Battle still running... {elapsed}s")
        time.sleep(1)


def initialize_coords():
    f.log("[coords] Inicializando resolución...")
    try:
        real_w, real_h = f.get_real_resolution()
        coords.init_resolution(real_w, real_h)
        f.log(f"[coords] Resolución inicializada: {real_w}x{real_h}")
    except Exception as exc:
        f.log(f"[coords] No se pudo obtener la resolución real: {exc}")
        coords.init_resolution(1920, 1080)
        f.log("[coords] Usando resolución por defecto: 1920x1080")


if __name__ == "__main__":
    prepare_th_run()
    th_game_flow()
