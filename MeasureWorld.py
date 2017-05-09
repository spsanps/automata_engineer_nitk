from random import random
from time import time, sleep
from itertools import combinations
import threading

import pygame

from Misc import *

MAX_POS = 1000
MAX_ANGLE = 360

INPUT_ERROR = 1.0 / 100
INPUT_SYSTEMATIC_ERROR = 0 / 100


class VirtualSensor:
    def __init__(self):
        self.data = None

        self.new_data_available = False
        self.running = False
        self.world = None

        self.rate = 20

    def set_stream(self, w):
        self.world = w

    def measure_world_data(self):
        """Adds error to input before returning"""

        a_pos, a_angle = self.world.get_current_data()
        time_at_get = time()

        # print a_pos, a_angle

        e = INPUT_ERROR * 2  # Average error has to stay at given value

        e_pos = a_pos + a_pos * (2 * random() - 1) / 1000
        e_angle = a_angle + a_angle * (2 * random() - 1) / 1000
        # random() is used to get a fraction of max error values

        # print e_pos, e_angle
        return e_pos, e_angle, time_at_get

    def start_sensor(self):
        clock = pygame.time.Clock()

        def sensor_existence():
            while self.running:
                self.data = self.measure_world_data()
                self.new_data_available = True
                clock.tick(self.rate)

        t = threading.Thread(target=sensor_existence)
        t.setDaemon(True)

        self.running = True

        t.start()

    def stop_sensor(self):
        self.running = False


class Sensor(VirtualSensor):
    def __init__(self):
        VirtualSensor.__init__(self)

        del self.world
        del self.rate
        # del self.measure_world_data

        self.calibration_data = ((0, 0), (100, 100))
        self.grid_size = 48 * 2
        self.cropped_size = 200
        self.last_position = None
        self.small_search_area = None
        self.video_stream = None
        self.max_rate = 30

        # Detection ----------------------------------------------------------------------------------------------------
        self.lower_blue = np.array([98, 160, 50], dtype=np.uint8)
        self.upper_blue = np.array([137, 250, 250], dtype=np.uint8)

    def initialise_stream(self):
        self.video_stream = cv2.VideoCapture(1)
        self.video_stream.set(3, 640)
        self.video_stream.set(4, 480)
        # self.video_stream.set(5, 30)

    def stop_stream(self):
        self.video_stream.release()

    def calibrate(self):
        raise NotImplementedError

    def save_calibration_data(self):
        raise NotImplementedError

    def load_calibration_data(self):
        raise NotImplementedError

    def map_to_world(self, p):
        n, m = p
        y = self.grid_size - m
        x = n
        return np.array((x, y)) * 2.4384 / self.grid_size

    def map_from_world(self, p):
        p = np.array(p)
        x, y = p / 2.4382 * self.grid_size
        m = int(round(self.grid_size - y))
        n = int(round(x))
        return n, m

    def set_calibration_data(self, p1, p2):
        self.calibration_data = (p1, p2)
        self.grid_size = abs(sum(tuple(np.array(p1) - np.array(p2))) / 2)
        self.cropped_size = int(1.25 / 8 * self.grid_size)

    def get_normalized_data(self, f):
        if self.calibration_data is None: return f
        # if f is None:
        #    f = self.video_stream.read()[1]
        p1, p2 = self.calibration_data
        x1, y1 = p1
        x2, y2 = p2
        # print x1, x2, y1, y2
        crop_img = f[y1:y2, x1:x2]

        return crop_img

        # raise NotImplementedError

    def find_red_cell(self):
        """
        Finds the red cell by averaging position of 10 frames
        :return:
        """
        lower = np.array([0, 100, 25], dtype=np.uint8)
        upper = np.array([25, 255, 255], dtype=np.uint8)


        # t1 = time()

        counter = 0
        best_contours = []
        while counter < 10:
            _, image = self.video_stream.read()
            image = self.get_normalized_data(image)
            mask = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(image, lower, upper)
            mask = cv2.dilate(mask, None, iterations=9)
            mask = cv2.erode(mask, None, iterations=1)

            im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            max_area = 0
            best_cnt = None
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    best_cnt = cnt

            if best_cnt is not None:
                best_contours.append(best_cnt)
                # print counter, len(best_contours)
                counter += 1

        # t2 = time()

        # print t2 - t1

        points = [center_of_contour(c) for c in best_contours]
        mean_point = sum(points) / len(points)
        distance_to_mean = lambda point: distance(point, mean_point)

        points.sort(key=distance_to_mean)
        # print len(points)
        points = points[: -5]
        position = sum(points) / len(points)

        """
        _, image = self.video_stream.read()
        cx, cy = position
        print cx, cy
        cv2.circle(image, (cx, cy), 3, 255, -1)
        while True:
            cv2.imshow('frame', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        """
        return self.map_to_world(position)

    def get_last_position(self):
        return self.last_position

    def find_initial_position(self):
        """
        Finds the red cell by averaging position of 10 frames
        :return:
        """
        lower = [25, 75, 75]
        upper = [40, 255, 250]
        
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # t1 = time()

        counter = 0
        best_contours = []
        while counter < 10:
            _, image = self.video_stream.read()
            image = self.get_normalized_data(image)
            mask = cv2.inRange(image, lower, upper)
            mask = cv2.dilate(mask, None, iterations=9)
            mask = cv2.erode(mask, None, iterations=1)

            im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            max_area = 0
            best_cnt = None
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    best_cnt = cnt

            if best_cnt is not None:
                best_contours.append(best_cnt)
                # print counter, len(best_contours)
                counter += 1

        # t2 = time()

        # print t2 - t1

        points = [center_of_contour(c) for c in best_contours]
        mean_point = sum(points) / len(points)
        distance_to_mean = lambda point: distance(point, mean_point)

        points.sort(key=distance_to_mean)
        # print len(points)
        points = points[: -5]
        position = sum(points) / len(points)

        """
        _, image = self.video_stream.read()
        cx, cy = position
        print cx, cy
        cv2.circle(image, (cx, cy), 3, 255, -1)
        while True:
            cv2.imshow('frame', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        """
        # print position

        if position is None or type(position) is int: return -1
        # print position
        # self.last_position = self.map_from_world(position[0])
        self.last_position = position

        return self.map_to_world(position)

    def find_initial_position_without_green(self):
        # print 'Started'
        """
        _, f = self.video_stream.read()
        f = self.get_normalized_data(f)
        cell_size = int(round(self.grid_size / 8.0))
        flag = False
        position = None
        for i in xrange(0, 8):
            for j in xrange(0, 8):
                crop_img = f[j * cell_size:(j + 1) * cell_size, i * cell_size:(i + 1) * cell_size]
                points = self.identity_robot(None, crop_img, auto_thersh=False)
                if points != -1:
                    bigger_points = [(i * cell_size + p[0], j * cell_size + p[1]) for p in points]
                    position = self.get_all_information(points)
                    flag = True
                    break
            if flag: break

        """
        list_data = []
        counter = 0
        while counter < 7:
            _, f = self.video_stream.read()
            f = self.get_normalized_data(f)
            points = self.identity_robot(None, f)
            if points == -1: continue
            data = self.get_all_information(points)
            if data == -1: continue
            list_data.append(data)
            counter += 1

        some_x, theta = zip(*list_data)

        mean_point = sum(some_x) / len(some_x)
        distance_to_mean = lambda point: distance(point, mean_point)

        list(some_x).sort(key=distance_to_mean)
        some_x = some_x[: -2]
        position = sum(some_x) / len(some_x)

        if position is None or type(position) is int: return -1
        # print position
        # self.last_position = self.map_from_world(position[0])
        self.last_position = self.map_from_world(position)
        return position

    def identity_robot(self, f):#position, f, auto_thersh=True):
        """
        Searches for robot in the latest position and
        returns 3 contours around 3 distinct colored parts of the robot.
        :param position: if position is None search entire area
        :param f: frame
        """
        """        # print f
        if position is None:
            cropped_image = f
        else:
            x, y = position
            y1, y2, = y - self.cropped_size / 2, self.cropped_size / 2 + y,
            x1, x2 = x - self.cropped_size / 2, x + self.cropped_size / 2

            data = np.array([y1, y2, x1, x2])
            data[data < 0] = 0
            y1, y2, x1, x2 = data

            cropped_image = f[y1:y2, x1:x2]
        """
        """cv2.imshow('a', cropped_image)
        while True:
            k = cv2.waitKey(5) & 0xFF
            if k == 27: break
        """
        lower_blue = np.array([98, 160, 50], dtype=np.uint8)
        upper_blue = np.array([137, 250, 250], dtype=np.uint8)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)


        # mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=3)



        hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image to get only blue colors
        # print hsv, self.lower_blue, cropped_image
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        mask = cv2.dilate(mask, None, iterations=3)

        img = cv2.medianBlur(mask, 5)

        p2 = 25
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 10, param1=50, param2=p2, minRadius=1, maxRadius=30)

        # print circles

        if circles is None:
            circles = []
        else:
            circles = circles[0, :]

        if auto_thersh:
            while len(circles) > 4:
                circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 10, param1=50, param2=p2, minRadius=1,
                                           maxRadius=30)
                if circles is None:
                    circles = []
                else:
                    circles = circles[0, :]
                p2 += 1
                if p2 > 35: return -1

            while len(circles) < 4:
                circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 10, param1=50, param2=p2, minRadius=1,
                                           maxRadius=30)
                if circles is None:
                    circles = []
                else:
                    circles = circles[0, :]
                p2 -= 1
                if p2 < 15: return -1

            if len(circles) > 4: return -1
            # print circles, len(circles)
        else:
            if len(circles) != 4: return -1

        points = circles[:, :-1]
        # print points

        # print points

        if position is None:
            return [self.map_to_world(p) for p in points]
        else:
            switch_to_bigger = lambda p: self.last_position + p - np.array(
                (self.cropped_size / 2.0, self.cropped_size / 2.0))
            # print self.cropped_size
            # print self.last_position
            # print points
            # print [switch_to_bigger(p) for p in points]
            return [self.map_to_world(switch_to_bigger(p)) for p in points]

            # print points

    def auto_set_calibration_data(self):
        self.video_stream.read()
        _, frame = self.video_stream.read()
        lower_green = np.array([25, 30, 25], dtype=np.uint8)
        upper_green = np.array([60, 255, 250], dtype=np.uint8)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        #edges = cv2.Canny(mask, 100, 200)

        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in contours]

        max_index = np.argmax(areas)
        cnt = contours[max_index]
        points = cnt[:, 0, :]
        x_left = min(points[:, 0]) + 20
        x_right = max(points[:, 0]) - 20
        y_up = min(points[:, 1]) + 20
        y_down = max(points[:, 1]) - 20
        self.set_calibration_data((x_left, y_up), (x_right, y_down))

    def get_all_information(self, circle_positions):
        """
        Gets information from the contours and localizes robot position.
        Converts robot position to points in 2D Cartesian space.
        """
        if circle_positions == -1: return -1
        distances = []
        for a, b in combinations(circle_positions, 2):
            distances.append(distance(a, b))

        distances.sort()

        long_thersh = min(distances[-2:])

        b1, b2, c, f = None, None, None, None
        for i in xrange(len(circle_positions)):
            short_count = 0
            long_count = 0
            for j in xrange(len(circle_positions)):
                if i == j: continue
                if distance(circle_positions[i], circle_positions[j]) < long_thersh:  # avg_distance*9/10:
                    short_count += 1
                else:
                    long_count += 1

            # print short_count, long_count

            if short_count == 3:
                c = np.array(circle_positions[i])
            elif long_count > short_count:
                f = np.array(circle_positions[i])
            elif b1 is None:
                b1 = np.array(circle_positions[i])
            else:
                b2 = np.array(circle_positions[i])

        if b1 is None or b2 is None or c is None or f is None: return -1

        b = (b2 + b1) / 2.0

        pos = (b + c + f) / 3.0

        self.last_position = self.map_from_world(pos)

        theta1 = angle_of(f - b)
        theta2 = angle_of(f - c)

        if np.rad2deg(abs(theta1 - theta2)) > 15:
            return -1

        theta = (theta1 + theta2) / 2

        #print pos, theta % (2 * math.pi)
        return pos, theta % (2 * math.pi)

    def start_sensor(self):
        self.initialise_stream()

        clock = pygame.time.Clock()

        def sensor_existence():

            while self.running:

                time_at_get = time()

                _, f = self.video_stream.read()
                if f is None:
                    # print "No input..."
                    continue
                f = self.get_normalized_data(f)
                circles = self.identity_robot(f)
                if circles == -1:
                    s.find_initial_position()
                    continue
                data = self.get_all_information(circles)

                if type(data) is int: continue

                x, theta = data  # position and angle

                self.data = (x, theta, time_at_get)
                self.new_data_available = True

                clock.tick(self.max_rate)

        t = threading.Thread(target=sensor_existence)
        t.setDaemon(True)

        self.running = True

        t.start()

    def stop_sensor(self):
        self.running = False
        sleep(0.1)  # To avoid stopping the stream before sensor threads stops
        self.stop_stream()


if __name__ == '__main__':
    s = Sensor()
    s.initialise_stream()
    s.find_initial_position()
    s.set_calibration_data((0, 0), (500, 500))

    print s.grid_size
    print s.cropped_size

    while True:
        _, f = s.video_stream.read()
        if f is None: continue
        crop_img = s.get_normalized_data(f)

        k = cv2.waitKey(5) & 0xFF
        p = s.map_from_world(map_to_meters(map_to_cell(s.find_initial_position())))

        print s.identity_robot(p, f)

        cv2.imshow('a', crop_img)
        # cv2.imshow('res', f)
        # if k == 27:
    s.stop_stream()

    """
    while True:
        _, f = s.video_stream.read()
        crop_img = s.get_normalized_data(f)

        k = cv2.waitKey(5) & 0xFF
        i = s.map_from_world(s.find_red_cell())
        cv2.circle(crop_img, (i[0], i[1]), 2, (0, 0, 255), 3)
        cv2.imshow('a', crop_img)
        #cv2.imshow('res', f)
        if k == 27:
            break
    s.stop_stream()
    """
    # print s.find_red_cell()
    # print s.find_initial_position()
    s.stop_stream()
