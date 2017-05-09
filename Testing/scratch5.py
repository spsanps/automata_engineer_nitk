__author__ = 'sanps'

__author__ = 'sanps'

from time import time

import cv2

cap = cv2.VideoCapture(0)

t = 0
i = 0

while True:
    # Capture frame-by-frame
    i += 1
    _, frame = cap.read()

    o = frame

    frame = cv2.resize(frame, (64 * 2, 48 * 2))

    t1 = time()

    frame = cv2.Canny(frame, 150, 200)

    frame = cv2.dilate(frame, None, iterations=2)

    fd = frame
    frame = cv2.erode(frame, None, iterations=1)

    fe = frame
    image, contours, hierarchy = cv2.findContours(frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    t2 = time()

    t += t2 - t1

    # thresh2 = thresh.copy()

    # Find contours in the threshold image


    for c in contours:
        try:
            M = cv2.moments(c)
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            # cv2.circle(o, (cx * 640 / (64 * 2), cy * 480 / (48 * 2)), 5, 255, -1)
            cv2.circle(o, cx, cy, 5, 255, -1)
        except:
            pass

    try:
        pass
        # cv2.drawContours(frame, contours[0], 10, 255, -1)
    except:
        pass
    # Display the resulting frame
    cv2.imshow('frame', o)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print t, t / i

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
