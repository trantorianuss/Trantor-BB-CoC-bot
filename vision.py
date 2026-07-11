import cv2
import os
import func as f
from func import screenshot
from func import find_template_multiscale  # tu función real

print(">>> vision.py starting")

def print_resultados(resultados):
    """
    Imprime los resultados de detectar_puntos() en una línea por template.
    Formato:
    nombre → None
    nombre → pos=(x, y), size=(w, h), conf=0.98, scale=1.0
    """

    for nombre, data in resultados.items():
        if data is None:
            f.log(f"{nombre} → None")
        else:
            x, y = data["position"]
            w, h = data["size"]
            conf = data["confidence"]
            scale = data["scale"]

            f.log(f"{nombre} → pos=({x}, {y}), size=({w}, {h}), conf={conf:.4f}, scale={scale}")


def detectar_puntos(templates, scales = (0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15)
, threshold=0.80, debug=False):
    """
    Detecta múltiples plantillas en una sola captura.
    Devuelve un diccionario donde cada clave es el nombre de la plantilla
    y el valor es None (si no se detecta) o un dict con los datos de detección.

    Si debug=True:
        - Guarda recortes individuales de cada detección
        - Guarda una captura anotada con rectángulos y nombres
    """

    # 1. Captura
    screenshot_path = screenshot("detectar_puntos")
    img = cv2.imread(screenshot_path)

    if img is None:
        f.log("❌ No se pudo cargar la captura")
        return {}

    resultados = {}

    # Crear carpeta debug si hace falta
    if debug and not os.path.exists("debug"):
        os.makedirs("debug")

    # Copia para dibujar anotaciones
    annotated = img.copy()

    # 2. Recorrer todas las plantillas
    for tpl_path in templates:

        nombre = os.path.basename(tpl_path).replace(".png", "")
        f.log(f"🔍 Buscando {nombre} ...")

        result = find_template_multiscale(
            screenshot_path,
            tpl_path,
            scales=scales,
            threshold=threshold
        )

        # 3. Guardar resultado
        if not result:
            resultados[nombre] = None
            continue

        # Datos de detección
        x, y = result["position"]
        w, h = result["size"]

        resultados[nombre] = {
            "position": (x, y),
            "size": (w, h),
            "confidence": result["confidence"],
            "scale": result["scale"]
        }

        # ============================
        # DEBUG: Guardar recorte
        # ============================
        if debug:
            crop = img[y:y+h, x:x+w]
            crop_path = f"debug/{nombre}_crop.png"
            cv2.imwrite(crop_path, crop)

            # ============================
            # DEBUG: Dibujar rectángulo
            # ============================
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                nombre,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    # ============================
    # DEBUG: Guardar imagen anotada
    # ============================
    if debug:
        annotated_path = "debug/detecciones_annotated.png"
        cv2.imwrite(annotated_path, annotated)
        f.log(f"🖼 Imagen anotada guardada en {annotated_path}")

    return resultados



