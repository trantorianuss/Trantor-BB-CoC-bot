# file to store the screen layout of the game, so that it can be used in other files without having to redefine it each time

# screen_layout.py

# removed con el drop analizer
# DROP_AREA = (1400, 500, 1600, 700)  # area where troops are dropped during an attack
# ATTACK_DROP = (1500, 600)  # coordinates for the drop point during an attack, used for analyzing the drop point and visualizing it on the screenshot

# Actual slot/drop constants used by attacks.py
FIRST_SLOT_CENTER = (225, 925)
SLOT_STEP = 150

DROP_POINT = (1535, 585)  ## OLD BB code, to review

# Elixir level reference pixels. The points are ordered from full to low.
# The full point is known; the remaining X coordinates are intentionally pending.
ELIXIR_FULL_PIXEL = (1525, 179)
ELIXIR_75_PIXEL = (1605, 179)
ELIXIR_50_PIXEL = (1685, 179)
ELIXIR_25_PIXEL = (1765, 179)
ELIXIR_COLOR = (121, 69, 197)

# Battle UI detection reference
SURRENDER_PIXEL = (48, 737)
SURRENDER_COLOR = (247, 93, 95)
BATTLE_END_PIXEL = (888, 900)
BATTLE_END_COLOR = (180, 230, 125)
PIXEL_TOLERANCE = 20

# Initial screen detector reference for the FIND button.
# These are deliberately provisional values and must be calibrated.
FIND_BUTTON_PIXEL = (1400, 750)
FIND_BUTTON_COLOR = (139, 212, 58)

# Daily star bonus screen detection.
# Provisional values: replace with measured coordinates/color from the game.
STAR_BONUS_PIXEL = (960, 500)
STAR_BONUS_COLOR = (255, 255, 255)
# Provisional point inside the button used to dismiss the bonus window.
STAR_BONUS_BUTTON = (960, 850)




"""
# below, examples of coordinates for various buttons and slots in the game
# not the real coordinates, just examples. You will need to adjust these values based on your screen resolution and the actual positions of the buttons in your game.


SURRENDER_BUTTON = (1785, 90)

RETURN_HOME = (960, 915)

SLOT_1 = (75, 925)
SLOT_2 = (225, 925)

MATCH_BUTTON = (1700, 930)

SURRENDER_RED_PIXEL = (1770, 80)

BOAT_SEARCH_REGION = (
    1300,
    0,
    620,
    450
)

"""
