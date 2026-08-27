import time
print(f">>> gameflow.py  starting [{time.perf_counter():.3f}]")

import time as t
import func as f
import attacks as a
#import elixir_cart
import cart_calibration

import botstate
import machine_state

import random
from func import tap_scale
import settings
import screen_layout
import screen_detector


def tap_surrender_button():
    while True:
        if not botstate.should_run():
            f.log("[GameFlow] Bot detenido. Se cancela la espera del botón surrender.")
            return False

        detected = screen_detector.screen_detect(screen_detector.WAITING_SURRENDER)

        if detected == screen_detector.DETECTED_SURRENDER:
            f.log(f"SURRENDER ready: {detected}", debug=True, color="magenta", category="detection")
            x = random.randint(24, 246)
            y = random.randint(721, 780)
            tap_scale(x, y)
            return True

        if detected == screen_detector.DETECTED_FIND:
            f.log("Warning: Find button not expected", color="red", category="detection")

        f.log("Botón surrender no está visible. Reintentando en 10 segundos.")
        t.sleep(10)


def confirm_surrender():
    x = random.randint(1014, 1323)
    y = random.randint(643, 752)
    tap_scale(x, y)


def handle_star_bonus():
    """Handle the optional daily star bonus window after returning Home.

    The pixel and button coordinates are provisional and must be calibrated
    against a real bonus-window screenshot.
    """
    image = f.capture_screenshot()

    if screen_detector.is_star_bonus_visible(image):
        f.log("[GameFlow] Bonus estelar detectado. Pulsando botón para continuar.")
        x, y = screen_layout.STAR_BONUS_BUTTON
        tap_scale(x, y)
        t.sleep(1)
        return True

    f.log("[GameFlow] No hay bonus estelar. Continuando.", debug=True)
    return False


def tap_return_home():
    x = random.randint(850, 1065)
    y = random.randint(875, 950)
    tap_scale(x, y)


def collect_pink_elixir():
    f.log("[Elixir] Moviendo cámara y abriendo Carro…")
    if not open_cart(debug=True):
        f.log("[Elixir] Carro no encontrado, no se hace tap de recogida.")
        return

    f.log("[Elixir] Pulsando botón Recoger…")
    f.log("[Elixir] AQUI L TAP COMMENTED.")
    f.human_tap_scale(1301, 871, 1510, 944)
    f.log("[Elixir] Recompensa recogida.")
    t.sleep(5)
    f.log("[Elixir] Cerrando Ventana.")
    f.human_tap_scale(1583, 60, 1630, 132)
    f.log("[Elixir] Recompensa recogida.")
    t.sleep(5)
    return True


def open_cart(debug=False):
    xi = 1850
    yi = 350
    dx, dy = settings.swipe_dx, settings.swipe_dy
    f.wait_for_stable_screen()
    f.stable_swipe(xi, yi, xi + dx, yi + dy, 1500)
    screenshot_path = f.screenshot("cart_search")
    position = cart_calibration.locate_cart(screenshot_path, debug=debug)
    if position is None:
        f.log("[Elixir] Carro no encontrado.")
        return False
    x, y = position
    f.log(f"TAP REAL EN: {x}, {y}")
    f.tap_absolute(x, y)
    t.sleep(0.4)
    return True


def try_collect_pink_elixir():
    f.log("[Elixir] Intentando recoger elixir rosa…")
    if collect_pink_elixir():
        f.log("[Elixir] Elixir rosa recogido correctamente.")
        return True
    f.log("[Elixir] No había elixir rosa listo para recoger.")
    return False


def get_elixir_level():
    levels = (
        ("FULL", screen_layout.ELIXIR_FULL_PIXEL),
        ("75%", screen_layout.ELIXIR_75_PIXEL),
        ("50%", screen_layout.ELIXIR_50_PIXEL),
        ("25%", screen_layout.ELIXIR_25_PIXEL),
    )
    f.log("[Elixir] Buscando Niveles de Elixir.", debug=True)
    image = f.capture_screenshot()
    for level, (x, y) in levels:
        f.log(f"[Elixir] buscando Nivel : {level} (pos={x},{y})", debug=True)
        if x is None or y is None:
            continue
        if f.check_pixel_from_image(image, x, y, screen_layout.ELIXIR_COLOR, tol=screen_layout.PIXEL_TOLERANCE):
            f.log(f"[Elixir] Nivel detectado: {level} (pos={x},{y})")
            return level
    return None


def is_elixir_full():
    f.log("[Elixir] Buscando si Elixir Full.")
    return get_elixir_level() == "FULL"


def find_match():
    f.log("[GameFlow] Buscando aldea…")
    f.log("Pulso en Atacar", category="Find")
    tap_scale(100, 1000)
    machine_state.set_state(machine_state.WAITING_FIND)
    while botstate.should_run():
        find_ready = screen_detector.is_find_button_visible()
        f.log(f"FIND ready: {find_ready}", debug=True, color="magenta", category="detection")
        if find_ready:
            f.log("Pulso en Find")
            tap_scale(1375, 650)
            t.sleep(5)
            machine_state.set_state(machine_state.ATTACKING)
            return True
        f.log("Warning: FIND button not detected. Esperando…", color="red", category="detection")
        t.sleep(1)
    f.log("[GameFlow] Bot detenido mientras esperaba FIND.")
    return False


def wait_for_battle_end():
    f.log("Esperando fin de batalla…")
    while botstate.should_run():
        x, y = screen_layout.BATTLE_END_PIXEL
        if f.check_pixel(x, y, screen_layout.BATTLE_END_COLOR, tol=screen_layout.PIXEL_TOLERANCE):
            f.log("Batalla terminada")
            return True
        t.sleep(1)
    f.log("Bot detenido mientras esperaba el fin de batalla.")
    return False


def collect_loot():
    f.log("Recogiendo botín…")
    f.tap_scale(950, 900)
    t.sleep(2)
    f.swipe1()
    t.sleep(1)
    f.tap_scale(871, 521)
    t.sleep(1)
    f.tap_scale(1400, 920)
    t.sleep(1)
    f.tap_scale(1600, 100)
    t.sleep(1)
    f.log("Botín recogido")


def perform_attack(attempt_label):
    f.log(f">>> Ataque {attempt_label} <<<")
    if not find_match():
        return False
    t.sleep(2)
    a.BBFarm()

    if settings.get_attack_mode() == "surrender":
        if not tap_surrender_button():
            return False
        t.sleep(1)
        confirm_surrender()
        t.sleep(1)
    else:
        if not wait_for_battle_end():
            return False

    # Ambos modos convergen aquí: primero volver a Home.
    f.log(">>> Return Home <<<")
    tap_return_home()
    t.sleep(3)

    # Después de Home puede aparecer, de forma opcional, la ventana del bonus estelar.
    handle_star_bonus()


def farm_until_full(attacks_per_cycle=None):
    while not is_elixir_full():
        cycle_attacks = settings.get_attacks_per_cycle() if attacks_per_cycle is None else attacks_per_cycle
        f.log(f">>> Nuevo ciclo de {cycle_attacks} ataques <<<")
        for i in range(cycle_attacks):
            if not botstate.should_run():
                return False
            perform_attack(i + 1)
        if try_collect_pink_elixir():
            f.log("Recogido elixir rosa. Nuevo ciclo de ataques.")
            continue
        f.log("No había elixir rosa. Iniciando ataques extra...")
        while True:
            if not botstate.should_run():
                return False
            f.log("Ataque extra...")
            perform_attack("extra")
            if try_collect_pink_elixir():
                f.log("Recogido elixir rosa tras ataque extra. Nuevo ciclo.")
                break
            f.log("Aún no hay elixir rosa. Otro ataque extra...")
    f.log(">>> Almacén lleno. Fin del ciclo. <<<")
    return True
