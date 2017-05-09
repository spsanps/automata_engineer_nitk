from time import time

import cv2
from matplotlib import pyplot as plt

c = cv2.VideoCapture(0)
_, img = c.read()

img = cv2.resize(img, (64 * 2, 48 * 2))

t1 = time()

img = cv2.Canny(img, 190, 200)

img = cv2.dilate(img, None, iterations=3)
img = cv2.erode(img, None, iterations=1)

image, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

t2 = time()

for c in contours:
    M = cv2.moments(c)
    try:
        cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
        cv2.circle(img, (cx, cy), 1, 255, -1)
    except:
        pass

try:
    cv2.drawContours(img, contours[0], 10, 255, -1)
except:
    pass
# cv2.imshow('frame', f)



cv2.destroyAllWindows()
# c.release()

print t2 - t1

plt.subplot(121), plt.imshow(img)
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122), plt.imshow(img, cmap='gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.show()
