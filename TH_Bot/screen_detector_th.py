"""Screen detection for the Town Hall flow.

Kept separate from the BB detector so TH can evolve independently.
"""

import func as f

from TH_Bot import config_th


WAITING_NEXT = "waiting_next"
DETECTED_NEXT = "next"
WAITING_REWARD = "waiting_reward"
DETECTED_REWARD = "reward"
WAITING_RETURN_HOME = "waiting_return_home"
DETECTED_RETURN_HOME = "return_home"

# Current provisional TH values.
NEXT_BUTTON_PIXEL = (1630, 840)
NEXT_BUTTON_COLOR = (230, 84, 13)


def is_pixel_visible(image, pixel, color):
    return f.check_pixel_from_image(
        image,
        pixel[0],
        pixel[1],
        color,
        tol=config_th.PIXEL_TOLERANCE,
    )


def is_next_button_visible(image=None):
    """Return True when the TH NEXT button is detected."""
    if image is None:
        f.log("[TH DETECTOR] Capturing screenshot...")
        image = f.capture_screenshot()
        f.log("[TH DETECTOR] Screenshot received")

    if image is None:
        f.log("[TH DETECTOR] Screenshot unavailable", color="red")
        return False

    result = is_pixel_visible(image, NEXT_BUTTON_PIXEL, NEXT_BUTTON_COLOR)
    f.log(f"[TH DETECTOR] NEXT pixel check -> {result}")
    return result


def is_claim_reward_button_visible(image):
    """Return True when the temporary event Claim Reward button is detected."""
    result = is_pixel_visible(
        image,
        config_th.CLAIM_REWARD_BUTTON_PIXEL,
        config_th.CLAIM_REWARD_BUTTON_COLOR,
    )
    f.log(f"[TH DETECTOR] Claim Reward pixel check -> {result}")
    return result


def is_return_home_button_visible(image):
    """Return True when the TH Return Home button is detected."""
    result = is_pixel_visible(
        image,
        config_th.RETURN_HOME_BUTTON_PIXEL,
        config_th.RETURN_HOME_BUTTON_COLOR,
    )
    f.log(f"[TH DETECTOR] Return Home pixel check -> {result}")
    return result


def screen_detect(state):
    """Detect the relevant TH screen element for the requested state."""
    f.log(f"[TH DETECTOR] screen_detect(state={state}) -> capturing screenshot")
    image = f.capture_screenshot()
    f.log("[TH DETECTOR] screen_detect -> screenshot received")

    if image is None:
        f.log("[TH DETECTOR] screen_detect -> no screenshot", color="red")
        return None

    if state == WAITING_NEXT and is_next_button_visible(image):
        return DETECTED_NEXT

    if state == WAITING_REWARD and is_claim_reward_button_visible(image):
        return DETECTED_REWARD

    if state == WAITING_RETURN_HOME and is_return_home_button_visible(image):
        return DETECTED_RETURN_HOME

    return None
