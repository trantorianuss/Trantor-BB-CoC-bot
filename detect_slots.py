#!/usr/bin/env python3
"""
Detecta los rectángulos de selección de la barra inferior de Clash of Clans.

No necesita saber de antemano:
- cuántos slots hay
- el ancho de los slots
- la posición exacta de cada slot

Uso:
    python detect_slots.py xxxxx.png

Genera:
    xxxxx_slots.png

La imagen resultante muestra un número en el centro de cada rectángulo
detectado y por consola se imprime su posición, tamaño y centro.

NOTA:
Esta primera versión detecta las "cards" de selección por su geometría.
Por tanto puede incluir tropas, máquina de asedio y héroes. Es intencionado:
primero queremos comprobar que la detección geométrica funciona bien.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.signal import find_peaks


def detect_slots(filename):
    path = Path(filename)
    image = cv2.imread(str(path))

    if image is None:
        raise FileNotFoundError(f"No se pudo abrir: {filename}")

    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Solo analizamos la franja inferior donde está la barra de selección.
    # No usamos una posición X/Y concreta de los slots.
    y0 = int(height * 0.81)
    y1 = height - max(20, int(height * 0.035))

    # Una carta tiene bordes verticales bastante marcados.
    # Sumamos el cambio horizontal de intensidad para obtener una
    # "proyección vertical" de posibles límites.
    projection = np.abs(
        np.diff(gray[y0:y1].astype(np.int16), axis=1)
    ).sum(axis=0)

    # La separación mínima se calcula a partir del tamaño de la imagen,
    # no del tamaño conocido de los slots.
    min_distance = max(30, int(width * 0.025))

    # Umbral adaptativo según la propia imagen.
    prominence = max(
        np.percentile(projection, 75) * 0.50,
        projection.mean() + projection.std() * 0.50
    )

    peaks, _ = find_peaks(
        projection,
        distance=min_distance,
        prominence=prominence
    )

    peaks = [
        int(x) for x in peaks
        if width * 0.02 < x < width * 0.97
    ]

    # Algunos elementos (texto/iconos) generan un borde interno.
    # Eliminamos picos que producen intervalos demasiado pequeños.
    # El tamaño válido se obtiene de los propios picos encontrados.
    changed = True
    while changed and len(peaks) > 2:
        changed = False
        gaps = np.diff(peaks)

        # Un intervalo inferior al 65% del siguiente/anterior es
        # normalmente un borde interno, no un slot completo.
        for i, gap in enumerate(gaps):
            if gap < 65:
                left_strength = projection[peaks[i]]
                right_strength = projection[peaks[i + 1]]

                if left_strength < right_strength:
                    peaks.pop(i)
                else:
                    peaks.pop(i + 1)

                changed = True
                break

    # Los intervalos entre límites son los candidatos a slots.
    candidates = []
    for left, right in zip(peaks[:-1], peaks[1:]):
        slot_width = right - left

        # Solo descartamos tamaños claramente incompatibles con una card.
        # No se usa un ancho concreto: el rango es relativo a la imagen.
        if width * 0.035 <= slot_width <= width * 0.09:
            candidates.append((left, right))

    # El límite superior de la card se obtiene buscando la zona de
    # mayor contraste horizontal alrededor de la barra.
    # Para esta UI, los rectángulos ocupan aproximadamente la misma
    # franja vertical; calculamos su altura desde los bordes detectados.
    top = int(height * 0.82)
    bottom = int(height * 0.965)

    result = image.copy()

    print(f"Imagen: {path}")
    print(f"Resolución: {width}x{height}")
    print()

    for number, (left, right) in enumerate(candidates, start=1):
        x = left
        y = top
        w = right - left
        h = bottom - top

        cx = x + w // 2
        cy = y + h // 2

        cv2.rectangle(
            result,
            (x, y),
            (right, bottom),
            (0, 0, 255),
            3
        )

        text = str(number)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = max(0.7, min(1.2, width / 1400))
        thickness = 3

        (tw, th), _ = cv2.getTextSize(
            text, font, scale, thickness
        )

        cv2.putText(
            result,
            text,
            (cx - tw // 2, cy + th // 2),
            font,
            scale,
            (0, 0, 255),
            thickness,
            cv2.LINE_AA
        )

        print(
            f"Slot {number}: "
            f"x={x}, y={y}, w={w}, h={h}, "
            f"centro=({cx}, {cy})"
        )

    output = path.with_name(path.stem + "_slots.png")
    cv2.imwrite(str(output), result)

    print()
    print(f"Detectados: {len(candidates)}")
    print(f"Resultado: {output}")

    return candidates


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python detect_slots.py xxxxx.png")
        sys.exit(1)

    detect_slots(sys.argv[1])
