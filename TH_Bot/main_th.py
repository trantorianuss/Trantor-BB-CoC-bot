import time
print(f">>> main_th.py  starting [{time.perf_counter():.3f}]")

import threading
import cv2
import ocr

from TH_Bot import botcontroller_th as controller
from TH_Bot.gui_th import BotInterface
from TH_Bot.th_strategies import load_attack_config


import func as f
import paint as p
import settings
import state_calibration
import vision
import coords
import elixir_cart
import logger as l

import calibration
import machine_state
import pixel_inspector


def parse_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


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
                image = cv2.resize(image, (coords.BASE_W, coords.BASE_H), interpolation=cv2.INTER_AREA)
            l.log(f"Screenshot resized to base resolution: {coords.BASE_W}x{coords.BASE_H}")

        if app.screenshot_resize_checkbox.get() == 1:
            filename = f.save_image("screen_resized", image)
        else:
            filename = f.save_image("screen", image)
        l.log(f"Screenshot saved: {filename}")
    except Exception as e:
        l.log(f"Screenshot failed: {e}")


def bttn_pixel_inspector():
    pixel_inspector.open(app)


def bttn_recognize():
    try:
        filename = f.screenshot()
        result = ocr.ocr_image(filename)
        l.log(f"OCR result: {result}")
    except Exception as e:
        l.log(f"Image recognition failed: {e}")


def _run_search_cart(dy, debug):
    try:
        elixir_cart.search_cart(total_offset=dy, debug=debug)
    except Exception as e:
        l.log(f"Find Cart failed: {e}")


def bttn_buscar_carro():
    try:
        _, dy_val = app.get_swipe_values()
        dy = parse_int(dy_val, default=400)
        l.log("Find Cart started...")
        thread = threading.Thread(target=_run_search_cart, args=(dy, True), daemon=True)
        thread.start()
    except Exception as e:
        l.log(f"Find Cart failed: {e}")


def bttn_test():
    try:
        _, dy_val = app.get_swipe_values()
        dy = parse_int(dy_val, default=400)
        xi = 1850
        yi = 350
        l.log("=== TEST: detecting points ===")
        l.log("=== TEST: performing SWIPE ===")
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
        l.log("=== TEST FINISHED ===")
    except Exception as e:
        l.log(f"Test detect_points failed: {e}")


def bttn_calibrar_zoom(popup=None):
    l.log("Zoom Calibration Test")
    try:
        l.log("=== TEST STARTED ===")
        result = f.calibrar_zoom(popup=popup)
        if result is None:
            l.log("Calibration did not detect the BH.")
            return
        state_calibration.set_calibration(
            pos=result["pos"],
            size=result["size"],
            scale=result["scale"],
            zoom=result["zoom"],
        )
        l.log(f"Calibration OK: zoom={result['zoom']} pos={result['pos']} size={result['size']}")
    except Exception as e:
        l.log(f"Calibration failed: {e}")


def bttn_calibrate(popup=None):
    l.log("Starting calibration...")
    screenshot_path = f.screenshot("calibration")
    calibration.run(screenshot_path)


print("==========================================")
print(">>> Clash of Clans Trantor Bot starting...")
print("==========================================")

app = BotInterface(
    on_start_farm=bttn_start_Farm,
    on_stop=bttn_stop,
    on_screenshot=bttn_screenshot,
    on_recognize=bttn_recognize,
    on_buscar_carro=bttn_buscar_carro,
    on_test=bttn_test,
    on_calibrar_zoom=bttn_calibrar_zoom,
    on_calibrate=bttn_calibrate,
    on_pixel_inspector=bttn_pixel_inspector,
)

l.set_log_sink(app.log)

l.log("  Clash of Clans Trantor Bot")
l.log("  Initializing application...")


f.cleanup_screenshots()
coords.initialize()
load_attack_config()



if __name__ == "__main__":
    app.log("================================================")
    app.log(">>> Trantor Bot ready... Waiting for user input.")
    app.log("================================================")
    app.mainloop()
