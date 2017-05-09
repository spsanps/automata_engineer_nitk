__author__ = 'sanps'

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here

    # frame = cv2.blur(frame,(3,3))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    thresh = cv2.inRange(hsv, np.array((17, 149, 107)), np.array((22, 240, 167)))

    # thresh2 = thresh.copy()

    # Find contours in the threshold image
    image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


    # Finding contour with maximum area and store it as best_cnt
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    # Finding centroids of best_cnt and draw a circle there
    try:
        best_cnt
    except:
        best_cnt = (50, 50)

    M = cv2.moments(best_cnt)
    cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
    cv2.circle(frame, (cx, cy), 10, 255, -1)

    try:
        cv2.drawContours(frame, contours, 10, 255, -1)
    except:
        pass
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
