"""Screen detection for the Town Hall flow."""

import func as f

from TH_Bot import config_th


WAITING_FIND = "waiting_find"
FIND_DETECTED = "find"
WAITING_NEXT = "waiting_next"
DETECTED_NEXT = "next"
WAITING_REWARD = "waiting_reward"
DETECTED_REWARD = "reward"
WAITING_RETURN_HOME = "waiting_return_home"
DETECTED_RETURN_HOME = "return_home"

FIND_BUTTON_PIXEL = (160, 825)
FIND_BUTTON_COLOR = (249, 173, 44)


def is_pixel_visible(image, pixel, color):
    return f.check_pixel_from_image(image, pixel[0], pixel[1], color, tol=config_th.PIXEL_TOLERANCE)


def is_find_button_visible(image):
    result = is_pixel_visible(image, FIND_BUTTON_PIXEL, FIND_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] FIND pixel check -> {result}")
    return result


def is_next_button_visible(image=None):
    if image is None:
        image = f.capture_screenshot()
    if image is None:
        f.log("[TH DETECTOR] Screenshot unavailable", color="red")
        return False
    result = is_pixel_visible(image, (1630, 840), (230, 84, 13))
    f.log(f"[TH DETECTOR] NEXT pixel check -> {result}")
    return result


def is_claim_reward_button_visible(image):
    result = is_pixel_visible(image, config_th.CLAIM_REWARD_BUTTON_PIXEL, config_th.CLAIM_REWARD_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] Claim Reward pixel check -> {result}")
    return result


def is_return_home_button_visible(image):
    result = is_pixel_visible(image, config_th.RETURN_HOME_BUTTON_PIXEL, config_th.RETURN_HOME_BUTTON_COLOR)
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
    if state == WAITING_NEXT and is_next_button_visible(image):
        return DETECTED_NEXT
    if state == WAITING_REWARD and is_claim_reward_button_visible(image):
        return DETECTED_REWARD
    if state == WAITING_RETURN_HOME and is_return_home_button_visible(image):
        return DETECTED_RETURN_HOME
    return None
