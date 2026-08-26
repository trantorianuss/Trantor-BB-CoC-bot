"""TH-specific runtime configuration."""

# Temporary event flow switch.
EVENT_REWARD_ENABLED = True

# Attack / flow timing.
ATTACK_BUTTON_DELAY = 0.5
BETWEEN_TROOPS_DELAY = 0
AFTER_BATTLE_END_DELAY = 3.0
SCREEN_DETECT_DELAY = 2
BATTLE_RESULT_CHECK_DELAY = 5
EXIT_POLL_INTERVAL = 0.05

# Deployment behaviour.
MULTITAP_MAX = 4

# Calibration/debug UI limits.
ZONE_WINDOW_MAX_WIDTH = 1000
ZONE_WINDOW_MAX_HEIGHT = 700

# Persistent TH attack calibration file.
# Kept as a filename here; main_th resolves it relative to the TH package.
ATTACK_CONFIG_FILENAME = "attack_th.json"

# After Claim Reward, the game shows a reward screen that accepts three taps
# around the center. The exact point is randomized within this radius.
REWARD_TAP_CENTER = (640, 640)
REWARD_TAP_RADIUS = 100
REWARD_TAP_DELAY = 0.3

PIXEL_TOLERANCE = 10
