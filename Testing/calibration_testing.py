import cv2
from zoom_in import Sensor
import numpy as np

s = Sensor()
s.initialise_stream()

_, frame = s.video_stream.read()

lower_green = np.array([25, 30, 25], dtype=np.uint8)
upper_green = np.array([60, 255, 250], dtype=np.uint8)
#print frame
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_green, upper_green)
edges = cv2.Canny(mask, 100, 200)

im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
areas = [cv2.contourArea(c) for c in contours]

#cv2.drawContours(edges,contours,-1,(125,125,0),3)
max_index = np.argmax(areas)
cnt = contours[max_index]
cv2.drawContours(edges,[cnt],-1,(255,125,0),3)
points = cnt[:, 0, :]
x_left = min(points[:, 0]) + 20
x_right = max(points[:, 0]) - 20
y_up = min(points[:, 1]) + 20
y_down = max(points[:, 1]) - 20
s.set_calibration_data((x_left, y_up), (x_right, y_down))
f = s.get_normalized_data(frame)

print x_left, x_right, y_up, y_down
cv2.imshow('res', f)

while True:
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
