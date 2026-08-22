"""Game flow for the Town Hall (main village).

The calibration/menu remains in main_th.py. Attack execution lives here so the
TH flow can later grow into a proper state machine without growing main_th.py.
"""

import random
from concurrent.futures import ThreadPoolExecutor

import coords
import func as f

from TH_Bot import screen_detector_th


def th_game_flow(ctx):
    """Run the TH farming loop using the runtime context supplied by main_th."""
    f.log("[TH] Starting TH game flow")

    while not is_elixir_full(ctx):
        if ctx.exit_requested():
            return

        f.log("[TH] Elixir not full -> starting attack")
        if not start_attack(ctx):
            return

        ctx.save_deployment_debug()

        if not deploy_troops(ctx):
            return

        if not wait_for_battle_end(ctx):
            f.log("[TH] Battle did not finish. Leaving flow.")
            return

        f.log("[TH] Battle finished -> checking elixir again")

    f.log("[TH] Elixir is full -> flow finished")


def is_elixir_full(ctx):
    image = f.capture_screenshot()
    x, y = ctx.ELIXIR_FULL_PIXEL
    return f.check_pixel_from_image(
        image,
        x,
        y,
        ctx.ELIXIR_FULL_COLOR,
        tol=ctx.PIXEL_TOLERANCE,
    )


def start_attack(ctx):
    f.log("[TH] Pressing first attack button")
    f.tap_scale(*ctx.ATTACK_BUTTON_1)
    if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
        return False

    f.log("[TH] Pressing Find")
    f.tap_scale(*ctx.FIND_BUTTON)
    if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
        return False

    f.log("[TH] Pressing second attack button")
    f.tap_scale(*ctx.ATTACK_BUTTON_2)

    f.log("[TH] Waiting for NEXT button")
    while True:
        if ctx.exit_requested():
            return False

        if screen_detector_th.screen_detect(screen_detector_th.WAITING_NEXT) == screen_detector_th.DETECTED_NEXT:
            f.log("[TH] NEXT button detected -> attack screen ready")
            return True

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def slot(ctx, n):
    x, y = ctx.get_th_slot_position(n)
    f.tap_scale(x, y)


def multi_tap_scale(points, ctx):
    if not points:
        return True
    if ctx.exit_requested():
        return False

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

    return not ctx.exit_requested()


def random_drop_point(ctx):
    center_x, center_y = ctx.DROP_DIAMOND_CENTER
    half_width = ctx.DROP_DIAMOND_HALF_WIDTH
    half_height = ctx.DROP_DIAMOND_HALF_HEIGHT

    while True:
        x = random.uniform(center_x - half_width, center_x + half_width)
        y = random.uniform(center_y - half_height, center_y + half_height)
        if abs(x - center_x) / half_width + abs(y - center_y) / half_height <= 1:
            return int(x), int(y)


def deploy_troops(ctx):
    edge_index = 0

    for slot_number, count, drop_area, delay, use_multitap in ctx.DEPLOY_SEQUENCE:
        if ctx.exit_requested():
            return False

        if delay > 0 and not ctx.sleep_with_exit(delay):
            return False

        f.log(
            f"[TH] Slot {slot_number} | cantidad={count} | "
            f"zona={drop_area} | delay={delay}s | multitap={use_multitap}"
        )
        slot(ctx, slot_number)

        if count == 0:
            continue

        if drop_area == "center":
            drop_points = [ctx.DROP_POINT_CENTER]
        elif drop_area == "edge":
            drop_points = ctx.EDGE_ZONE_POINTS or ctx.DROP_POINTS_EDGE
        elif drop_area == "random":
            drop_points = None
        else:
            f.log(f"[TH] Zona de despliegue desconocida: {drop_area}", color="red")
            continue

        points_to_drop = []
        for _ in range(count):
            if ctx.exit_requested():
                return False

            if drop_area == "edge":
                drop_point = drop_points[edge_index % len(drop_points)]
                edge_index += 1
            elif drop_area == "random":
                drop_point = random_drop_point(ctx)
                f.log(f"[TH] Random drop -> {drop_point}")
            else:
                drop_point = drop_points[0]

            points_to_drop.append(drop_point)

        if use_multitap:
            for start in range(0, len(points_to_drop), ctx.MULTITAP_MAX):
                batch = points_to_drop[start:start + ctx.MULTITAP_MAX]
                if not multi_tap_scale(batch, ctx):
                    return False
        else:
            for point in points_to_drop:
                if ctx.exit_requested():
                    return False
                f.tap_scale(*point)
                if not ctx.sleep_with_exit(ctx.BETWEEN_TROOPS_DELAY):
                    return False

    f.log("[TH] Despliegue terminado")
    return True


def wait_for_battle_end(ctx):
    """Wait for the battle to finish, then detect and tap Return Home."""
    f.log("[TH] Waiting for battle to finish -> waiting for Return Home")
    elapsed = 0

    while True:
        if ctx.exit_requested():
            return False

        result = screen_detector_th.screen_detect(
            screen_detector_th.WAITING_RETURN_HOME
        )
        if result == screen_detector_th.DETECTED_RETURN_HOME:
            f.log(f"[TH] Return Home detected after {elapsed}s -> tapping")
            f.tap_scale(*screen_detector_th.RETURN_HOME_BUTTON_PIXEL)
            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False
            f.log("[TH] Return Home tapped -> back to main screen")
            return True

        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Battle still running... {int(elapsed)}s")

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False
