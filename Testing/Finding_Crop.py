from MeasureWorld import *

s = Sensor()
s.initialise_stream()
while True:
    _, f = s.video_stream.read()
    if f is None: continue
    crop_img = s.get_normalized_data(f)


    cv2.imshow('a', crop_img)


    up_end = (input("Enter up 1: "), input("Enter up 2: "))
    low_end = (input("Enter low 1: "), input("Enter low 2: "))

    s.set_calibration_data(up_end, low_end)

    while True:
        k = cv2.waitKey(5) & 0xF
        if k == 27:
            break
cv2.destroyAllWindows()
s.stop_stream()
