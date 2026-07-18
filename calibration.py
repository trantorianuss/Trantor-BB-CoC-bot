import json
import cv2
import numpy as np


# ==========================================================
# Variables globales
# ==========================================================

image = None
clone = None

roi = None
boat = None
cart = None

dragging = False
x0 = y0 = 0

mode = "roi"       # roi -> boat -> cart


# ==========================================================
# Entrada principal
# ==========================================================

def run(image_path):

    print("run()")

    global image, clone, mode

    image = cv2.imread(image_path)

    if image is None:
        print("No se pudo abrir la imagen")
        return

    clone = image.copy()

    mode = "roi"
    print("roi")

    cv2.namedWindow("Calibration")
    cv2.setMouseCallback("Calibration", mouse_callback)

    while True:

        cv2.imshow("Calibration", image)

        key = cv2.waitKey(20)

        if key == 13:      # ENTER
            save()
            break

        elif key == 27:    # ESC
            break

    cv2.destroyAllWindows()


# ==========================================================
# Ratón
# ==========================================================

def mouse_callback(event, x, y, flags, param):

    global image
    global clone
    global dragging
    global x0, y0
    global roi
    global boat
    global cart
    global mode

    # ---------------- ROI ----------------

    if mode == "roi":

        if event == cv2.EVENT_LBUTTONDOWN:

            x0 = x
            y0 = y
            dragging = True

        elif event == cv2.EVENT_MOUSEMOVE and dragging:

            image = clone.copy()

            cv2.rectangle(
                image,
                (x0, y0),
                (x, y),
                (0, 255, 0),
                2
            )

        elif event == cv2.EVENT_LBUTTONUP:

            dragging = False

            roi = (
                min(x0, x),
                min(y0, y),
                abs(x - x0),
                abs(y - y0)
            )

            print("ROI:", roi)

            mode = "boat"

            print("Haz click sobre el BARCO")


    # ---------------- BOAT ----------------

    elif mode == "boat":

        if event == cv2.EVENT_LBUTTONDOWN:

            boat = (x, y)

            print("Boat:", boat)

            mode = "cart"

            print("Haz click sobre el CARRO")


    # ---------------- CART ----------------

    elif mode == "cart":

        if event == cv2.EVENT_LBUTTONDOWN:

            cart = (x, y)

            print("Cart:", cart)

            mode = "done"

            print("Pulsa ENTER para guardar")


# ==========================================================
# Guardar calibración
# ==========================================================

def save():

    global roi
    global clone

    if roi is None:
        print("No hay ROI")
        return

    if boat is None:
        print("No hay barco")
        return

    if cart is None:
        print("No hay carro")
        return

    x, y, w, h = roi

    crop = clone[y:y+h, x:x+w]

    keypoints, descriptors = extract_features(crop)

    print("Keypoints:", len(keypoints))

    save_calibration(
        crop,
        descriptors
    )


# ==========================================================
# ORB
# ==========================================================

def extract_features(image):

    orb = cv2.ORB_create(1000)

    keypoints, descriptors = orb.detectAndCompute(
        image,
        None
    )

    return keypoints, descriptors


# ==========================================================
# Guardar a disco
# ==========================================================

def save_calibration(crop, descriptors):

    data = {

        "roi": roi,
        "boat": boat,
        "cart": cart

    }

    with open("calibration/calibration.json", "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

    cv2.imwrite(
        "calibration/calibration_roi.png",
        crop
    )

    np.save(
        "calibration/calibration_descriptors.npy",
        descriptors
    )

    print("Calibración guardada")

# ==========================================================
# Read Calibration
# ==========================================================

def load_calibration():

    with open("calibration/calibration.json", "r") as f:
        data = json.load(f)

    return data