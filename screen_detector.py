import func as f
import screen_layout


# -----------------------------------------
# Detección sencilla del estado de la pantalla
# -----------------------------------------


def is_find_button_visible():
    """Comprueba si el botón FIND parece estar visible.

    La posición y el color son valores provisionales y deben calibrarse
    con una captura real del emulador.
    """
    x, y = screen_layout.FIND_BUTTON_PIXEL

    return f.check_pixel(
        x,
        y,
        screen_layout.FIND_BUTTON_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )
