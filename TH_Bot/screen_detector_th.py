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
        image = f.capture_screenshot()

    return f.check_pixel_from_image(
        image,
        NEXT_BUTTON_PIXEL[0],
        NEXT_BUTTON_PIXEL[1],
        NEXT_BUTTON_COLOR,
        tol=PIXEL_TOLERANCE,
    )


def screen_detect(state):
    """Detect the relevant TH screen element for the requested state."""
    image = f.capture_screenshot()

    if state == WAITING_NEXT and is_next_button_visible(image):
        return DETECTED_NEXT

    return None
