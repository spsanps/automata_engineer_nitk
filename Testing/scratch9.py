import cv2
import numpy as np

lower = [15, 15, 50]
upper = [60, 60, 250]

lower = np.array(lower, dtype="uint8")
upper = np.array(upper, dtype="uint8")

# find the colors within the specified boundaries and apply
# the mask
cap = cv2.VideoCapture(0)
while True:
    _, image = cap.read()
    mask = cv2.inRange(image, lower, upper)
    mask = cv2.dilate(mask, None, iterations=9)
    mask = cv2.erode(mask, None, iterations=1)

    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    best_cnt = None
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    contours = [best_cnt]

    if best_cnt is not None: cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    cv2.imshow('frame', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
