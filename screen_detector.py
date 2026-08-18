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

    Si se proporciona una imagen, se reutiliza esa captura. Si no, la función
    captura la pantalla por sí misma. La función se mantiene como detección
    individual; screen_detect() se utiliza cuando hay que comprobar varios
    elementos sobre una misma captura.
    """
    x, y = screen_layout.SURRENDER_PIXEL

    if image is None:
        return f.check_pixel(
            x,
            y,
            screen_layout.SURRENDER_COLOR,
            tol=screen_layout.PIXEL_TOLERANCE,
        )

    return f.check_pixel_from_image(
        image,
        x,
        y,
        screen_layout.SURRENDER_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )


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

        x, y = screen_layout.FIND_BUTTON_PIXEL
        if f.check_pixel_from_image(
            image,
            x,
            y,
            screen_layout.FIND_BUTTON_COLOR,
            tol=screen_layout.PIXEL_TOLERANCE,
        ):
            return DETECTED_FIND

    elif state == WAITING_FIND:
        x, y = screen_layout.FIND_BUTTON_PIXEL
        if f.check_pixel_from_image(
            image,
            x,
            y,
            screen_layout.FIND_BUTTON_COLOR,
            tol=screen_layout.PIXEL_TOLERANCE,
        ):
            return DETECTED_FIND

    return None


def is_find_button_visible():
    """Comprueba si el botón FIND parece estar visible.

    Función sencilla mantenida por compatibilidad. La nueva función
    screen_detect() centraliza las comprobaciones sobre una captura.
    """
    x, y = screen_layout.FIND_BUTTON_PIXEL

    return f.check_pixel(
        x,
        y,
        screen_layout.FIND_BUTTON_COLOR,
        tol=screen_layout.PIXEL_TOLERANCE,
    )
