"""Game flow for the Town Hall (main village)."""

import random

import func as f
import machine_state

from TH_Bot import config_th, screen_detector_th
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
    machine_state.set_state(machine_state.WAITING_FIND)
    f.log("[TH] Starting attack")
    f.tap_scale(*ctx.ATTACK_BUTTON_1)
    if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
        return False

    elapsed = 0
    while True:
        if ctx.exit_requested():
            return False

        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_FIND)
        if result == screen_detector_th.FIND_DETECTED:
            f.log("[TH] Find detected -> tapping")
            f.tap_scale(*ctx.FIND_BUTTON)
            if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
                return False
            f.tap_scale(*ctx.ATTACK_BUTTON_2)
            if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
                return False
            return True

        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Find... {int(elapsed)}s")

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_battle_end(ctx):
    """Wait for battle result, optionally collect the event reward, then Return Home."""
    machine_state.set_state(machine_state.WAITING_RESULT)
    f.log("[TH] Waiting for battle to finish")

    if not wait_for_battle_result(ctx):
        return False

    if config_th.EVENT_REWARD_ENABLED:
        if not wait_for_claim_reward(ctx):
            return False

    return wait_for_return_home(ctx)


def wait_for_battle_result(ctx):
    """Wait until the battle result screen is detected."""
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return False

        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_NEXT)
        if result == screen_detector_th.RETURN_HOME_DETECTED:
            f.log("[TH] Return Home detected")
            return True
        if result == screen_detector_th.CLAIM_REWARD_DETECTED:
            f.log("[TH] Claim Reward detected")
            return True

        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 10 == 0:
            f.log(f"[TH] Battle still running... {int(elapsed)}s")

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_claim_reward(ctx):
    """Wait for, tap and complete the temporary event reward screen."""
    machine_state.set_state(machine_state.WAITING_REWARD)
    f.log("[TH] Waiting for Claim Reward")
    elapsed = 0

    while True:
        if ctx.exit_requested():
            return False

        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_REWARD)
        if result == screen_detector_th.CLAIM_REWARD_DETECTED:
            machine_state.set_state(machine_state.COLLECTING_REWARD)
            f.log(f"[TH] Claim Reward detected after {elapsed}s -> tapping")
            f.tap_scale(*config_th.CLAIM_REWARD_BUTTON_PIXEL)

            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False

            f.log("[TH] Claim Reward tapped -> performing 3 reward taps")
            for _ in range(3):
                if ctx.exit_requested():
                    return False

                x = random.randint(
                    config_th.REWARD_TAP_CENTER[0] - config_th.REWARD_TAP_RADIUS,
                    config_th.REWARD_TAP_CENTER[0] + config_th.REWARD_TAP_RADIUS,
                )
                y = random.randint(
                    config_th.REWARD_TAP_CENTER[1] - config_th.REWARD_TAP_RADIUS,
                    config_th.REWARD_TAP_CENTER[1] + config_th.REWARD_TAP_RADIUS,
                )
                f.log(f"[TH] Reward tap -> ({x}, {y})")
                f.tap_scale(x, y)
                if not ctx.sleep_with_exit(config_th.REWARD_TAP_DELAY):
                    return False

            return True

        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Claim Reward... {int(elapsed)}s")

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_return_home(ctx):
    """Wait for and tap the Return Home button."""
    machine_state.set_state(machine_state.WAITING_RETURN_HOME)
    f.log("[TH] Waiting for Return Home")
    elapsed = 0

    while True:
        if ctx.exit_requested():
            return False

        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_RETURN_HOME)
        if result == screen_detector_th.RETURN_HOME_DETECTED:
            f.log(f"[TH] Return Home detected after {elapsed}s -> tapping")
            f.tap_scale(*config_th.RETURN_HOME_BUTTON_PIXEL)
            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False
            return True

        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Return Home... {int(elapsed)}s")

        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False
