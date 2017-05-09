import cv2
import numpy as np

cap = cv2.VideoCapture()

while True:
    # Read the frames
    _, frame = cap.read()

    # Smooth it
    frame = cv2.blur(frame, (3, 3))

    # Convert to hsv and find range of colors
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, np.array((0, 80, 80)), np.array((20, 255, 255)))

    thresh2 = thresh.copy()

    # Find contours in the threshold image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Finding contour with maximum area and store it as best_cnt
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    # Finding centroids of best_cnt and draw a circle there
    M = cv2.moments(best_cnt)
    cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
    cv2.circle(frame, (cx, cy), 10, 255, -1)
