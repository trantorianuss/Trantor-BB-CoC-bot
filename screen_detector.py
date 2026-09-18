import func as f
import screen_layout


# -----------------------------------------
# Detección sencilla del estado de la pantalla
# -----------------------------------------

# Estados iniciales del ataque.
# Pueden no ser los nombres/estados definitivos cuando la máquina de estados
# crezca y se formalice.
ATTACKING = "attacking"
WAITING_SURRENDER = "waiting_surrender"
WAITING_FIND = "waiting_find"

# Valores que puede devolver screen_detect().
DETECTED_SURRENDER = "surrender"
DETECTED_FIND = "find"


def is_surrender_button_visible(image=None):
    """Comprueba si el botón de surrender está visible.

    Si no se proporciona una imagen, captura la pantalla. A partir de ahí
    siempre analiza la imagen con check_pixel_from_image().
    """
    if image is None:
        image = f.capture_screenshot()

    x, y = screen_layout.SURRENDER_PIXEL

    return f.check_pixel_from_image(
        image,
        x,
        y,
        screen_layout.SURRENDER_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )


def is_find_button_visible(image=None):
    """Comprueba si el botón FIND parece estar visible.

    Si no se proporciona una imagen, captura la pantalla. A partir de ahí
    siempre analiza la imagen con check_pixel_from_image().
    """
    if image is None:
        image = f.capture_screenshot()

    x, y = screen_layout.FIND_BUTTON_PIXEL

    return f.check_pixel_from_image(
        image,
        x,
        y,
        screen_layout.FIND_BUTTON_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )


def is_bb_home_visible(image=None):
    """Comprueba si la pantalla principal de BB está visible."""
    if image is None:
        image = f.capture_screenshot()

    x, y = screen_layout.BB_HOME_PIXEL

    return f.check_pixel_from_image(
        image,
        x,
        y,
        screen_layout.BB_HOME_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )


def is_star_bonus_visible(image=None):
    """Comprueba si aparece la ventana intermedia del bonus estelar.

    Los dos puntos deben coincidir para confirmar la pantalla.
    """
    if image is None:
        image = f.capture_screenshot()

    x1, y1 = screen_layout.STAR_BONUS_PIXEL_1
    x2, y2 = screen_layout.STAR_BONUS_PIXEL_2

    first_match = f.check_pixel_from_image(
        image,
        x1,
        y1,
        screen_layout.STAR_BONUS_COLOR_1,
        tol=screen_layout.PIXEL_TOLERANCE,
    )
    second_match = f.check_pixel_from_image(
        image,
        x2,
        y2,
        screen_layout.STAR_BONUS_COLOR_2,
        tol=screen_layout.PIXEL_TOLERANCE,
    )

    return first_match and second_match


def screen_detect(state):
    """Comprueba los elementos relevantes para el estado indicado.

    Se hace una única captura por consulta. Sobre esa misma imagen se prueban
    los elementos relevantes para el estado, en el orden de probabilidad.

    Devuelve DETECTED_SURRENDER, DETECTED_FIND o None si no encuentra ninguno.
    """
    image = f.capture_screenshot()

    if state == WAITING_SURRENDER:
        # Mientras esperamos SURRENDER, FIND es una pantalla posible pero no esperada.
        if is_surrender_button_visible(image):
            return DETECTED_SURRENDER

        if is_find_button_visible(image):
            return DETECTED_FIND

    elif state == WAITING_FIND:
        if is_find_button_visible(image):
            return DETECTED_FIND

    return None
