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

    global dragging, x0, y0, image, clone, roi

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


def save_OLD():

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

def save():

    global roi, clone

    if roi is None:
        print("No hay calibración")
        return

    x, y, w, h = roi

    crop = clone[y:y+h, x:x+w]

    keypoints, descriptors = extract_features(crop)

    print("Keypoints encontrados:", len(keypoints)) 


    img = cv2.drawKeypoints(
    crop,
    keypoints,
    None,
    color=(0, 255, 0)
    )

    cv2.imshow("ORB", img)
    cv2.waitKey(0)
    # Comento porque daba error si doy en la X
    # cv2.destroyWindow("ORB")


    image2 = cv2.imread("segunda_captura.png")

    kp2, des2 = extract_features(image2)

    match_features(
        crop,
        keypoints,
        descriptors,
        image2,
        kp2,
        des2
    )



def extract_features(crop):

    orb = cv2.ORB_create(1000)

    keypoints, descriptors = orb.detectAndCompute(crop, None)

    return keypoints, descriptors


def match_features(img1, kp1, des1, img2, kp2, des2):

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    matches = bf.knnMatch(des1, des2, k=2)

    good = []

    for pair in matches:

        if len(pair) < 2:
            continue

        m, n = pair

        if m.distance < 0.75 * n.distance:
            good.append(m)

    print("Matches encontrados:", len(good))

    img_matches = cv2.drawMatches(
        img1,
        kp1,
        img2,
        kp2,
        good,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    zoom = 3.0

    img_zoom = cv2.resize(
        img_matches,
        None,
        fx=zoom,
        fy=zoom,
        interpolation=cv2.INTER_NEAREST
    )

    cv2.imshow("Matches", img_zoom)

    cv2.imshow("Matches", img_matches)
    cv2.waitKey(0)


