import os
import time as t

import cv2
from PIL import Image

import func as f

def detect_cart(image_path, debug=False):

    templates = _get_cart_templates(debug)

    img = cv2.imread(image_path)
    if img is None:
        f.log(f"[CART] No se pudo cargar la imagen: {image_path}")
        return None

    for tpl in templates:

        result = f.find_template_multiscale(
            image_path,
            tpl,
            scales=(0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15),
            threshold=0.82
        )

        if not result:
            continue

        if not _validate_cart_detection(img, tpl, result):
            continue

        result["template"] = tpl
        return result

    return None

def search_cart(total_offset=500, debug=False):

    # Swipe desde zona alta
    xi = 1850
    yi = 350
    
    f.wait_for_stable_screen()


    f.stable_swipe(xi, yi, xi, yi + total_offset, 1500)

    screenshot_path = f.screenshot("cart_search")

    detection = detect_cart(screenshot_path, debug=debug)

    if not detection:
        f.log("Cart not found")
        return False

    _save_detection_debug(screenshot_path, detection)

    tap_cart(detection)

    return True



def _get_cart_templates(debug=False):

    templates = []

    if debug:
        templates.extend([
            "templates/Elixir_Cart_1.png",
            "templates/Elixir_Cart_2.png",
        ])

    templates.extend([
        "templates/Elixir_Cart_3.png",
        "templates/carro_extra_full.png",
    ])

    return templates

def _validate_cart_detection(img, tpl, result):

    if img is None:
        return False

    # Todos los templates menos este son válidos
    if tpl != "templates/carro_extra_full.png":
        return True

    if not result or "position" not in result:
        return False

    x, y = result["position"]

    if x <= 5 or y <= 5:
        return False

    b, g, r = map(int, img[y-5, x-5])

    if not (abs(r - 172) <= 20 and
            abs(g - 79) <= 20 and
            abs(b - 41) <= 20):
        f.log("Descartado: fondo NO rojo")
        return False

    return True

def _save_detection_debug(screenshot_path, result):

    try:
        if not os.path.exists("debug"):
            os.makedirs("debug")

        if not result or "position" not in result or "size" not in result:
            f.log("[DEBUG] Detección incompleta, no se puede guardar recorte")
            return

        x, y = result["position"]
        w, h = result["size"]

        img = Image.open(screenshot_path)
        crop = img.crop((x, y, x + w, y + h))

        ts = t.strftime("%Y%m%d_%H%M%S")
        crop_name = f"debug/carro_detectado_{ts}.png"
        crop.save(crop_name)

        f.log(f"[DEBUG] Recorte guardado en {crop_name}")

    except Exception as e:
        f.log(f"[DEBUG] Error guardando recorte: {e}")

def tap_cart(detection):

    if not detection or "position" not in detection or "size" not in detection:
        f.log("[CART] Detección incompleta, no se hace tap")
        return

    x, y = detection["position"]
    w, h = detection["size"]

    cx = x + w // 2
    cy = y + h // 2

    f.log(f"TAP REAL EN: {cx}, {cy}")

    f.tap_absolute(cx, cy)

    t.sleep(0.4)


"""
BACKUP - OLD buscar_carro() function from func.py (moved here for archival)

def buscar_carro(total_offset=500, debug=False):
    log("Iniciando búsqueda del carro...")

    # Swipe desde zona alta
    xi = 1850
    yi = 350

    # xi = 1450
    # yi = 150


    # t.sleep(2)  # Espera para estabilizar antes del swipe
    log("Espero un poco antes del swipe para buscar el carro...")
    wait_for_stable_screen()



    screenshot_path = screenshot(tag="pre_swipe")
    log("saco foto antes del swipe para buscar el carro...")

    p.draw_line_on_image(screenshot_path, xi, yi, xi, yi + total_offset, color=(255, 0, 0), width=5)
    log("pinto linea simulando swipe el carro...")

    stable_swipe(xi, yi, xi, yi + total_offset, 1500)
    #swipe_test()  # swipe de prueba para buscar el carro

    #t.sleep(3)  # Esperar a que la pantalla se estabilice
    log("esperando 3 segundos después del swipe para buscar el carro...")

    screenshot_path = screenshot("buscar_carro")

    # --- ORDEN DE BÚSQUEDA ---
    templates = []

    if debug:
        templates.append("templates/Elixir_Cart_1.png")
        templates.append("templates/Elixir_Cart_2.png")

    templates.append("templates/Elixir_Cart_3.png")
    templates.append("templates/carro_extra_full.png")

    # --- BÚSQUEDA SECUENCIAL ---
    result = None
    tpl_used = None

    for tpl in templates:
        log(f"Buscando {tpl} ...")
        result = find_template_multiscale(
            screenshot_path,
            tpl,
            scales=(0.9, 1.0, 1.1),
            threshold=0.82
        )

        if not result:
            continue  # no match, probar siguiente

        # --- VALIDACIÓN SOLO PARA LA PLANTILLA ROJA ---
        if tpl == "templates/carro_extra_full.png":
            img = cv2.imread(screenshot_path)
            x, y = result["position"]
            w, h = result["size"]

            if x > 5 and y > 5:
                b, g, r = map(int, img[y-5, x-5])  # <-- FIX IMPORTANTE
                if not (abs(r - 172) <= 20 and abs(g - 79) <= 20 and abs(b - 41) <= 20):
                    log("Descartado: fondo NO rojo → seguir buscando")
                    result = None
                    continue  # seguir con la siguiente plantilla       

        # Si llega aquí → match válido
        tpl_used = tpl
        break

    # --- RESULTADO ---
    if result:
        log(f"Carro detectado con {tpl_used} en {result['position']} scale={result['scale']} conf={result['confidence']:.2f}")

        # ============================
        #   RECORTE DEL ÁREA DETECTADA
        # ============================
        try:
            if not os.path.exists("debug"):
                os.makedirs("debug")

            x, y = result["position"]
            w, h = result["size"]

            img = Image.open(screenshot_path)
            crop = img.crop((x, y, x + w, y + h))

            ts = t.strftime("%Y%m%d_%H%M%S")
            crop_name = f"debug/carro_detectado_{ts}.png"
            crop.save(crop_name)

            log(f"[DEBUG] Recorte guardado en {crop_name}")
        except Exception as e:
            log(f"[DEBUG] Error guardando recorte: {e}")

        # Tap en el centro
        cx = x + w // 2
        cy = y + h // 2

        log(f"[DEBUG] x={x}, y={y}, w={w}, h={h}")
        log(f"TAP REAL EN: {cx}, {cy}")
        screenshot_path = screenshot("carro_encontrado")

        tap_absolute(cx, cy)
        t.sleep(0.4)
        return True

    log("Carro no encontrado después del swipe")
    return False
"""



