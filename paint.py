import random
from PIL import Image, ImageDraw

import func as f

print(">>> Paint.py starting")


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


def paint_test():
    f.log("=== Dibujo INICIADO ===")

    # 1) Screenshot real
    file1 = take_screenshot()
    f.log(f"Screenshot: {file1}")

    # 2) Abrir imagen y confirmar tamaño
    img = Image.open(file1)
    w, h = img.size
    f.log(f"Tamaño imagen: {w} x {h}")

    draw = ImageDraw.Draw(img)

    # ============================
    #  DIBUJAR LÍNEA 0,0 → w,h
    # ============================
    # draw.line((0, 0, w, h), fill=(255, 0, 0), width=5)

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
    # x1, y1 = 200, 200
    # x2, y2 = 600, 600
    # draw.rectangle((x1, y1, x2, y2),
    #                outline=(0, 0, 255), width=5)

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
    cx, cy = 1450, 150
    fx, fy = 1050, 550
    draw.line((cx, cy, fx, fy), fill=(255, 255, 0), width=5)

    # ============================
    #  GUARDAR RESULTADO
    # ============================
    outname = file1.replace(".png", "_shapes.png")
    img.save(outname)
    f.log(f"Imagen final guardada en: {outname}")


    f.log("=== Dibujo FINALIZADO ===")