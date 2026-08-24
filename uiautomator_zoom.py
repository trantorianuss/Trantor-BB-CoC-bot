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
        (1140, 340),  # P1: dedo 1 inicial
        ( 140, 340),  # P2: dedo 2 inicial
        ( 940, 340),  # P3: dedo 1 final
        ( 340, 340),  # P4: dedo 2 final

        steps=20,
    )

    log("[ZOOM] Zoom gesture completed")

