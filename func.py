import os
import shutil
import time as t
from PIL import Image, ImageEnhance
from PIL.ImageChops import screen
import easyocr
import cv2
import numpy as np
import random as r
import subprocess
import random

import config
import paint as p
import coords
import state
from logger import log

BASE_W = 1920
BASE_H = 1080

print(">>> func.py starting")

reader = easyocr.Reader(['en'], gpu=False)


import os
import config

def adb(cmd_rest):
    """
    Ejecuta un comando ADB usando ADB_PATH y ADB_PORT del config.
    cmd_rest es la parte del comando que va después de 'shell'.
    Ejemplo: 'input tap 100 200'
    """
    full_cmd = f'{config.ADB_PATH} -s {config.ADB_PORT} shell {cmd_rest}'.strip()
    log(f" {full_cmd}", debug=True, category="adb")

    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        log(f"Error: {result.stderr.strip() or result.stdout.strip()}", debug=True, category="adb")
        return ""

    return result.stdout.strip()


class Timer:

    def __init__(self, nombre):
        self.nombre = nombre

    def __enter__(self):
        self.t0 = t.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        dt = (t.perf_counter() - self.t0) * 1000
        log(f"[TIME] {self.nombre}: {dt:.1f} ms", category="timing")

def get_real_resolution():
    out = adb("wm size")
    if not out:
        raise RuntimeError("No se pudo obtener la resolución desde ADB")

    # Ejemplo de salida: "Physical size: 1920x1080"
    size_part = out.split(":")[-1].strip()
    w, h = map(int, size_part.split("x"))
    return w, h

def screenshot(tag: str = None):
    # tag opcional para diferenciar capturas, útil para debugging

    # Crear carpeta si no existe
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    # Nombre con timestamp
    timestamp = t.strftime("%Y%m%d_%H%M%S")

    # Si viene un tag, lo añadimos al nombre
    if tag:
        filename = f"screenshots/screen_{timestamp}_{tag}.png"
    else:
        filename = f"screenshots/screen_{timestamp}.png"

    # Captura directa del emulador
    t0 = t.perf_counter()
    cmd = f"{config.ADB_PATH} -s {config.ADB_PORT} exec-out screencap -p"
    with open(filename, "wb") as f_out:
        subprocess.run(cmd.split(), stdout=f_out)

    t1 = t.perf_counter()
    log(f"screenshot ADB : {(t1-t0)*1000:.1f} ms")

    return filename


def ocr_image(filename, region=None, allowlist=None, detail=0):
    """OCR sobre una imagen guardada, opcionalmente recortando una región."""
    with Image.open(filename) as photo:
        if region:
            photo = photo.crop(region)
        photo = photo.convert("L")
        photo = ImageEnhance.Contrast(photo).enhance(2.0)
        image_np = np.array(photo)

    try:
        return reader.readtext(image_np, allowlist=allowlist, detail=detail)
    except Exception as e:
        log(f"[OCR] Error procesando imagen {filename}: {e}")
        return []


def recognize_screenshot(region=None, allowlist=None):
    filename = screenshot()
    return ocr_image(filename, region=region, allowlist=allowlist, detail=0)


def find_template(haystack_path, needle_path, threshold=0.8):
    """Busca una plantilla en una imagen y devuelve la posición si la confianza es suficiente."""
    screen = cv2.imread(haystack_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(needle_path, cv2.IMREAD_GRAYSCALE)

    if screen is None or template is None:
        log(f"[TEMPLATE] No se pudo cargar imagenes: {haystack_path} / {needle_path}")
        return None

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    return {
        "position": max_loc,
        "confidence": float(max_val),
        "size": (template.shape[1], template.shape[0]),
        "scale": 1.0,
    }


def find_template_multiscale(haystack_path, needle_path, scales=(0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15), threshold=0.8):
    """Busca una plantilla en varios tamaños para soportar pequeñas variaciones."""
    screen = cv2.imread(haystack_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(needle_path, cv2.IMREAD_GRAYSCALE)

    if screen is None or template is None:
        log(f"[TEMPLATE] No se pudo cargar imagenes: {haystack_path} / {needle_path}")
        return None

    best_result = None

    for scale in scales:
        new_w = int(template.shape[1] * scale)
        new_h = int(template.shape[0] * scale)

        if new_w < 10 or new_h < 10 or new_w > screen.shape[1] or new_h > screen.shape[0]:
            continue

        resized = cv2.resize(
            template,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR,
        )

        result = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            continue

        candidate = {
            "position": max_loc,
            "confidence": float(max_val),
            "size": (new_w, new_h),
            "scale": float(scale),
        }

        if best_result is None or candidate["confidence"] > best_result["confidence"]:
            best_result = candidate

    return best_result


def find_template_on_screen(template_path, threshold=0.8):
    screenshot_path = screenshot()
    return find_template(screenshot_path, template_path, threshold=threshold)

def wait_for_stable_screen(timeout=5):
    start = t.time()
    last = screenshot("stable_check")

    while t.time() - start < timeout:
        t.sleep(0.3)
        current = screenshot("stable_check2")

        img1 = cv2.imread(last)
        img2 = cv2.imread(current)

        if img1 is None or img2 is None:
            last = current
            continue

        diff = cv2.absdiff(img1, img2)
        nonzero = np.count_nonzero(diff)

        if nonzero < 500:  # pantalla estable
            return current  # DEVUELVE LA CAPTURA ESTABLE

        last = current

    return last  # aunque no esté perfecta, devolvemos la última

def stable_swipe(x1, y1, x2, y2, duration=500):
    log("[STABLE SWIPE] esperando pantalla estable...")
    before = wait_for_stable_screen()  # solo 1 captura

    swipe(x1, y1, x2, y2, duration)
    t.sleep(0.5)

    after = screenshot("after_swipe")  # solo 1 captura

    img1 = cv2.imread(before)
    img2 = cv2.imread(after)

    diff = cv2.absdiff(img1, img2)
    nonzero = np.count_nonzero(diff)

    if nonzero < 500:
        log("[STABLE SWIPE] swipe NO ejecutado, reintentando...")
        t.sleep(0.5)
        swipe(x1, y1, x2, y2, duration)
    else:
        log("[STABLE SWIPE] swipe ejecutado correctamente")






def tap_scale(x, y, *_args):
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x, y = coords.scale(x, y)

    log(f"[TAP SCALE] x={x}, y={y}", debug=True, category="flow")
    adb(f"input tap {x} {y}")


def tap_absolute(x, y, *_args):
    log(f"[TAP ABSOLUTE] x={x}, y={y}", debug=True, category="flow")
    adb(f"input tap {x} {y}")


def human_tap_scale(x1, y1, x2, y2):
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x1, y1 = coords.scale(x1, y1)
        x2, y2 = coords.scale(x2, y2)

    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    log(f"[HUMAN TAP SCALE] x={x}, y={y}", debug=True)
    adb(f"input tap {x} {y}")


def human_tap_absolute(x1, y1, x2, y2):
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    log(f"[HUMAN TAP ABSOLUTE] x={x}, y={y}", debug=True)
    adb(f"input tap {x} {y}")


def swipe(x1, y1, x2, y2, duration_ms):
    """
    Swipe genérico usando ADB.
    x1, y1 = punto inicial
    x2, y2 = punto final
    duration_ms = duración en milisegundos
    """
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x1, y1 = coords.scale(x1, y1)
        x2, y2 = coords.scale(x2, y2)

    log(f"[SWIPE] x1={x1}, y1={y1}, x2={x2}, y2={y2}, dur={duration_ms}ms")
    adb(f"input touchscreen swipe {x1} {y1} {x2} {y2} {duration_ms}")


def swipe_test():  # borrar si no esta en uso 
    log("me cago en su ....")
    adb("input touchscreen swipe 1450 150 1450 550 500")

def swipe1():  # borrar si no esta en uso 
    adb("input touchscreen swipe 1450 150 900 650 500")

def swipe2(): 
    adb("input touchscreen swipe 1900 850 100 850 500")

def simple_swipe_up(pixels, duration_ms=300):
    """
    Hace un swipe hacia arriba exactamente 'pixels' píxeles.
    No hace nada más.
    """
    # Punto inicial (centro aproximado de la pantalla)
    x1 = random.randint(750, 850)
    y1 = random.randint(950, 1050)

    # Punto final (misma X, subir 'pixels')
    x2 = x1 - int(pixels * 0.5)   
    y2 = y1 + pixels

    log(f"[SIMPLE SWIPE] {x1},{y1} -> {x2},{y2} dur={duration_ms}ms")

    swipe(x1, y1, x2, y2, duration_ms)

def test_swipe_and_tap_cart():
    """
    Primera versión simple:
    - dx, dy aleatorios
    - Swipe de (200+dx, 400+dy)
    - TAP en (1270-dx, 420-dy)
    """

    # Aleatorio suave, ajusta el rango si quieres más o menos variación
    dx = random.randint(-50, 50)
    dy = random.randint(-50, 50)

    base_sx = 200
    base_sy = 400

    swipe_x = base_sx + dx   # horizontal (hacia la izquierda)
    swipe_y = base_sy + dy   # vertical (hacia abajo)

    # Punto inicial del swipe (puedes cambiarlo si quieres)
    x1 = 800
    y1 = 1000

    # Punto final: izquierda y abajo
    x2 = x1 - swipe_x
    y2 = y1 + swipe_y

    log(f"[TEST SWIPE] dx={dx}, dy={dy}, swipe=({x1},{y1})->({x2},{y2})")
    swipe(x1, y1, x2, y2, 300)



def find(): 
  print(">>> entro en find <<<")
  tap_scale(100, 1000)
  t.sleep(0.3)
  print(">>> find despes de sleeep <<<")
  tap_scale(1375, 650)
  print(">>> find despues de sleep y tap <<<")

def next():
  tap_scale(1750, 800)


def checkloot(port):
    filename = f"Pictures/{port}val.png"
    screenshot(port, filename)
    print("captured")
    t.sleep(0.2)

    with Image.open(filename) as photo:
        (left, upper, right, lower) = (97, 155, 285, 295)
        loot = photo.crop((left, upper, right, lower))

        loot = loot.convert('L')
        loot = ImageEnhance.Contrast(loot).enhance(2.0)
        # Binarize (convert to black and white)
        loot = loot.point(lambda x: 0 if x < 250 else 255)

        loot.save(filename)

        checkloot.result = reader.readtext(filename, allowlist='0123456789', detail=0)
        if len(checkloot.result) < 3:
            checkloot.result = ["0", "0", "0"] # Default values if OCR fails


def checktrophies(port):
    filename = f"Pictures/{port}trophies.png"
    screenshot(port, filename)
    print("captured")
    t.sleep(0.2)

    with Image.open(filename) as photo:
        (left, upper, right, lower) = (130, 160, 255, 210)
        trophies = photo.crop((left, upper, right, lower))

        trophies = trophies.convert('L')
        trophies = ImageEnhance.Contrast(trophies).enhance(2.0)
        trophies = trophies.point(lambda x: 0 if x < 240 else 255)

        trophies.save(filename)

        checktrophies.result = reader.readtext(filename, allowlist='0123456789', detail=0)

def get_pixel(x, y):
    if coords.REAL_W is not None and coords.REAL_H is not None:
        x, y = coords.scale(x, y)

    filename = screenshot()
    checkp = Image.open(filename).convert("RGB")
    return checkp.getpixel((x, y))


def check_pixel(x, y, target, tol=20):
    r, g, b = get_pixel(x, y)

    return (
        abs(r - target[0]) <= tol and
        abs(g - target[1]) <= tol and
        abs(b - target[2]) <= tol
    )

def checkpixel_old(port):
    filename = f"Pictures/{port}return.png"
    screenshot(port, filename)

    checkp = Image.open(filename)
    return checkp.getpixel((898, 909)) == checkp.getpixel((969, 938))

def checkpixelBB_old(x,y):
    filename = f"Pictures/{config.ADB_PORT}bb.png"
    screenshot(config.ADB_PORT, filename)
    checkp = Image.open(filename)
    return checkp.getpixel((x, y))


def calibrar_zoom(popup=None):
    # 1. Screenshot real
    filename = screenshot(tag="calibracion")
    img = cv2.imread(filename)

    if img is None:
        log("❌ Error leyendo la captura")
        return

    # 2. Cargar plantilla BH
    bh_template = cv2.imread("templates/bh.png")
    if bh_template is None:
        log("❌ No se encontró plantilla BH")
        return

    # 3. Matching multiescala
    scales = [0.8, 1.0, 1.2]
    best_val = -1
    best_match = None

    for s in scales:
        resized = cv2.resize(bh_template, None, fx=s, fy=s)
        res = cv2.matchTemplate(img, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val > best_val:
            best_val = max_val
            best_match = {
                "scale": s,
                "pos": max_loc,
                "size": resized.shape[:2]
            }

    if best_val < 0.45:
        log("❌ No se detectó el BH. Revisa el zoom.")
        return None

    # 4. Calcular datos de calibración
    result = {
        "pos": best_match["pos"],
        "size": best_match["size"],
        "scale": best_match["scale"],
        "confidence": best_val,
    }

    # 5. Estimar zoom
    bh_w = result["size"][1]
    if bh_w < 80:
        zoom = "mínimo"
    elif bh_w < 120:
        zoom = "medio"
    else:
        zoom = "alto"

    result["zoom"] = zoom

    # 6. Log
    log("✅ Calibración completada")
    log(f"BH detectado en {result['pos']}")
    log(f"Tamaño BH: {result['size']}")
    log(f"Zoom estimado: {result['zoom']}")
    log(f"Escala usada: {result['scale']}")

    return result

