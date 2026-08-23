"""Temporary TH-specific runtime configuration.

Event reward handling is disabled by default. Enable it while the event is
active, then turn it off again when the normal post-battle flow is restored.
"""

# Temporary event flow switch.
EVENT_REWARD_ENABLED = True

# After Claim Reward, the game shows a reward screen that accepts three taps
# around the center. The exact point is randomized within this radius.
REWARD_TAP_CENTER = (640, 640)
REWARD_TAP_RADIUS = 100
REWARD_TAP_DELAY = 0.3

PIXEL_TOLERANCE = 10
