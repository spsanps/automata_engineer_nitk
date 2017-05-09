import threading
from time import time
import math

import pygame
import numpy as np

from customArrays import ConstList


def angle_of(vector):
    x, y = vector
    if x == 0: return np.deg2rad(90)
    if x < 0: return math.pi + np.arctan(y / x)
    return np.arctan(y / x)


mag = lambda x: math.sqrt(sum([math.pow(i, 2) for i in x]))  # Magnitude of vector


class Brain:
    def __init__(self):
        """Basic variables"""

        self.MAX_SPEED = 30.0 / 100  # In meters per second for moving on path

        # --------------------------Variables for communications with other threads-----------------------

        self.path = None  # Each index corresponds to 1 / 1000 of 8 foot converted to meters (0.0024384)
        self.path_len = None
        self.index_len = None
        self.out = None
        self.sensor = None
        self.imr = None  # Internal model of reality

        # -------------------------------------Variables for Processing-----------------------------------

        self.alive = False
        self.think_rate = 1000

        self.simulated_data = ConstList(50)  # Keep record of last 1000 simulated positions
        self.last_real_dp = None

        self.correction_weight = (self.think_rate - 10) / self.think_rate

    def set_path(self, p):
        self.path = p
        self.path_len = len(p)
        self.index_len = 2.0 / self.path_len

    def set_out(self, o):
        self.out = o

    def set_imr(self, p):
        self.imr = p

    def set_sensor(self, s):
        self.sensor = s

    def get_error_correction_terms(self, d, ds):
        """
        Simple correction; change if required
        ;return correction terms
        """

        if self.last_real_dp is None:
            return 1, 1

        x, _, v, _, _ = d
        xs, _, vs, _, _ = ds

        xl, _, vl, _, _ = self.last_real_dp

        angle_r = angle_of(x - xl)
        angle_s = angle_of(xs - xl)

        turn_angle = np.rad2deg(angle_r - angle_s)

        ratio = 1 - abs(turn_angle) / 10 * 0.5
        if ratio < 0.5: ratio = 0.5

        l_c, r_c = ratio, 1  # For positive turn angles

        if turn_angle < 0:
            l_c, r_c = r_c, l_c

        k = 0  # Linear equation
        increase_factor = 1
        if mag(vs) == 0:
            k = mag(v)
        else:
            increase_factor = mag(v) / mag(vs)

        new_c_t = np.array((l_c, r_c)) * increase_factor + k  # Correction terms

        prev_c_t = np.array((self.imr.l_correction_term, self.imr.r_correction_term))
        new_c_t = self.correction_weight * prev_c_t + (1 - self.correction_weight) * new_c_t
        # Weighting to avoid rapid change in correction term values

        return new_c_t

    def update_imr(self, d):
        X, theta_Z, v, omega_Z, time_at_get = d

        old_data = self.simulated_data.get()

        for i in xrange(len(old_data) - 1, 0, -1):
            if type(old_data[i]) == int: continue

            if time_at_get > old_data[i][-1]:
                index = i
                break
        else:
            print "Sensor update time too low. Increase memory to compensate. - Robot Brain"
            return -1

        if index == len(old_data) - 1: return -1

        dp1 = np.array(old_data[index])  # Data point 1
        dp2 = np.array(old_data[index + 1])  # Data point 2

        t1 = old_data[index][-1]
        t2 = old_data[index + 1][-1]

        ds = dp1 + (dp2 - dp1) * (time_at_get - t1) / (t2 - t1)  # Simulated data

        l_c, r_c = self.get_error_correction_terms(d, ds)

        # print l_c, r_c

        self.imr.update_data = (d, ds, l_c, r_c)
        self.imr.to_update = True

        self.last_real_dp = d

    def get_torque_values(self, path_index, to_angle):

        to_pos, speed = self.path[path_index]

        # to_angle = np.deg2rad(angle_of(to_pos - self.imr.pos) - self.imr.theta_Z) % 360

        # if to_angle > 180: to_angle += -360  # to get value in between -180 and 180

        if abs(to_angle) > 45:
            if to_angle > 0:
                return -100, 100
            else:
                return 100, -100

        torque_ratio = to_angle  # if angle is 10, 10 is the torque ratio

        # speed += 100 * mag(to_pos - self.imr.pos) / (5.0 / 100)
        if torque_ratio == 0:
            l, r = speed, speed
        else:
            l, r = speed / abs(torque_ratio), speed

        if torque_ratio < 0: l, r = r, l  # Spin opposite direction

        return int(round(l)), int(round(r))

    def come_alive(self):
        """Start controlling the robot"""

        clock = pygame.time.Clock()

        def existence():
            current_index = 0

            end = False
            measuring_time_since_end = False
            time_since_end = 0

            while self.alive:

                # ----------------------- Update ------------------------
                if self.sensor.new_data_available:
                    d = self.sensor.data
                    self.sensor.new_data_available = False
                    self.update_imr(d)
                    # print 'updating'
                # ----------------------- Update ------------------------

                # ----------------------------------------Index Calculation--------------------------------------------
                to_x, to_speed = self.path[int(round(current_index))]
                to_x = np.array(to_x)

                to_pos_vector = to_x - self.imr.pos
                current_vel_vector = self.imr.v

                if mag(current_vel_vector) != 0:
                    direction_to_face = np.rad2deg(angle_of(to_pos_vector - current_vel_vector)) % 360
                    # noinspection PyTypeChecker

                    to_catch_up = abs(np.dot(to_pos_vector, current_vel_vector / mag(current_vel_vector)))
                else:
                    to_catch_up = mag(to_pos_vector) * 1.5
                    print to_catch_up
                    direction_to_face = np.rad2deg(angle_of(to_pos_vector - self.imr.theta_Z)) % 360
                    # print direction_to_face
                if direction_to_face > 180: direction_to_face -= 360

                index_to_add = to_speed * self.MAX_SPEED * (1.0 / self.think_rate) / self.index_len
                if abs(direction_to_face) > 90:
                    index_to_add = (to_catch_up + 1.0 / 100) / self.index_len / 10
                    # If indexing is behind angle will be > 90
                elif to_catch_up > 1.5 / 100:
                    index_to_add = 0  # More than 1.5 cm

                current_index += index_to_add

                if current_index >= self.path_len - 1:
                    if to_catch_up < 0.75 / 100: l_t, r_t = 0, 0
                    current_index = self.path_len - 1
                else:
                    l_t, r_t = self.get_torque_values(int(round(current_index)), direction_to_face)
                    # Bounding torque values
                    higher_bound = max((abs(l_t), abs(r_t)))
                    if higher_bound > 100:
                        l_t = l_t / higher_bound * 100
                        r_t = r_t / higher_bound * 100

                self.out.latest_data = (l_t, r_t)
                self.imr.l_applied_torque, self.imr.r_applied_torque = l_t, r_t
                self.simulated_data.add(
                    (self.imr.pos, self.imr.theta_Z, self.imr.v, self.imr.omega_Z, self.imr.time_at_last_call))

                # Code for shutting down--------------------------------------------------------------------------------

                if not end and current_index >= self.path_len - 1:
                    end = True
                    measuring_time_since_end = False

                if end:
                    if measuring_time_since_end:
                        if time() - time_since_end > 1:  # Wait one second before shutting down
                            self.kill()
                    else:
                        time_since_end = time()
                        measuring_time_since_end = True

                print to_pos_vector, direction_to_face, current_vel_vector, to_speed, current_index, to_catch_up, index_to_add, l_t, r_t

                clock.tick(self.think_rate)

        t = threading.Thread(target=existence)
        t.setDaemon(True)

        self.alive = True

        t.start()

    def kill(self):
        self.alive = False
        self.imr.running = False
        self.sensor.running = False
        self.out.communicating = False


class Control:
    def __init__(self):
        """Basic variables"""

        self.MAX_SPEED = 30.0 / 100  # In meters per second for moving on path

        # --------------------------Variables for communications with other threads-----------------------

        self.path = None  # Shouldn't include speed
        self.path_len = None
        self.out = None
        self.out2 = None
        self.sensor = None

        # -------------------------------------Variables for Processing-----------------------------------

        self.running = False
        self.rate = 1000
        self.old_data = ConstList(3)

    def set_path(self, p):
        self.path = p
        self.path_len = len(p)

    def set_out(self, o):
        self.out = o

    def set_imr(self, p):
        self.imr = p

    def set_sensor(self, s):
        self.sensor = s

    def get_current_data(self):
        all_data = self.old_data.get()
        if type(all_data[-2]) is int:
            if type(all_data[-1]) is int: return 0, 0, 0, 0
            x, t = all_data[-1][:-1]  # Splicing to remove time_at_get
            return x, 0, t, 0

        if type(all_data[-1]) is int: return 0, 0, 0, 0

        x2, t2, time2 = all_data[-1]
        x1, t1, time1 = all_data[-2]

        x = x1 + (x2 - x1) * (time() - time1) / (time2 - time1)
        t = t1 + (t2 - 1) * (time() - time1) / (time2 - time1)
        v = (x2 - x1) / (time2 - time1)
        o = (t2 - t1) / (time2 - time1)

        return all_data[-1][0], v, all_data[-1][1], o  # Remove calculation if unnecessary
        # return x, v, t, o

    def get_torque_values(self, to_x):

        x, v, t, o = self.get_current_data()

        # print x, v, t, o

        to_pos_vector = to_x - x
        to_angle = np.rad2deg(angle_of(to_pos_vector) - t) % 360
        if to_angle > 180: to_angle -= 360  # Principle value
        #print np.rad2deg(angle_of(to_pos_vector)), np.rad2deg(t), to_angle,

        if abs(to_angle) > 45:
            if to_angle > 0:
                return -50, 50
            else:
                return 50, -50

        if to_angle == 0:
            return 100, 100

        torque_ratio = (1 / (
            1 + math.exp(-(abs(to_angle) / 3 - 6))) + 1) * 9.5 - 8.5  # Sigmoid Function 0 -> 1, 30 -> 10

        l, r = 50 / abs(torque_ratio), 50
        if to_angle < 0: l, r = r, l  # Spin opposite direction

        return int(round(l)), int(round(r))

    def come_alive(self):
        """Start controlling the robot"""

        clock = pygame.time.Clock()

        def existence():
            current_index = 0

            end = False
            measuring_time_since_end = False
            time_since_end = 0

            while self.running:

                # Update -----------------------------------------------------------------------------------------------
                if self.sensor.new_data_available:
                    d = self.sensor.data
                    # print d
                    self.sensor.new_data_available = False
                    self.old_data.add(d)
                    # print 'updating'

                # Index Calculation-------------------------------------------------------------------------------------
                x, _, theta, _ = self.get_current_data()

                distance_to_flag = mag(self.path[current_index] - x)

                if distance_to_flag < 15.0 / 100:
                    current_index += 1

                if current_index == self.path_len:
                    current_index -= 1
                    if distance_to_flag < 14.0 / 100:
                        l_t, r_t = 0, 0
                        end = True
                    else:
                        l_t, r_t = self.get_torque_values(self.path[current_index])
                else:
                    l_t, r_t = self.get_torque_values(self.path[current_index])

                self.out.latest_data = (l_t, r_t)
                if self.out2 is not None: self.out2.latest_data = (l_t, r_t)

                #print current_index, self.path[current_index], x, np.rad2deg(theta), distance_to_flag, l_t, r_t

                # Code for shutting down--------------------------------------------------------------------------------

                if end:
                    if measuring_time_since_end:
                        if time() - time_since_end > 1:  # Wait one second before shutting down
                            self.kill()
                    else:
                        time_since_end = time()
                        measuring_time_since_end = True

                clock.tick(self.rate)

        t = threading.Thread(target=existence)
        t.setDaemon(True)

        self.running = True

        t.start()

    def kill(self):
        # self.imr.running = False
        self.sensor.running = False
        self.out.communicating = False
        self.running = False
