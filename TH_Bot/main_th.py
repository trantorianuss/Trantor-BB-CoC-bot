"""TH bot entry point and calibration tools."""

import json
import msvcrt
import time
from pathlib import Path
from types import SimpleNamespace

import cv2

import coords
import func as f

from TH_Bot.gameflow_th import th_game_flow
from TH_Bot.troops_th import DEPLOY_SEQUENCE


ELIXIR_FULL_PIXEL = (1540, 176)
ELIXIR_FULL_COLOR = (192, 39, 192)
ATTACK_BUTTON_1 = (125, 995)
FIND_BUTTON = (320, 800)
ATTACK_BUTTON_2 = (1700, 960)
MULTITAP_MAX = 4
ATTACK_BUTTON_DELAY = 0.5
BETWEEN_TROOPS_DELAY = 0
AFTER_BATTLE_END_DELAY = 2.0
SCREEN_DETECT_DELAY = 2
EXIT_POLL_INTERVAL = 0.05
DROP_POINTS_EDGE = [(80, 440), (120, 400), (160, 360), (200, 320)]
DROP_POINT_CENTER = (960, 540)
DROP_DIAMOND_CENTER = (960, 540)
DROP_DIAMOND_HALF_WIDTH = 450
DROP_DIAMOND_HALF_HEIGHT = 450
ATTACK_CONFIG_FILE = Path(__file__).with_name("attack_th.json")
EDGE_ZONE_START = None
EDGE_ZONE_END = None
EDGE_ZONE_POINTS = []
TH_SLOT_1_CENTER = None
TH_SLOT_2_CENTER = None
ZONE_WINDOW_MAX_WIDTH = 1000
ZONE_WINDOW_MAX_HEIGHT = 700
PIXEL_TOLERANCE = 10


def exit_requested():
    if msvcrt.kbhit():
        key = msvcrt.getwch()
        if key.lower() == "x":
            f.log("[TH] X pulsada -> saliendo de la rutina", color="yellow")
            return True
    return False


def sleep_with_exit(seconds):
    end_time = time.time() + seconds
    while True:
        if exit_requested():
            return False
        remaining = end_time - time.time()
        if remaining <= 0:
            return True
        time.sleep(min(EXIT_POLL_INTERVAL, remaining))


def load_attack_config():
    global EDGE_ZONE_START, EDGE_ZONE_END, EDGE_ZONE_POINTS, TH_SLOT_1_CENTER, TH_SLOT_2_CENTER
    if not ATTACK_CONFIG_FILE.exists():
        f.log("[TH] No existe attack_th.json; será necesario definir la calibración")
        return False
    try:
        with ATTACK_CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)
        start = config.get("edge_zone_start")
        end = config.get("edge_zone_end")
        if start and end:
            EDGE_ZONE_START = tuple(start)
            EDGE_ZONE_END = tuple(end)
            build_edge_zone_points()
            f.log(f"[TH] Zona EDGE cargada: {EDGE_ZONE_START} -> {EDGE_ZONE_END} ({len(EDGE_ZONE_POINTS)} puntos)")
        else:
            f.log("[TH] Zona EDGE no definida")
        slot_1 = config.get("slot_1_center")
        slot_2 = config.get("slot_2_center")
        TH_SLOT_1_CENTER = tuple(slot_1) if slot_1 else None
        TH_SLOT_2_CENTER = tuple(slot_2) if slot_2 else None
        if TH_SLOT_1_CENTER and TH_SLOT_2_CENTER:
            f.log(f"[TH] Slots cargados: S1={TH_SLOT_1_CENTER} | S2={TH_SLOT_2_CENTER}")
        else:
            f.log("[TH] Centros de slots no definidos; será necesario calibrarlos")
        return True
    except Exception as exc:
        f.log(f"[TH] No se pudo cargar attack_th.json: {exc}", color="red")
        return False


def save_attack_config():
    config = {}
    if EDGE_ZONE_START is not None and EDGE_ZONE_END is not None:
        config["edge_zone_start"] = list(EDGE_ZONE_START)
        config["edge_zone_end"] = list(EDGE_ZONE_END)
    if TH_SLOT_1_CENTER is not None:
        config["slot_1_center"] = list(TH_SLOT_1_CENTER)
    if TH_SLOT_2_CENTER is not None:
        config["slot_2_center"] = list(TH_SLOT_2_CENTER)
    try:
        with ATTACK_CONFIG_FILE.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)
        f.log(f"[TH] Configuración guardada en {ATTACK_CONFIG_FILE.name}")
    except Exception as exc:
        f.log(f"[TH] No se pudo guardar attack_th.json: {exc}", color="red")


def build_edge_zone_points():
    global EDGE_ZONE_POINTS
    distance = ((EDGE_ZONE_END[0] - EDGE_ZONE_START[0]) ** 2 + (EDGE_ZONE_END[1] - EDGE_ZONE_START[1]) ** 2) ** 0.5
    point_count = max(2, int(distance / 40) + 1)
    EDGE_ZONE_POINTS = []
    for i in range(point_count):
        t = i / (point_count - 1)
        x = int(EDGE_ZONE_START[0] + t * (EDGE_ZONE_END[0] - EDGE_ZONE_START[0]))
        y = int(EDGE_ZONE_START[1] + t * (EDGE_ZONE_END[1] - EDGE_ZONE_START[1]))
        EDGE_ZONE_POINTS.append((x, y))


def get_th_slot_position(n):
    if TH_SLOT_1_CENTER is None or TH_SLOT_2_CENTER is None:
        raise RuntimeError("TH slot centers are not calibrated")
    step_x = TH_SLOT_2_CENTER[0] - TH_SLOT_1_CENTER[0]
    fixed_y = (TH_SLOT_1_CENTER[1] + TH_SLOT_2_CENTER[1]) / 2
    return int(TH_SLOT_1_CENTER[0] + step_x * (n - 1)), int(fixed_y)


def debug_tap_scale(x, y, name, color):
    image = f.capture_screenshot()
    if image is None:
        f.log(f"[TH DEBUG] No se pudo capturar screenshot para {name}", color="red")
        f.tap_scale(x, y)
        return not exit_requested()
    marked_x, marked_y = x, y
    if coords.REAL_W is not None and coords.REAL_H is not None:
        marked_x, marked_y = coords.scale(x, y)
    f.log(f"[TH DEBUG] {name}: coordenadas iniciales=({x},{y}) | coordenadas convertidas=({marked_x},{marked_y})")
    image_h, image_w = image.shape[:2]
    cv2.circle(image, (image_w // 2, image_h // 2), 50, (0, 255, 255), 5)
    cv2.circle(image, (int(marked_x), int(marked_y)), 25, color, 4)
    cv2.drawMarker(image, (int(marked_x), int(marked_y)), color, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=3)
    filename = f.save_image(f"th_debug_{name}", image)
    f.log(f"[TH DEBUG] Screenshot guardado: {filename}")
    f.tap_scale(x, y)
    return not exit_requested()


def save_deployment_debug():
    image = f.capture_screenshot()
    if image is None:
        f.log("[TH DEBUG] No se pudo capturar screenshot del mapa de despliegue", color="red")
        return
    def to_real(point):
        x, y = point
        if coords.REAL_W is not None and coords.REAL_H is not None:
            return tuple(int(v) for v in coords.scale(x, y))
        return int(x), int(y)
    center = to_real(DROP_DIAMOND_CENTER)
    diamond = [
        to_real((DROP_DIAMOND_CENTER[0], DROP_DIAMOND_CENTER[1] - DROP_DIAMOND_HALF_HEIGHT)),
        to_real((DROP_DIAMOND_CENTER[0] + DROP_DIAMOND_HALF_WIDTH, DROP_DIAMOND_CENTER[1])),
        to_real((DROP_DIAMOND_CENTER[0], DROP_DIAMOND_CENTER[1] + DROP_DIAMOND_HALF_HEIGHT)),
        to_real((DROP_DIAMOND_CENTER[0] - DROP_DIAMOND_HALF_WIDTH, DROP_DIAMOND_CENTER[1])),
    ]
    for p1, p2 in zip(diamond, diamond[1:] + diamond[:1]):
        cv2.line(image, p1, p2, (0, 255, 255), 3)
    cv2.circle(image, center, 10, (0, 255, 255), -1)
    if EDGE_ZONE_START is not None and EDGE_ZONE_END is not None:
        start = to_real(EDGE_ZONE_START)
        end = to_real(EDGE_ZONE_END)
        cv2.line(image, start, end, (255, 0, 255), 4)
        cv2.circle(image, start, 10, (255, 0, 255), -1)
        cv2.circle(image, end, 10, (255, 0, 255), -1)
        for point in EDGE_ZONE_POINTS:
            cv2.circle(image, to_real(point), 6, (255, 0, 0), -1)
    if TH_SLOT_1_CENTER is not None and TH_SLOT_2_CENTER is not None:
        for slot_number in range(1, 11):
            x, y = to_real(get_th_slot_position(slot_number))
            cv2.circle(image, (x, y), 18, (0, 255, 0), 2)
            cv2.putText(image, str(slot_number), (x - 8, y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    filename = f.save_image("th_deployment_debug", image)
    f.log(f"[TH DEBUG] Mapa despliegue guardado: {filename}")


def select_two_points(title, prompt):
    image = f.capture_screenshot()
    if image is None:
        f.log("[TH] No se pudo capturar screenshot para la calibración", color="red")
        return None
    image_h, image_w = image.shape[:2]
    display_scale = min(1.0, ZONE_WINDOW_MAX_WIDTH / image_w, ZONE_WINDOW_MAX_HEIGHT / image_h)
    display_w = int(image_w * display_scale)
    display_h = int(image_h * display_scale)
    display_image = cv2.resize(image, (display_w, display_h))
    points = []
    def mouse_callback(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN or len(points) >= 2:
            return
        base_x = int((x / display_scale) / coords.SX)
        base_y = int((y / display_scale) / coords.SY)
        points.append((base_x, base_y))
        cv2.circle(display_image, (x, y), 7, (0, 255, 0), -1)
        cv2.putText(display_image, str(len(points)), (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if len(points) == 2:
            p1 = (int(points[0][0] * coords.SX * display_scale), int(points[0][1] * coords.SY * display_scale))
            p2 = (int(points[1][0] * coords.SX * display_scale), int(points[1][1] * coords.SY * display_scale))
            cv2.line(display_image, p1, p2, (0, 255, 255), 3)
        cv2.imshow(title, display_image)
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(title, mouse_callback)
    f.log(prompt)
    f.log("[TH] Pulsa ESC para cancelar")
    while len(points) < 2:
        cv2.imshow(title, display_image)
        key = cv2.waitKey(50) & 0xFF
        if key == 27:
            cv2.destroyWindow(title)
            f.log("[TH] Calibración cancelada")
            return None
    cv2.imshow(title, display_image)
    cv2.waitKey(500)
    cv2.destroyWindow(title)
    return points


def select_edge_zone():
    global EDGE_ZONE_START, EDGE_ZONE_END
    points = select_two_points("TH - Selecciona zona EDGE (2 puntos)", "[TH] Haz click en los DOS extremos de la zona EDGE")
    if points is None:
        return False
    EDGE_ZONE_START, EDGE_ZONE_END = points
    build_edge_zone_points()
    save_attack_config()
    return True


def select_slot_centers():
    global TH_SLOT_1_CENTER, TH_SLOT_2_CENTER
    points = select_two_points("TH - Centros Slot 1 y Slot 2", "[TH] Haz click en el CENTRO del Slot 1 y después en el CENTRO del Slot 2")
    if points is None:
        return False
    TH_SLOT_1_CENTER, TH_SLOT_2_CENTER = points
    save_attack_config()
    return True


def prepare_th_run():
    initialize_coords()
    load_attack_config()
    while True:
        print()
        print("1. Marcar zona de despliegue EDGE")
        print("2. Marcar centro del Slot 1 y centro del Slot 2")
        print("X. Exit")
        print("0. Ejecutar")
        choice = input("> ").strip()
        if choice == "1":
            select_edge_zone()
        elif choice == "2":
            select_slot_centers()
        elif choice.lower() == "x":
            f.log("[TH] X. Exit -> saliendo del menú", color="yellow")
            return False
        elif choice == "0":
            missing = []
            if TH_SLOT_1_CENTER is None:
                missing.append("centro del Slot 1")
            if TH_SLOT_2_CENTER is None:
                missing.append("centro del Slot 2")
            if missing:
                f.log("[TH] No se puede ejecutar: falta " + " y ".join(missing) + ". Usa la opción 2.", color="yellow")
                continue
            return True
        else:
            print("Opción no válida")


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


def build_context():
    return SimpleNamespace(
        ELIXIR_FULL_PIXEL=ELIXIR_FULL_PIXEL,
        ELIXIR_FULL_COLOR=ELIXIR_FULL_COLOR,
        ATTACK_BUTTON_1=ATTACK_BUTTON_1,
        FIND_BUTTON=FIND_BUTTON,
        ATTACK_BUTTON_2=ATTACK_BUTTON_2,
        MULTITAP_MAX=MULTITAP_MAX,
        ATTACK_BUTTON_DELAY=ATTACK_BUTTON_DELAY,
        BETWEEN_TROOPS_DELAY=BETWEEN_TROOPS_DELAY,
        AFTER_BATTLE_END_DELAY=AFTER_BATTLE_END_DELAY,
        SCREEN_DETECT_DELAY=SCREEN_DETECT_DELAY,
        DROP_POINTS_EDGE=DROP_POINTS_EDGE,
        DROP_POINT_CENTER=DROP_POINT_CENTER,
        DROP_DIAMOND_CENTER=DROP_DIAMOND_CENTER,
        DROP_DIAMOND_HALF_WIDTH=DROP_DIAMOND_HALF_WIDTH,
        DROP_DIAMOND_HALF_HEIGHT=DROP_DIAMOND_HALF_HEIGHT,
        DEPLOY_SEQUENCE=DEPLOY_SEQUENCE,
        PIXEL_TOLERANCE=PIXEL_TOLERANCE,
        EDGE_ZONE_POINTS=EDGE_ZONE_POINTS,
        exit_requested=exit_requested,
        sleep_with_exit=sleep_with_exit,
        get_th_slot_position=get_th_slot_position,
        save_deployment_debug=save_deployment_debug,
    )


if __name__ == "__main__":
    if prepare_th_run():
        th_game_flow(build_context())
