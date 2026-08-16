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


# -----------------------------------------------------------------------------
# Temporary coordinates / values for the first TH test.
# Replace these with the real values once the flow is verified.
# -----------------------------------------------------------------------------

ELIXIR_FULL_PIXEL = (100, 100)       # TODO: real pixel position
ELIXIR_FULL_COLOR = (255, 0, 255)    # TODO: real RGB/BGR value used by func
BATTLE_END_PIXEL = (200, 200)        # TODO: real pixel position
BATTLE_END_COLOR = (0, 255, 0)       # TODO: real RGB/BGR value used by func

# Attack start sequence.
ATTACK_BUTTON_1 = (400, 800)         # TODO: real "Atacar" button coordinates
FIND_BUTTON = (600, 700)             # TODO: real "Find" button coordinates
ATTACK_BUTTON_2 = (800, 800)         # TODO: real second "Atacar" button coordinates

# Example troop deployment point near the edge of the main village.
DROP_POINT = (300, 500)              # TODO: real TH drop point

PIXEL_TOLERANCE = 10


# -----------------------------------------------------------------------------
# Debug: screenshot + mark the exact point that will be used by tap_scale
# -----------------------------------------------------------------------------

def debug_tap_scale(x, y, name, color):
    """Capture and mark the exact scaled tap point immediately before tapping.

    The input coordinates are the same base coordinates passed to tap_scale().
    The marker is converted with the same coords.scale() used by tap_scale(),
    so the saved screenshot shows where ADB will actually tap.
    """

    image = f.capture_screenshot()

    if image is None:
        f.log(f"[TH DEBUG] No se pudo capturar screenshot para {name}", color="red")
        f.tap_scale(x, y)
        return

    marked_x, marked_y = x, y

    if coords.REAL_W is not None and coords.REAL_H is not None:
        marked_x, marked_y = coords.scale(x, y)

    # OpenCV images are BGR. Draw a visible circle at the real tap position.
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
    f.log(
        f"[TH DEBUG] {name}: base=({x},{y}) -> screen=({marked_x},{marked_y}) -> {filename}"
    )

    # The actual tap is still performed by the normal tap_scale().
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
    debug_tap_scale(*ATTACK_BUTTON_1, "attack_1", (0, 0, 255))
    time.sleep(1)

    f.log("[TH] Pressing Find")
    debug_tap_scale(*FIND_BUTTON, "find", (0, 255, 0))
    time.sleep(5)

    f.log("[TH] Pressing second attack button")
    debug_tap_scale(*ATTACK_BUTTON_2, "attack_2", (255, 0, 0))
    time.sleep(2)


def deploy_troops():
    """Deploy a small test group at the edge of the TH village."""

    f.log(f"[TH] Deploying test troops at {DROP_POINT}")

    # TODO: select the required troop slot(s).
    # TODO: replace the test drop point with the real TH edge coordinates.
    f.tap_scale(*DROP_POINT)
    time.sleep(0.5)
    f.tap_scale(*DROP_POINT)
    time.sleep(0.5)
    f.tap_scale(*DROP_POINT)

    f.log("[TH] Test troop deployment finished")


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


# -----------------------------------------------------------------------------
# Command-line entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    th_game_flow()
