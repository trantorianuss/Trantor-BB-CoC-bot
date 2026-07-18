import cv2
import numpy as np
from calibration import load_calibration


def extract_features(image):

    orb = cv2.ORB_create(1000)

    keypoints, descriptors = orb.detectAndCompute(image, None)

    return keypoints, descriptors


def show_keypoints(image, keypoints):

    img = cv2.drawKeypoints(
        image,
        keypoints,
        None,
        color=(0,255,0)
    )

    cv2.imshow("ORB", img)


def match_features(img1, kp1, des1,
                   img2, kp2, des2):

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    matches = bf.knnMatch(des1, des2, k=2)

    good = []

    for pair in matches:

        if len(pair) < 2:
            continue

        m, n = pair

        if m.distance < 0.75 * n.distance:
            good.append(m)

    print("Good matches:", len(good))

    img = cv2.drawMatches(
        img1,
        kp1,
        img2,
        kp2,
        good,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    cv2.imshow("Matches", img)

    return good


def main():

    cal = load_calibration()

    roi_rect = tuple(cal["roi"])
    cart = tuple(cal["cart_position"])

    roi_image = cv2.imread("calibration/calibration_roi.png")
    screenshot = cv2.imread("calibration/segunda_captura.png")

    kp1, des1 = extract_features(roi_image)
    kp2, des2 = extract_features(screenshot)

    print("ROI:", len(kp1))
    print("Screenshot:", len(kp2))

    show_keypoints(roi_image, kp1)

    good = match_features(
        roi_image,
        kp1,
        des1,
        screenshot,
        kp2,
        des2
    )

    src_pts = np.float32([
        kp1[m.queryIdx].pt
        for m in good
    ]).reshape(-1, 1, 2)

    dst_pts = np.float32([
        kp2[m.trainIdx].pt
        for m in good
    ]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(
        src_pts,
        dst_pts,
        cv2.RANSAC,
        5.0
    )

    print(H)

    h, w = roi_image.shape[:2]

    corners = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ]).reshape(-1, 1, 2)

    corners2 = cv2.perspectiveTransform(
        corners,
        H
    )

    cv2.polylines(
        screenshot,
        [corners2.astype(int)],
        True,
        (0,255,0),
        3
    )

    scale = 0.6




    # Buscar el carro en la imagen de la captura

    print("ROI:", roi_rect)
    print("width:", w, "height:", h)
    print("Cart:", cart)

    cart = (
        cart[0] - roi_rect[0],
        cart[1] - roi_rect[1]
    )
    print("Cart-ROI:", cart)

    cart_pt = np.float32([
        [cart]
    ]).reshape(-1, 1, 2)

    cart2 = cv2.perspectiveTransform(
        cart_pt,
        H
    )

    x, y = cart2[0][0]

    x = int(x)
    y = int(y)

    cv2.drawMarker(
        screenshot,
        (x, y),
        (0, 0, 255),
        markerType=cv2.MARKER_CROSS,
        markerSize=40,
        thickness=3
    )

    # transformacion final

    preview = cv2.resize(
        screenshot,
        None,
        fx=scale,
        fy=scale
    )

    cv2.namedWindow("ROI encontrado", cv2.WINDOW_NORMAL)
    cv2.imshow("ROI encontrado", preview)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

    