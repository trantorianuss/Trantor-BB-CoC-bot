import time
print(f">>> main.py  starting [{time.perf_counter():.3f}]")

import threading
import cv2
import ocr

import func as f
import botcontroller as controller
import paint as p
import settings
import state_calibration
import vision
import coords
import elixir_cart
import logger as l 
from gui import BotInterface
import calibration
import machine_state


# Helper
def parse_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

# -----------------------------
#   FUNCIONES MANEJADORAS (LOGIC)
# -----------------------------


def bttn_start_Farm():
    machine_state.set_state(machine_state.STARTING)
    controller.start_farm()

def bttn_stop():
    controller.stop()

def bttn_screenshot():
    try:
        image = f.capture_screenshot()

        if image is None:
            raise RuntimeError("Screenshot capture returned no image")

        if app.screenshot_resize_checkbox.get() == 1:
            height, width = image.shape[:2]
            if (width, height) != (coords.BASE_W, coords.BASE_H):
                image = cv2.resize(
                    image,
                    (coords.BASE_W, coords.BASE_H),
                    interpolation=cv2.INTER_AREA,
                )
            app.log(f"Screenshot resized to base resolution: {coords.BASE_W}x{coords.BASE_H}")

        filename = f.save_image("screen", image)
        app.log(f"Screenshot saved: {filename}")
    except Exception as e:
        app.log(f"Screenshot failed: {e}")

def bttn_recognize():
    try:
        filename = f.screenshot()
        result = ocr.ocr_image(filename)
        app.log(f"OCR result: {result}")
    except Exception as e:
        app.log(f"Image recognition failed: {e}")

def _run_search_cart(dy, debug):
    try:
        elixir_cart.search_cart(total_offset=dy, debug=debug)
    except Exception as e:
        app.log(f"Buscar Carro failed: {e}")


def bttn_buscar_carro():
    try:
        _, dy_val = app.get_swipe_values()
        dy = parse_int(dy_val, default=400)
        app.log("Buscar Carro iniciado...")
        thread = threading.Thread(target=_run_search_cart, args=(dy, True), daemon=True)
        thread.start()
    except Exception as e:
        app.log(f"Buscar Carro failed: {e}")

def bttn_test():
    try:
        _, dy_val = app.get_swipe_values()
        dy = parse_int(dy_val, default=400)

        # Swipe desde zona alta
        xi = 1850
        yi = 350

        app.log("=== TEST: detectar puntos ===")

        app.log("=== TEST: hago SWIPE ===")
        f.stable_swipe(xi, yi, xi, yi + dy, 1500)


        templates = [
            "templates/cueva.png",
            "templates/esquina_norte.png",
            "templates/esquina_oeste.png",
            "templates/barco.png",
            "templates/muelle.png"
        ]

        resultados = vision.detectar_puntos(
            templates,
            scales=(0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15),
            threshold=0.82,
            debug=True
        )

        vision.print_resultados(resultados)

        app.log("=== FIN TEST ===")

    except Exception as e:
        app.log(f"Test detectar_puntos failed: {e}")


def bttn_calibrar_zoom(popup=None):
    app.log("Test de Calibrar Zoom")
    try:
        app.log("=== TEST INICIADO ===")
        result = f.calibrar_zoom(popup=popup)

        if result is None:
            app.log("Calibración no detectó el BH.")
            return

        state_calibration.set_calibration(
            pos=result["pos"],
            size=result["size"],
            scale=result["scale"],
            zoom=result["zoom"],
        )

        app.log(f"Calibración OK: zoom={result['zoom']} pos={result['pos']} size={result['size']}")

    except Exception as e:
        app.log(f"Calibración falló: {e}")

def bttn_calibrate(popup=None):

    app.log("Starting calibration...")

    screenshot_path = f.screenshot("calibration")

    calibration.run(screenshot_path)

# -----------------------------
#   INICIALIZACIÓN
# -----------------------------

# antes de crear app
print("==========================================")
print(">>> Clash of Clans Trantor Bot starting...")
print("==========================================")


# Instanciar pasándole los callbacks
app = BotInterface(
    on_start_farm=bttn_start_Farm,
    on_stop=bttn_stop,
    on_screenshot=bttn_screenshot,
    on_recognize=bttn_recognize,
    on_buscar_carro=bttn_buscar_carro,
    on_test=bttn_test,
    on_calibrar_zoom=bttn_calibrar_zoom,
    on_calibrate=bttn_calibrate   
)

# Conectar el logger central con la UI para que toda la app use la misma salida
l.set_log_sink(app.log)


def initialize_coords():
    app.log("[coords] Inicializando resolución...")
    try:
        real_w, real_h = f.get_real_resolution()
        coords.init_resolution(real_w, real_h)
        app.log(f"[coords] Resolución inicializada: {real_w}x{real_h}")
    except Exception as exc:
        app.log(f"[coords] No se pudo obtener la resolución real: {exc}")
        coords.init_resolution(1920, 1080)
        app.log("[coords] Usando resolución por defecto: 1920x1080")


# -----------------------------
#   MAIN
# -----------------------------

l.log("  Clash of Clans Trantor Bot")
l.log("  Initializing application...")

f.cleanup_screenshots()
initialize_coords()


if __name__ == "__main__":
    app.mainloop()