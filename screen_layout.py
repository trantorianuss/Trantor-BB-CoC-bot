# file to store the screen layout of the game, so that it can be used in other files without having to redefine it each time

# screen_layout.py

DROP_AREA = (1400, 500, 1600, 700)  # area where troops are dropped during an attack
ATTACK_DROP = (1500, 600)  # coordinates for the drop point during an attack, used for analyzing the drop point and visualizing it on the screenshot


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