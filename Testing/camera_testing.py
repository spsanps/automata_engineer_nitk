import cv2
import numpy as np

cap = cv2.VideoCapture(1)
#cap.set(3, 64*15)
#cap.set(4, 48*15)
cap.read()

while True:
    _, frame = cap.read()
    cv2.imshow('res',frame)
    cv2.imwrite("image_proefwoeicessed.jpg", frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
