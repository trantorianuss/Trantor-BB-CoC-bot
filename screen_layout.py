# file to store the screen layout of the game, so that it can be used in other files without having to redefine it each time

# Actual slot/drop constants used by attacks.py
FIRST_SLOT_CENTER = (225, 925)
SLOT_STEP = 150
DROP_POINT = (1535, 585)  ## OLD BB code, to review

# BB main attack/search buttons
ATTACK_BUTTON = (100, 1000)
FIND_BUTTON = (1375, 650)
RETURN_HOME_BUTTON = (960, 915)

# Elixir level reference pixels.
ELIXIR_FULL_PIXEL = (1525, 183)
ELIXIR_75_PIXEL = (1605, 183)
ELIXIR_50_PIXEL = (1685, 183)
ELIXIR_25_PIXEL = (1765, 183)
ELIXIR_COLOR = (121, 69, 197)

GOLD_FULL_PIXEL = (1525, 80)
GOLD_75_PIXEL = (1605, 80)
GOLD_50_PIXEL = (1685, 80)
GOLD_25_PIXEL = (1765, 80)
GOLD_COLOR = (231, 192, 13)

# Battle UI detection reference
SURRENDER_PIXEL = (48, 737)
SURRENDER_COLOR = (247, 93, 95)
BATTLE_END_PIXEL = (888, 900)
BATTLE_END_COLOR = (180, 230, 125)
PIXEL_TOLERANCE = 20

# Initial screen detector reference for the FIND button.
FIND_BUTTON_PIXEL = (1400, 750)
FIND_BUTTON_COLOR = (139, 212, 58)

# Battle screen detection reference.
# Calibrate from a pixel inside the Attacker / Defender text after FIND.
ATTACK_SCREEN_PIXEL = (104, 33)
ATTACK_SCREEN_COLOR = (225, 225, 153)

# BB Home screen detection reference.
BB_HOME_PIXEL = (109, 28)
BB_HOME_COLOR = (63, 197, 243)

# Daily star bonus screen detection.
STAR_BONUS_PIXEL = (855, 810)
STAR_BONUS_COLOR = (187, 233, 135)
STAR_BONUS_BUTTON = (855, 810)
