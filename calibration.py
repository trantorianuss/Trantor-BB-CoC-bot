import json
import cv2

# Variables globales del módulo
image = None
clone = None

roi = None

boat = None
cart = None

dragging = False
x0 = y0 = 0
x1 = y1 = 0


def run(image_path):

    global image, clone

    image = cv2.imread(image_path)

    if image is None:
        print("No se pudo abrir la imagen")
        return

    clone = image.copy()

    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_callback)

    while True:

        cv2.imshow("Calibration", image)

        key = cv2.waitKey(20)

        if key == 13:          # ENTER
            save()
            break

        elif key == 27:        # ESC
            break

    cv2.destroyAllWindows()


def mouse_callback(event, x, y, flags, param):

    global dragging, x0, y0

    # Aquí irá toda la lógica:
    #
    # - Dibujar el rectángulo
    # - Marcar barco
    # - Marcar carro
    #

    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)

        x0 = x
        y0 = y

        dragging = True
    
    elif event == cv2.EVENT_MOUSEMOVE and dragging:
        image = clone.copy()    

        cv2.rectangle(image, (x0, y0), (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        print(x, y)
        dragging = False

        roi = (
            min(x0,x),
            min(y0,y),
            abs(x-x0),
            abs(y-y0)
            )
        
        print("ROI:", roi)


def save():

    if roi is None:
        print("No hay calibración")
        return

    data = {
        "roi": roi,
        "boat": boat,
        "cart": cart
    }

    with open("calibration.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Calibración guardada")