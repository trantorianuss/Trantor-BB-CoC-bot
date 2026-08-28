import time
print(f">>> gameflow.py  starting [{time.perf_counter():.3f}]")

import time as t
import func as f
import attacks as a
#import elixir_cart
import cart_calibration

import botstate
import machine_state

import random
from func import tap_scale
import settings
import screen_layout
import screen_detector


def tap_surrender_button():
    while True:
        if not botstate.should_run():
            f.log("[GameFlow] Bot stopped. Cancelling surrender button wait.")
            return False

        detected = screen_detector.screen_detect(screen_detector.WAITING_SURRENDER)

        if detected == screen_detector.DETECTED_SURRENDER:
            f.log(f"SURRENDER ready: {detected}", debug=True, color="magenta", category="detection")
            x = random.randint(24, 246)
            y = random.randint(721, 780)
            tap_scale(x, y)
            return True

        if detected == screen_detector.DETECTED_FIND:
            f.log("Warning: Find button not expected", color="red", category="detection")

        f.log("Surrender button not visible. Retrying in 10 seconds.")
        t.sleep(10)


def confirm_surrender():
    x = random.randint(1014, 1323)
    y = random.randint(643, 752)
    tap_scale(x, y)


def handle_star_bonus():
    """Handle the optional daily star bonus window after returning Home."""
    image = f.capture_screenshot()

    if screen_detector.is_star_bonus_visible(image):
        f.log("[GameFlow] Star Bonus detected. Pressing button to continue.")
        x, y = screen_layout.STAR_BONUS_BUTTON
        tap_scale(x, y)
        t.sleep(1)
        return True

    f.log("[GameFlow] No Star Bonus. Continuing.", debug=True)
    return False


def tap_return_home():
    x = random.randint(850, 1065)
    y = random.randint(875, 950)
    tap_scale(x, y)


def collect_pink_elixir():
    f.log("[Elixir] Moving camera and opening Cart…")
    if not open_cart(debug=True):
        f.log("[Elixir] Cart not found; collection tap skipped.")
        return
    f.log("[Elixir] Pressing Collect button…")
    f.log("[Elixir] AQUI L TAP COMMENTED.")
    f.human_tap_scale(1301, 871, 1510, 944)
    f.log("[Elixir] Reward collected.")
    t.sleep(5)
    f.log("[Elixir] Closing window.")
    f.human_tap_scale(1583, 60, 1630, 132)
    f.log("[Elixir] Reward collected.")
    t.sleep(5)
    return True


def open_cart(debug=False):
    xi = 1850
    yi = 350
    dx, dy = settings.swipe_dx, settings.swipe_dy
    f.wait_for_stable_screen()
    f.stable_swipe(xi, yi, xi + dx, yi + dy, 1500)
    screenshot_path = f.screenshot("cart_search")
    position = cart_calibration.locate_cart(screenshot_path, debug=debug)
    if position is None:
        f.log("[Elixir] Cart not found.")
        return False
    x, y = position
    f.log(f"TAP REAL EN: {x}, {y}")
    f.tap_absolute(x, y)
    t.sleep(0.4)
    return True


def try_collect_pink_elixir():
    f.log("[Elixir] Trying to collect pink elixir…")
    if collect_pink_elixir():
        f.log("[Elixir] Pink elixir collected successfully.")
        return True
    f.log("[Elixir] No pink elixir ready to collect.")
    return False


def get_elixir_level():
    levels = (
        ("FULL", screen_layout.ELIXIR_FULL_PIXEL),
        ("75%", screen_layout.ELIXIR_75_PIXEL),
        ("50%", screen_layout.ELIXIR_50_PIXEL),
        ("25%", screen_layout.ELIXIR_25_PIXEL),
    )
    f.log("[Elixir] Searching for Elixir level.", debug=True)
    image = f.capture_screenshot()

    for level, (x, y) in levels:
        f.log(f"[Elixir] Checking level: {level} (pos={x},{y})", debug=True)
        if x is None or y is None:
            continue
        if f.check_pixel_from_image(
            image,
            x,
            y,
            screen_layout.ELIXIR_COLOR,
            tol=screen_layout.PIXEL_TOLERANCE,
        ):
            f.log(f"[Elixir] Level detected: {level} (pos={x},{y})")
            return level

    screenshot_path = f.screenshot("elixir_detection_failed")
    f.log(
        f"[Elixir] No level detected. Screenshot saved: {screenshot_path}",
        color="red",
        category="detection",
    )
    return None


def get_gold_level():
    """Detect the current gold level using the four configured pixel points."""
    levels = (
        ("FULL", screen_layout.GOLD_FULL_PIXEL),
        ("75%", screen_layout.GOLD_75_PIXEL),
        ("50%", screen_layout.GOLD_50_PIXEL),
        ("25%", screen_layout.GOLD_25_PIXEL),
    )
    f.log("[Gold] Searching for Gold level.", debug=True)
    image = f.capture_screenshot()

    for level, (x, y) in levels:
        f.log(f"[Gold] Checking level: {level} (pos={x},{y})", debug=True)
        if x is None or y is None:
            continue
        if f.check_pixel_from_image(
            image,
            x,
            y,
            screen_layout.GOLD_COLOR,
            tol=screen_layout.PIXEL_TOLERANCE,
        ):
            f.log(f"[Gold] Level detected: {level} (pos={x},{y})")
            return level

    screenshot_path = f.screenshot("gold_detection_failed")
    f.log(
        f"[Gold] No level detected. Screenshot saved: {screenshot_path}",
        color="red",
        category="detection",
    )
    return None


def is_elixir_full():
    f.log("[Elixir] Checking if Elixir is full.")
    return get_elixir_level() == "FULL"


def resources_full(attack_mode):
    """Return True when the resources required by the selected mode are full."""
    elixir_full = is_elixir_full()

    if attack_mode == "surrender":
        return elixir_full

    gold_full = get_gold_level() == "FULL"
    f.log(
        f"[Resources] Full Attack: Elixir FULL={elixir_full}, Gold FULL={gold_full}",
        debug=True,
    )
    return elixir_full and gold_full


def find_match():
    f.log("[GameFlow] Searching for village…")
    f.log("Pressing Attack", category="Find")
    tap_scale(100, 1000)
    machine_state.set_state(machine_state.WAITING_FIND)
    while botstate.should_run():
        find_ready = screen_detector.is_find_button_visible()
        f.log(f"FIND ready: {find_ready}", debug=True, color="magenta", category="detection")
        if find_ready:
            f.log("Pressing Find")
            tap_scale(1375, 650)
            t.sleep(5)
            machine_state.set_state(machine_state.ATTACKING)
            return True
        f.log("Warning: FIND button not detected. Waiting…", color="red", category="detection")
        t.sleep(1)
    f.log("[GameFlow] Bot stopped while waiting for FIND.")
    return False


def wait_for_battle_end():
    f.log("Waiting for battle to end…")
    while botstate.should_run():
        x, y = screen_layout.BATTLE_END_PIXEL
        if f.check_pixel(x, y, screen_layout.BATTLE_END_COLOR, tol=screen_layout.PIXEL_TOLERANCE):
            f.log("Battle ended")
            return True
        t.sleep(1)
    f.log("Bot stopped while waiting for battle to end.")
    return False


def collect_loot():
    f.log("Collecting loot…")
    f.tap_scale(950, 900)
    t.sleep(2)
    f.swipe1()
    t.sleep(1)
    f.tap_scale(871, 521)
    t.sleep(1)
    f.tap_scale(1400, 920)
    t.sleep(1)
    f.tap_scale(1600, 100)
    t.sleep(1)
    f.log("Loot collected")


def perform_attack(attempt_label, attack_mode, total_attacks=None):
    if total_attacks is not None and isinstance(attempt_label, int):
        f.log(f">>> Attack {attempt_label} of {total_attacks} ({attack_mode}) <<<")
    else:
        f.log(f">>> Extra attack ({attack_mode}) <<<")

    if not find_match():
        return False
    t.sleep(2)
    a.BBFarm()

    if attack_mode == "surrender":
        if not tap_surrender_button():
            return False
        t.sleep(1)
        confirm_surrender()
        t.sleep(1)
    else:
        if not wait_for_battle_end():
            return False

    f.log(">>> Return Home <<<")
    tap_return_home()
    t.sleep(1)
    handle_star_bonus()
    return True


def farm_until_full(attacks_per_cycle=None):
    # Capture the selected attack mode once for the whole farming cycle.
    attack_mode = settings.get_attack_mode()
    f.log(f">>> Attack mode fixed for cycle: {attack_mode} <<<")

    while not resources_full(attack_mode):
        cycle_attacks = settings.get_attacks_per_cycle() if attacks_per_cycle is None else attacks_per_cycle
        f.log(f">>> New cycle of {cycle_attacks} attacks <<<")
        for i in range(cycle_attacks):
            if not botstate.should_run():
                return False
            perform_attack(i + 1, attack_mode, cycle_attacks)
        if try_collect_pink_elixir():
            f.log("Pink elixir collected. Starting new attack cycle.")
            continue
        f.log("No pink elixir available. Starting extra attacks...")
        while True:
            if not botstate.should_run():
                return False
            perform_attack("extra", attack_mode)
            if try_collect_pink_elixir():
                f.log("Pink elixir collected after extra attack. Starting new cycle.")
                break
            f.log("Pink elixir still unavailable. Starting another extra attack...")
    f.log(">>> Required resources are full. End of cycle. <<<")
    return True
