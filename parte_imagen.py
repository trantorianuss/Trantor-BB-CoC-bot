import cv2

def dividir_en_bloques_con_cuadricula(img, bloque_w=120, bloque_h=90, y_inicio=100, filas=5):
    """
    Divide la imagen en bloques de tamaño bloque_w x bloque_h.
    Empieza en y_inicio y genera 'filas' filas de bloques.
    
    Devuelve:
        bloques: lista de dicts con x, y, img
        cuadriculada: imagen original con líneas dibujadas simulando los cortes
    """

    h, w = img.shape[:2]
    bloques = []

    # Copia para dibujar la cuadrícula
    cuadriculada = img.copy()

    # Coordenada Y inicial
    y = y_inicio

    for fila in range(filas):
        if y + bloque_h > h:
            break

        x = 0
        while x + bloque_w <= w:
            # Extraer bloque
            bloque = img[y:y+bloque_h, x:x+bloque_w]

            bloques.append({
                "x": x,
                "y": y,
                "img": bloque
            })

            # Dibujar rectángulo en la imagen cuadriculada
            cv2.rectangle(
                cuadriculada,
                (x, y),
                (x + bloque_w, y + bloque_h),
                (0, 255, 0),
                1
            )

            x += bloque_w

        y += bloque_h

    return bloques, cuadriculada


img = cv2.imread("screenshots/captura.png")

bloques, cuadriculada = dividir_en_bloques_con_cuadricula(img)

cv2.imwrite("debug/captura_cuadriculada.png", cuadriculada)

for b in bloques:
    print(f"Bloque en x={b['x']} y={b['y']}")
    cv2.imwrite(f"debug/bloque_{b['x']}_{b['y']}.png", b["img"])

print(f"Total bloques: {len(bloques)}")

