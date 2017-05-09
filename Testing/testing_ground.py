import cv2
import numpy as np
frame = cv2.imread('image_processed.jpg')
"""

lower_blue = np.array([95, 30, 30], dtype=np.uint8)
upper_blue = np.array([140, 250, 250], dtype=np.uint8)
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_blue, upper_blue)
res = cv2.bitwise_and(frame, frame, mask=mask)
"""

cv2.imshow('res', res)
while True:
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
