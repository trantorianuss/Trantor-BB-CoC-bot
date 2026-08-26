"""Game flow for the Town Hall (main village)."""

import random
import time

import func as f
import machine_state
import uiautomator_zoom

from TH_Bot import config_th, screen_detector_th, screen_layout_th
from TH_Bot.troops_th import deploy_troops


def th_game_flow(ctx):
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
        deployment_image = wait_for_next_screen(ctx)
        if deployment_image is None:
            machine_state.set_state(machine_state.IDLE)
            return
        f.log("[TH] Next detected -> waiting 1s before zoom")
        if not ctx.sleep_with_exit(1.0):
            machine_state.set_state(machine_state.IDLE)
            return
        uiautomator_zoom.zoom()
        deployment_image = f.capture_screenshot()
        ctx.save_deployment_debug(deployment_image)
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
    debug_path = f.save_image("th_elixir_check", image)
    f.log(f"[TH] Elixir check screenshot: {debug_path}", debug=True, category="detection")
    x, y = screen_layout_th.ELIXIR_FULL_PIXEL
    return f.check_pixel_from_image(image, x, y, screen_layout_th.ELIXIR_FULL_COLOR, tol=ctx.PIXEL_TOLERANCE)


def start_attack(ctx):
    machine_state.set_state(machine_state.WAITING_FIND)
    f.log("[TH] Starting attack")
    f.tap_scale(*screen_layout_th.ATTACK_BUTTON_1)
    if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
        return False
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return False
        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_FIND)
        if result == screen_detector_th.FIND_DETECTED:
            f.log("[TH] Find detected -> tapping")
            f.tap_scale(*screen_layout_th.FIND_BUTTON)
            if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
                return False
            f.tap_scale(*screen_layout_th.ATTACK_BUTTON_2)
            if not ctx.sleep_with_exit(ctx.ATTACK_BUTTON_DELAY):
                return False
            return True
        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Find... {int(elapsed)}s")
        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_next_screen(ctx):
    machine_state.set_state(machine_state.WAITING_NEXT)
    f.log("[TH] Waiting for Next before deployment")
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return None
        image = f.capture_screenshot()
        detected = screen_detector_th.is_next_button_visible(image)
        if detected:
            f.log(f"[TH] Next detected after {elapsed}s -> starting deployment")
            return image
        elapsed += ctx.SCREEN_DETECT_DELAY
        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return None


def wait_for_battle_end(ctx):
    machine_state.set_state(machine_state.WAITING_RESULT)
    f.log("[TH] Waiting for battle to finish")
    result = wait_for_battle_result(ctx)
    if result == screen_detector_th.CLAIM_REWARD_DETECTED:
        if not wait_for_claim_reward(ctx):
            return False
    elif result == screen_detector_th.RETURN_HOME_DETECTED:
        f.log("[TH] Return Home detected directly")
    else:
        return False
    return wait_for_return_home(ctx)


def wait_for_battle_result(ctx):
    """Wait until the post-battle screen shows either Claim Reward or Return Home."""
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return None
        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_RESULT)
        if result == screen_detector_th.CLAIM_REWARD_DETECTED:
            f.log("[TH] Claim Reward detected")
            return result
        if result == screen_detector_th.RETURN_HOME_DETECTED:
            f.log("[TH] Return Home detected")
            return result
        elapsed += config_th.BATTLE_RESULT_CHECK_DELAY
        if int(elapsed) % 10 == 0:
            f.log(f"[TH] Battle still running... {int(elapsed)}s")
        if not ctx.sleep_with_exit(config_th.BATTLE_RESULT_CHECK_DELAY):
            return None


def wait_for_claim_reward(ctx):
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
            f.tap_scale(*screen_layout_th.CLAIM_REWARD_BUTTON_PIXEL)
            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False
            for _ in range(3):
                if ctx.exit_requested():
                    return False
                x = random.randint(config_th.REWARD_TAP_CENTER[0] - config_th.REWARD_TAP_RADIUS, config_th.REWARD_TAP_CENTER[0] + config_th.REWARD_TAP_RADIUS)
                y = random.randint(config_th.REWARD_TAP_CENTER[1] - config_th.REWARD_TAP_RADIUS, config_th.REWARD_TAP_CENTER[1] + config_th.REWARD_TAP_RADIUS)
                f.log(f"[TH] Reward tap -> ({x}, {y})")
                f.tap_scale(x, y)
                if not ctx.sleep_with_exit(config_th.REWARD_TAP_DELAY):
                    return False
            return wait_for_claim_reward_continue(ctx)
        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Claim Reward... {int(elapsed)}s")
        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_claim_reward_continue(ctx):
    machine_state.set_state(machine_state.WAITING_RETURN_HOME)
    f.log("[TH] Waiting for Claim Reward Continue")
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return False
        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_REWARD_CONTINUE)
        if result == screen_detector_th.CLAIM_REWARD_CONTINUE_DETECTED:
            f.log(f"[TH] Claim Reward Continue detected after {elapsed}s -> tapping")
            f.tap_scale(*screen_layout_th.CLAIM_REWARD_CONTINUE_PIXEL)
            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False
            return True
        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Claim Reward Continue... {int(elapsed)}s")
        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False


def wait_for_return_home(ctx):
    machine_state.set_state(machine_state.WAITING_RETURN_HOME)
    f.log("[TH] Waiting for Return Home")
    elapsed = 0
    while True:
        if ctx.exit_requested():
            return False
        result = screen_detector_th.screen_detect(screen_detector_th.WAITING_RETURN_HOME)
        if result == screen_detector_th.RETURN_HOME_DETECTED:
            f.log(f"[TH] Return Home detected after {elapsed}s -> tapping")
            f.tap_scale(*screen_layout_th.RETURN_HOME_BUTTON_PIXEL)
            if not ctx.sleep_with_exit(ctx.AFTER_BATTLE_END_DELAY):
                return False
            return True
        elapsed += ctx.SCREEN_DETECT_DELAY
        if int(elapsed) % 5 == 0:
            f.log(f"[TH] Waiting for Return Home... {int(elapsed)}s")
        if not ctx.sleep_with_exit(ctx.SCREEN_DETECT_DELAY):
            return False
