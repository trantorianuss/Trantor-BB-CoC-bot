"""Screen detection for the Town Hall flow.

Kept separate from the BB detector so TH can evolve independently.
"""

import func as f


WAITING_NEXT = "waiting_next"
DETECTED_NEXT = "next"
WAITING_RETURN_HOME = "waiting_return_home"
DETECTED_RETURN_HOME = "return_home"

# Current provisional TH values. They can be moved to a TH layout/config file later.
NEXT_BUTTON_PIXEL = (960, 960)
NEXT_BUTTON_COLOR = (108, 187, 31)

# TODO: set these to the real Return Home button pixel/color.
RETURN_HOME_BUTTON_PIXEL = (0, 0)
RETURN_HOME_BUTTON_COLOR = (0, 0, 0)

PIXEL_TOLERANCE = 10


def is_pixel_visible(image, pixel, color):
    return f.check_pixel_from_image(
        image,
        pixel[0],
        pixel[1],
        color,
        tol=PIXEL_TOLERANCE,
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


def is_return_home_button_visible(image):
    """Return True when the TH Return Home button is detected."""
    if RETURN_HOME_BUTTON_PIXEL == (0, 0):
        return False

    result = is_pixel_visible(
        image,
        RETURN_HOME_BUTTON_PIXEL,
        RETURN_HOME_BUTTON_COLOR,
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

    if state == WAITING_RETURN_HOME and is_return_home_button_visible(image):
        return DETECTED_RETURN_HOME

    return None
