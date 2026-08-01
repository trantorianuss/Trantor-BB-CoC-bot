# ------------------------------------------------------------
# Emulator
# ------------------------------------------------------------

# Puerto del emulador
ADB_PORT = "emulator-5554"

# Ruta del ADB (opcional, para más adelante)
ADB_PATH = "C:/LDPlayer/LDPlayer9/adb.exe"


# ------------------------------------------------------------
# Bot tuning
# ------------------------------------------------------------

DROP_RADIUS_FACTOR = 0.70  # used to calculate the drop radius based on the maximum distance from the center of the blob

# ------------------------------------------------------------
# Debug
# ------------------------------------------------------------

DEBUG = {
    "cart": True,
    "attack": True,
    "vision": True,
    "timing": True,
    "adb": False,
    "flow": True,
}

DEBUG_INSPECTION = False # used to print the file, function, and line number of the log message
DROP_ANALYZER = True # used to analyze the drop point and visualize it on the screenshot
