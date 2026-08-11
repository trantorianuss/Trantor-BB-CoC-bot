import time as t
import func as f
import attacks as a
#import elixir_cart
import cart_calibration

import botstate

import random
from func import tap_scale
import state
import screen_layout

print(">>> GameFlow.py starting")


# -----------------------------
#   Surrender : Farming in Builder base
# -----------------------------

def is_surrender_button_visible(x=48, y=737, target=(247, 93, 95), tol=20):
    """Comprueba si el botón de surrender está visible usando un pixel de referencia.
    Ajusta x, y y target a valores concretos de tu pantalla.
    """
    return f.check_pixel(x, y, target, tol=tol)


def tap_surrender_button():
    while True:
        if not botstate.should_run():
            f.log("[GameFlow] Bot detenido. Se cancela la espera del botón surrender.")
            return False

        if is_surrender_button_visible():
            x = random.randint(24, 246)
            y = random.randint(721, 780)
            tap_scale(x, y)
            return True

        f.log("[GameFlow] Botón surrender no está visible. Reintentando en 10 segundos.")
        t.sleep(10)


def confirm_surrender():
    x = random.randint(1014, 1323)
    y = random.randint(643, 752)
    tap_scale(x, y)


def tap_return_home():
    # Ajusta estos valores si tu botón está en otra zona
    x = random.randint(850, 1065)
    y = random.randint(875, 950)
    tap_scale(x, y)

# -------------------------
#  RECOGER ELIXIR ROSA
# -------------------------
def collect_pink_elixir():
    f.log("[Elixir] Moviendo cámara y abriendo Carro…")

    #if not elixir_cart.search_cart(total_offset=600, debug=True):
    if not open_cart(debug=True):
    
        f.log("[Elixir] Carro no encontrado, no se hace tap de recogida.")
        return

    f.log("[Elixir] Pulsando botón Recoger…")

    # Botón verde "Recoger"
    f.log("[Elixir] AQUI L TAP COMMENTED.")
    f.human_tap_scale(1301, 871, 1510, 944)

    f.log("[Elixir] Recompensa recogida.")
    t.sleep(5)  # Espera un segundo para asegurar que la acción se complete
    
    # Botón Rojo "Cerrar Ventana"
    f.log("[Elixir] Cerrando Ventana.")
    f.human_tap_scale(1583, 60, 1630, 132)

    f.log("[Elixir] Recompensa recogida.")
    t.sleep(5)  # Espera un segundo para asegurar que la acción se complete
    return True

def open_cart(debug=False):

    # Swipe desde zona alta
    xi = 1850
    yi = 350

    dx, dy = state.swipe_dx, state.swipe_dy
    
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

# -------------------------
#  COMPROBAR NIVEL DE ELIXIR
# -------------------------

def get_elixir_level():
    """Devuelve el nivel detectado del elixir para mostrarlo en el log.

    FULL es el único nivel que afecta al flujo del bot. Los niveles 75/50/25
    son únicamente informativos y sus coordenadas quedan pendientes de medir.
    """
    target = (121, 69, 197)
    tol = 20

    levels = (
        ("FULL", screen_layout.ELIXIR_FULL_PIXEL),
        ("75%", screen_layout.ELIXIR_75_PIXEL),
        ("50%", screen_layout.ELIXIR_50_PIXEL),
        ("25%", screen_layout.ELIXIR_25_PIXEL),
    )

    for level, (x, y) in levels:
        # Las coordenadas pendientes no se comprueban todavía.
        if x is None or y is None:
            continue

        if f.check_pixel(x, y, target, tol=tol):
            f.log(f"[Elixir] Nivel detectado: {level} (pos={x},{y})")
            return level

    return None


def is_elixir_full():
    """Comprueba exclusivamente la condición que termina el farming.

    Los niveles 75/50/25 son informativos y nunca cambian el flujo.
    """
    level = get_elixir_level()
    return level == "FULL"


# -----------------------------
#   FIND MATCH (buscar aldea)
# -----------------------------
def find_match():
    f.log("[GameFlow] Buscando aldea…")
    f.find()
    t.sleep(5)


# -----------------------------
#   ESPERAR FIN DE BATALLA
# -----------------------------
def wait_for_battle_end():
    f.log("[GameFlow] Esperando fin de batalla…")

    while f.checkpixelBB_old(888, 900) != (180, 230, 125, 255):
        t.sleep(1)

    f.log("[GameFlow] Batalla terminada")


# -----------------------------
#   RECOGER BOTÍN
# -----------------------------
def collect_loot():
    f.log("[GameFlow] Recogiendo botín…")

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

    f.log("[GameFlow] Botín recogido")


# -----------------------------
#   CICLO DE ATAQUE FARM (1 ciclo)
# -----------------------------


def perform_attack(attempt_label):
    f.log(f">>> Ataque {attempt_label} <<<")

    # 0. Buscar aldea
    find_match()
    t.sleep(2)          # ← necesario para que cargue la aldea

    # 1. Atacar
    a.BBFarm()

    # 2. Rendirse
    if not tap_surrender_button():
        return False
    t.sleep(1)

    # 3. Confirmar rendición
    confirm_surrender()
    t.sleep(1)

    # 4. Volver a Home
    f.log(">>> Return Home <<<")
    tap_return_home()
    t.sleep(1)


def farm_until_full(attacks_per_cycle=None):

    while not is_elixir_full():
        cycle_attacks = state.get_attacks_per_cycle() if attacks_per_cycle is None else attacks_per_cycle
        f.log(f">>> Nuevo ciclo de {cycle_attacks} ataques <<<")

        for i in range(cycle_attacks):  ## numero de ataques por ciclo
            if not botstate.should_run():
                return False
            perform_attack(i + 1)

        # --- INTENTAR RECOGER ELIXIR ---
        if try_collect_pink_elixir():
            f.log("[GameFlow] Recogido elixir rosa. Nuevo ciclo de ataques.")
            continue

        # --- ATAQUES EXTRA HASTA QUE HAYA ELIXIR ---
        f.log("[GameFlow] No había elixir rosa. Iniciando ataques extra...")

        while True:
             
            if not botstate.should_run():
                return False   

            f.log("[GameFlow] Ataque extra...")
            perform_attack("extra")

            if try_collect_pink_elixir():
                f.log("[GameFlow] Recogido elixir rosa tras ataque extra. Nuevo ciclo.")
                break   # ← vuelve al while principal (nuevo ciclo)

            f.log("[GameFlow] Aún no hay elixir rosa. Otro ataque extra...")

        # vuelve al inicio del while principal

    f.log(">>> Almacén lleno. Fin del ciclo. <<<")
    
    return True   # ← señal para parar






