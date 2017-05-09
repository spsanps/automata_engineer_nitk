import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap.read()

while True:
    _, frame = cap.read()


    lower_blue = np.array([25, 30, 25], dtype=np.uint8)
    upper_blue = np.array([60, 255, 250], dtype=np.uint8)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    edges = cv2.Canny(mask, 100, 200)

    im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    try:
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        points = cnt[:, 0, :]
        xleft = min(points[:, 0])
        xright = max(points[:, 0])
        yup = min(points[:, 1])
        ydown = max(points[:, 1])
        print xleft, xright, yup, ydown
        cv2.drawContours(frame, [cnt], -1, (125, 125, 0), 3)

    except:
        pass
    cv2.imshow("window title", frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
