"""Screen detection for the Town Hall flow.

Kept separate from the BB detector so TH can evolve independently.
"""

import func as f

from TH_Bot import config_th, screen_layout_th


WAITING_FIND = "waiting_find"
FIND_DETECTED = "find"

WAITING_RESULT = "waiting_result"
WAITING_NEXT = "waiting_next"  # compatibility with older calls
DETECTED_NEXT = "next"

WAITING_REWARD = "waiting_reward"
DETECTED_REWARD = "reward"
CLAIM_REWARD_DETECTED = DETECTED_REWARD

WAITING_REWARD_CONTINUE = "waiting_reward_continue"
DETECTED_REWARD_CONTINUE = "reward_continue"
CLAIM_REWARD_CONTINUE_DETECTED = DETECTED_REWARD_CONTINUE

WAITING_RETURN_HOME = "waiting_return_home"
DETECTED_RETURN_HOME = "return_home"
RETURN_HOME_DETECTED = DETECTED_RETURN_HOME


def is_pixel_visible(image, pixel, color):
    return f.check_pixel_from_image(image, pixel[0], pixel[1], color, tol=config_th.PIXEL_TOLERANCE)


def is_find_button_visible(image):
    result = is_pixel_visible(image, screen_layout_th.FIND_BUTTON, screen_layout_th.FIND_BUTTON_COLOR if hasattr(screen_layout_th, "FIND_BUTTON_COLOR") else (249, 173, 44))
    f.log(f"[TH DETECTOR] FIND pixel check -> {result}")
    return result


def is_next_button_visible(image):
    result = is_pixel_visible(image, screen_layout_th.NEXT_BUTTON_PIXEL, screen_layout_th.NEXT_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] NEXT pixel check -> {result}")
    return result


def is_claim_reward_button_visible(image):
    result = is_pixel_visible(image, screen_layout_th.CLAIM_REWARD_BUTTON_PIXEL, screen_layout_th.CLAIM_REWARD_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] Claim Reward pixel check -> {result}")
    return result


def is_claim_reward_continue_visible(image):
    result = is_pixel_visible(image, screen_layout_th.CLAIM_REWARD_CONTINUE_PIXEL, screen_layout_th.CLAIM_REWARD_CONTINUE_COLOR)
    f.log(f"[TH DETECTOR] Claim Reward Continue pixel check -> {result}")
    return result


def is_return_home_button_visible(image):
    result = is_pixel_visible(image, screen_layout_th.RETURN_HOME_BUTTON_PIXEL, screen_layout_th.RETURN_HOME_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] Return Home pixel check -> {result}")
    return result


def screen_detect(state):
    f.log(f"[TH DETECTOR] screen_detect(state={state}) -> capturing screenshot")
    image = f.capture_screenshot()
    f.log("[TH DETECTOR] screen_detect -> screenshot received")
    if image is None:
        f.log("[TH DETECTOR] screen_detect -> no screenshot", color="red")
        return None

    if state == WAITING_FIND and is_find_button_visible(image):
        return FIND_DETECTED

    if state == WAITING_RESULT:
        if is_claim_reward_button_visible(image):
            return DETECTED_REWARD
        if is_return_home_button_visible(image):
            return DETECTED_RETURN_HOME
        return None

    if state == WAITING_NEXT and is_next_button_visible(image):
        return DETECTED_NEXT
    if state == WAITING_REWARD and is_claim_reward_button_visible(image):
        return DETECTED_REWARD
    if state == WAITING_REWARD_CONTINUE and is_claim_reward_continue_visible(image):
        return DETECTED_REWARD_CONTINUE
    if state == WAITING_RETURN_HOME and is_return_home_button_visible(image):
        return DETECTED_RETURN_HOME
    return None