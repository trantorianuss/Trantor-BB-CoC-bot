"""
Standalone game flow for the Town Hall (main village).

This file is intentionally independent from gameflow.py / Builder Base flow.
It can be executed directly from the command line:

    python main_th.py

Only low-level functionality is reused from the application (currently func.py
for screenshots, pixel checks and taps). The TH flow itself lives here.
"""

import time

import cv2

import func as f
import coords
import screen_layout as layout


# -----------------------------------------------------------------------------
# Temporary coordinates / values for the first TH test.
# Replace these with the real values once the flow is verified.
# -----------------------------------------------------------------------------

ELIXIR_FULL_PIXEL = (100, 100)       # TODO: real pixel position
ELIXIR_FULL_COLOR = (255, 0, 255)    # TODO: real RGB/BGR value used by func
BATTLE_END_PIXEL = (200, 200)        # TODO: real pixel position
BATTLE_END_COLOR = (0, 255, 0)       # TODO: real RGB/BGR value used by func

# Attack start sequence.
ATTACK_BUTTON_1 = (125, 995)         # TODO: real "Atacar" button coordinates
FIND_BUTTON = (320, 800)             # TODO: real "Find" button coordinates
ATTACK_BUTTON_2 = (1700, 960)        # TODO: real second "Atacar" button coordinates

# Deployment sequence.
# Each entry is: (slot, number of troops, drop area, delay).
# delay is the wait BEFORE executing that action.
# count=0 means: press the slot only, without dropping troops.
# Available drop areas for now: "edge" and "center".
DEPLOY_SEQUENCE = [
    # Troops
    (1, 3, "edge", 0.1),
    (2, 4, "edge", 0.1),
    (3, 5, "edge", 0.1),

    # Heroes: select/deploy only
    (4, 0, "edge", 0.1),
    (5, 0, "edge", 0.1),

    # Hero abilities: select slot only, later in the attack
    (4, 0, "edge", 5.0),
    (5, 0, "edge", 1.0),

    # Spell / special slot
    (6, 2, "center", 3.0),
    (6, 1, "center", 2.0),
]

# Example troop deployment points.
# TODO: replace these with the real TH drop coordinates.
DROP_POINTS_EDGE = [
    (80, 444),
    (120, 444),
    (160, 444),
]
DROP_POINT_CENTER = (960, 540)

PIXEL_TOLERANCE = 10


# -----------------------------------------------------------------------------
# Debug: screenshot + mark the exact point that will be used by tap_scale
# -----------------------------------------------------------------------------

def debug_tap_scale(x, y, name, color):
    """Capture and mark the exact scaled tap point immediately before tapping."""

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
    center_x = image_w // 2
    center_y = image_h // 2
    cv2.circle(image, (center_x, center_y), 50, (0, 255, 255), 5)

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
# TH game flow
# -----------------------------------------------------------------------------

def th_game_flow():
    """Run the basic farming loop for the main village."""

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
    """Return True when the configured elixir-full pixel is detected."""

    image = f.capture_screenshot()

    x, y = ELIXIR_FULL_PIXEL
    return f.check_pixel_from_image(
        image,
        x,
        y,
        ELIXIR_FULL_COLOR,
        tol=PIXEL_TOLERANCE,
    )


def start_attack():
    """Start a TH attack through the three-button sequence."""

    f.log("[TH] Pressing first attack button")
    f.tap_scale(*ATTACK_BUTTON_1)
    time.sleep(1)

    f.log("[TH] Pressing Find")
    f.tap_scale(*FIND_BUTTON)
    time.sleep(5)

    f.log("[TH] Pressing second attack button")
    f.tap_scale(*ATTACK_BUTTON_2)
    time.sleep(2)


def slot(n):
    """Select troop slot n using the same layout calculation as BB."""

    x = layout.FIRST_SLOT_CENTER[0] + layout.SLOT_STEP * (n - 1)
    y = layout.FIRST_SLOT_CENTER[1]
    f.tap_scale(x, y)


def deploy_troops():
    """Execute the configured deployment sequence."""

    edge_index = 0

    for slot_number, count, drop_area, delay in DEPLOY_SEQUENCE:
        if delay > 0:
            time.sleep(delay)

        f.log(
            f"[TH] Slot {slot_number} | cantidad={count} | "
            f"zona={drop_area} | delay={delay}s"
        )

        slot(slot_number)

        if count == 0:
            continue

        if drop_area == "center":
            drop_points = [DROP_POINT_CENTER]
        elif drop_area == "edge":
            drop_points = DROP_POINTS_EDGE
        else:
            f.log(f"[TH] Zona de despliegue desconocida: {drop_area}", color="red")
            continue

        for _ in range(count):
            if drop_area == "edge":
                drop_point = drop_points[edge_index % len(drop_points)]
                edge_index += 1
            else:
                drop_point = drop_points[0]

            f.tap_scale(*drop_point)
            time.sleep(0.5)

    f.log("[TH] Despliegue terminado")


def wait_for_battle_end():
    """Wait until the battle-end pixel is detected."""

    f.log("[TH] Waiting for battle to finish")

    while True:
        image = f.capture_screenshot()
        x, y = BATTLE_END_PIXEL

        if f.check_pixel_from_image(
            image,
            x,
            y,
            BATTLE_END_COLOR,
            tol=PIXEL_TOLERANCE,
        ):
            f.log("[TH] Battle finished")
            return True

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


# -----------------------------------------------------------------------------
# Command-line entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    initialize_coords()
    th_game_flow()
