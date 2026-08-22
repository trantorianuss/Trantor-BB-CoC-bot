"""Game flow for the Town Hall (main village)."""

import func as f
import machine_state

from TH_Bot import screen_detector_th
from TH_Bot.troops_th import deploy_troops


def th_game_flow(ctx):
    """Run the TH farming loop using the runtime context supplied by main_th."""
    f.log("[TH] Starting TH game flow")
    machine_state.set_state(machine_state.IDLE)

    while not is_elixir_full(ctx):
        if ctx.exit_requested():
            machine_state.set_state(machine_state.IDLE)
            return

        f.log("[TH] Elixir not full -> starting attack")
        if not start_attack(ctx):
            machine_state.set_state(machine_state.IDLE)
            return

        machine_state.set_state(machine_state.ATTACKING)
        ctx.save_deployment_debug()

        if not deploy_troops(ctx):
            machine_state.set_state(machine_state.IDLE)
            return

        if not wait_for_battle_end(ctx):
            f.log("[TH] Battle did not finish. Leaving flow.")
            machine_state.set_state(machine_state.IDLE)
            return

        f.log("[TH] Battle finished -> checking elixir again")

    machine_state.set_state(machine_state.IDLE)
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
    machine_state.set_state(machine_state.STARTING)

    f.log("[TH] Pressing first attack button")
    f.tap_scale(*ctx.ATTACK_BUTTON_1)
    if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
        return False

    machine_state.set_state(machine_state.WAITING_FIND)
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


def wait_for_battle_end(ctx):
    """Wait for the battle to finish, then detect and tap Return Home."""
    machine_state.set_state(machine_state.WAITING_RESULT)
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
