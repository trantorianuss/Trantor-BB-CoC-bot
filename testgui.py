import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageDraw
import time
import random

import func as f

print("testgui.py starting")

# ============================================================
#  LOG
# ============================================================

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

# ============================================================
#  SCREENSHOT REAL
# ============================================================

def take_screenshot():
    """
    Usa la función real de func.py para hacer screenshot del emulador.
    """
    return f.screenshot()

# ============================================================
#  DIBUJAR LÍNEA EN IMAGEN
# ============================================================

def draw_line_on_image(filename, x1, y1, x2, y2, color=(0,255,0), width=4):
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    draw.line((x1, y1, x2, y2), fill=color, width=width)

    outname = filename.replace(".png", "_line.png")
    img.save(outname)
    return outname

# ============================================================
#  DIBUJAR CÍRCULO EN IMAGEN
# ============================================================

def draw_circle_on_image(filename, x, y, r, color=(255,0,0), width=4):
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)

    left   = x - r
    top    = y - r
    right  = x + r
    bottom = y + r

    draw.ellipse((left, top, right, bottom), outline=color, width=width)

    outname = filename.replace(".png", "_circle.png")
    img.save(outname)
    return outname

# ============================================================
#  FUNCIÓN TEST
# ============================================================



def test():
    log("=== TEST INICIADO ===")

    # 1) Screenshot real
    file1 = take_screenshot()
    log(f"Screenshot: {file1}")

    # 2) Abrir imagen y confirmar tamaño
    img = Image.open(file1)
    w, h = img.size
    log(f"Tamaño imagen: {w} x {h}")

    draw = ImageDraw.Draw(img)

    # ============================
    #  DIBUJAR LÍNEA 0,0 → w,h
    # ============================
    draw.line((0, 0, w, h), fill=(255, 0, 0), width=5)

    # ============================
    #  DIBUJAR CÍRCULO EN EL CENTRO
    # ============================
    cx, cy = w // 2, h // 2
    r = 100
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 outline=(0, 255, 0), width=5)

    # ============================
    #  DIBUJAR CUADRADO FIJO
    # ============================
    x1, y1 = 200, 200
    x2, y2 = 600, 600
    draw.rectangle((x1, y1, x2, y2),
                   outline=(0, 0, 255), width=5)

    # ============================
    #  DIBUJAR borde FIJO
    # ============================
    x1, y1 = 10, 10
    x2, y2 = w-10, h-10
    draw.rectangle((x1, y1, x2, y2),
                   outline=(0, 0, 255), width=5)

    # ============================
    #  DIBUJAR swipe
    # ============================
    cx, cy = w // 2, h // 2
    fx, fy = cx + 200, cy + 400
    draw.line((cx, cy, fx, fy), fill=(255, 255, 0), width=5)

    # ============================
    #  GUARDAR RESULTADO
    # ============================
    outname = file1.replace(".png", "_shapes.png")
    img.save(outname)
    log(f"Imagen final guardada en: {outname}")

    # ============================
    #  hacemos swipe real en el emulador
    # ============================
    dur_ms = random.randint(180, 350)
    f.swipe(cx, cy, fx, fy, dur_ms)
    log(f"Swipe ejecutado: {cx},{cy} -> {fx},{fy} dur={dur_ms}ms")

    # 1) Screenshot real
    file1 = take_screenshot()
    log(f"Screenshot: {file1}")

    # 2) Abrir imagen y confirmar tamaño
    img = Image.open(file1)
    w, h = img.size
    log(f"Tamaño imagen: {w} x {h}")

    draw = ImageDraw.Draw(img)

    # ============================
    #  DIBUJAR LÍNEA 0,0 → w,h
    # ============================
    draw.line((0, 0, w, h), fill=(255, 0, 0), width=5)

    # ============================
    #  DIBUJAR CÍRCULO en el tap
    # ============================
    cx, cy = 1270, 420
    r = 100
    draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                 outline=(0, 255, 0), width=5)

    # ============================
    #  GUARDAR RESULTADO 2
    # ============================
    outname = file1.replace(".png", "_shapes.png")
    img.save(outname)
    log(f"Imagen final guardada en: {outname}")

    log("=== TEST FINALIZADO ===")


# ============================================================
#  TKINTER GUI
# ============================================================

root = tk.Tk()
root.title("Test Swipe + Tap Visualizer")

btn = tk.Button(root, text="TEST", font=("Arial", 16), command=test)
btn.pack(pady=10)

log_box = ScrolledText(root, width=80, height=20, font=("Consolas", 10))
log_box.pack(padx=10, pady=10)

root.mainloop()
