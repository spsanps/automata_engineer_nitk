import cv2
import numpy as np
from time import time

cap = cv2.VideoCapture(0)

while True:
    # Read the frames
    _, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(img, 5)
    c_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


    t2 = time()
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=55, param2=35, minRadius=3, maxRadius=100)
    t1 = time()
    print t2 - t1

    try:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(c_img, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(c_img, (i[0], i[1]), 2, (0, 0, 255), 3)

    except:
        pass

    cv2.imshow('frame', c_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
