"""TH bot command-line entry point and calibration tools."""

import json
import cv2
from pathlib import Path

import botstate
import coords
import func as f

from TH_Bot import config_th, screen_layout_th, th_debug
from TH_Bot.gameflow_th import th_game_flow
from TH_Bot.th_strategies import DEFAULT_STRATEGY, build_context


ATTACK_CONFIG_FILE = Path(__file__).with_name(config_th.ATTACK_CONFIG_FILENAME)
EDGE_ZONE_START = None
EDGE_ZONE_END = None
EDGE_ZONE_POINTS = []
TH_SLOT_1_CENTER = None
TH_SLOT_2_CENTER = None


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


def select_two_points(title, prompt):
    image = f.capture_screenshot()
    if image is None:
        f.log("[TH] No se pudo capturar screenshot para la calibración", color="red")
        return None
    image_h, image_w = image.shape[:2]
    display_scale = min(1.0, config_th.ZONE_WINDOW_MAX_WIDTH / image_w, config_th.ZONE_WINDOW_MAX_HEIGHT / image_h)
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


def inicializa():
    """Initialize TH runtime state needed by both CMD and GUI entry points."""
    coords.initialize()
    load_attack_config()


def menu():
    """Run the command-line calibration menu and return whether to start the bot."""
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


if __name__ == "__main__":
    inicializa()
    if menu():
        botstate.start()
        th_game_flow(build_context(DEFAULT_STRATEGY, EDGE_ZONE_POINTS, get_th_slot_position))
