"""uiautomator2 helper for the CoC attack zoom."""

import uiautomator2 as u2

import config
from logger import log

_DEVICE = None
_STAGE = None


def zoom():
    """Apply the tested two-finger zoom gesture to the CoC stage."""
    global _DEVICE, _STAGE

    if _STAGE is None:
        log("[ZOOM] Connecting to uiautomator2")
        _DEVICE = u2.connect(config.ADB_PORT)
        _STAGE = _DEVICE(resourceId="com.supercell.clashofclans:id/stage")
        log("[ZOOM] CoC stage initialized")

    _STAGE.gesture(
        (750, 457),
        (509, 698),
        (650, 520),
        (600, 620),
        steps=20,
    )

    log("[ZOOM] Zoom gesture completed")
