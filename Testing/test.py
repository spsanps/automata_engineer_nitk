import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap.read()

while True:
    _, frame = cap.read()

    #if frame is None: continue

    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (9,9),None)

    # If found, add object points, image points (after refining them)
    cv2.imshow('res', gray)
    print corners

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()