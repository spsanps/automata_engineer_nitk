import cv2
import numpy as np

cap = cv2.VideoCapture(1)
cap.read()

while True:
    _, frame = cap.read()

    # define range of blue color in HSV
    #frame = cv2.resize(frame, (64 * 2, 48 * 2))

    #info = s.get_all_information(s.identity_robot(None, frame))
    #if info != -1:
    #    print info[0], np.rad2deg(info[1])

    lower_blue = np.array([50, 15, 25], dtype=np.uint8)
    upper_blue = np.array([255, 175, 250], dtype=np.uint8)

    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(frame, lower_blue, upper_blue)


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
