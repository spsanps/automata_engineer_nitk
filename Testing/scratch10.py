import cv2
import numpy as np
# import cv2.cv
# find the colors within the specified boundaries and apply
# the mask
cap = cv2.VideoCapture(0)
from MeasureWorld import Sensor
from time import time

s = Sensor()


def circled(f):
    f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    f = cv2.erode(f, None, iterations=1)
    # f = cv2.dilate(f, None, iterations=1)
    img = cv2.medianBlur(f, 5)
    c_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 10, param1=50, param2=25, minRadius=1, maxRadius=30)

    try:
        circles = np.uint16(np.around(circles))
        # print circles[0, :, :-1]
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(c_img, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(c_img, (i[0], i[1]), 2, (0, 0, 255), 3)
    except:
        pass
    return c_img

t1, t2 = 0, 0

while True:
    _, frame = cap.read()

    # define range of blue color in HSV
    frame = cv2.resize(frame, (64 * 2, 48 * 2))

    #info = s.get_all_information(s.identity_robot(None, frame))
    #if info != -1:
    #    print info[0], np.rad2deg(info[1])

    lower_blue = np.array([25, 30, 25], dtype=np.uint8)
    upper_blue = np.array([60, 255, 250], dtype=np.uint8)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)


    # mask = cv2.erode(mask, None, iterations=1)
    # mask = cv2.dilate(mask, None, iterations=1)
    # 9mask = cv2.blur(mask, (2, 2))

    res = cv2.bitwise_and(frame, frame, mask=mask)

    # cv2.imshow('frame', frame)
    # cv2.imshow('mask', mask)
    cv2.imshow('res', res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
