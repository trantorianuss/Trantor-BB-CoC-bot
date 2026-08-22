"""Screen detection for the Town Hall flow.

Kept separate from the BB detector so TH can evolve independently.
"""

import func as f


WAITING_NEXT = "waiting_next"
DETECTED_NEXT = "next"

# Current provisional TH values. They can be moved to a TH layout/config file later.
NEXT_BUTTON_PIXEL = (960, 960)
NEXT_BUTTON_COLOR = (108, 187, 31)
PIXEL_TOLERANCE = 10


def is_next_button_visible(image=None):
    """Return True when the TH NEXT button is detected."""
    if image is None:
        f.log("[TH DETECTOR] Capturing screenshot...")
        image = f.capture_screenshot()
        f.log("[TH DETECTOR] Screenshot received")

    if image is None:
        f.log("[TH DETECTOR] Screenshot unavailable", color="red")
        return False

    result = f.check_pixel_from_image(
        image,
        NEXT_BUTTON_PIXEL[0],
        NEXT_BUTTON_PIXEL[1],
        NEXT_BUTTON_COLOR,
        tol=PIXEL_TOLERANCE,
    )
    f.log(f"[TH DETECTOR] NEXT pixel check -> {result}")
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

    return None
