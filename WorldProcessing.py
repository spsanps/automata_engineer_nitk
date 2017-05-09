import math
import threading
from random import random
from time import time

import numpy as np
import pygame

mag = lambda x: math.sqrt(sum([math.pow(i, 2) for i in x]))


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])


class World:
    def __init__(self):
        """Constants, initial position and orientation for simulation."""

        # --------------------------State Variables----------------------------

        MEASURED_WHEEL_DIAMETER = 10.0 / 100
        WHEEL_ERROR = 1.0 / 100

        self.L_WHEEL_DIAMETER = MEASURED_WHEEL_DIAMETER + (2 * random() - 1) * WHEEL_ERROR
        self.R_WHEEL_DIAMETER = MEASURED_WHEEL_DIAMETER + (2 * random() - 1) * WHEEL_ERROR

        self.MASS = 500.0 / 1000
        self.MOMENT_OF_INERTIA_Z = 2 * self.MASS / 1000 * (10.0 / 100) * (10.0 / 100) / 5

        RADIUS_ERROR = 1.0 / 100

        RADIUS = 10.0 / 100
        self.L_RADIUS = RADIUS * (1 + (2 * random() - 1) * RADIUS_ERROR)
        self.R_RADIUS = RADIUS * (1 + (2 * random() - 1) * RADIUS_ERROR)

        self.FORCE_DUE_TO_FRICTION = 100.0 / 100 * (
            1.0 / 40) * 10  # 100% of velocity times the max torque required converted to force
        self.TORQUE_DUE_TO_SPIN = 700.0 / 100 * (1.0 / 40) * 10  # FIX VALUE

        self.pos = np.array((1.2, 1.2))  # Use cartesian, not matrix
        self.v = np.array((0, 0))
        self.a = np.array((0, 0))

        self.theta_Z = 0
        self.omega_Z = 0  # In radians
        self.alpha_Z = 0

        self.l_applied_torque = 0
        self.r_applied_torque = 0

        # -----------------------Other Function Variables-----------------------

        self.running = False
        self.simulation_rate = 1000

    def start_simulation(self):

        def simulate():
            """Error free simulation. Does one step."""

            clock = pygame.time.Clock()
            time_at_last_call = time()

            while self.running:
                t_now = time()
                time_since_last_call = t_now - time_at_last_call
                time_at_last_call = t_now

                # print time(), time_since_last_call, self.v, self.pos
                self.pos += self.v * time_since_last_call + 0.5 * self.a * math.pow(time_since_last_call, 2)
                self.v += self.a * time_since_last_call

                l_force = self.l_applied_torque * self.L_WHEEL_DIAMETER / 2
                r_force = self.r_applied_torque * self.R_WHEEL_DIAMETER / 2
                t_force = (l_force + r_force) / (self.simulation_rate * time_since_last_call * mag(self.v) * self.FORCE_DUE_TO_FRICTION + 1)

                torque_z = (-l_force * self.L_RADIUS + r_force * self.R_RADIUS) / (
                    self.simulation_rate * time_since_last_call * abs(self.omega_Z * self.TORQUE_DUE_TO_SPIN) + 1) / 1000

                self.theta_Z += self.omega_Z * time_since_last_call + 0.5 * self.alpha_Z * math.pow(
                    time_since_last_call,
                    2)
                self.omega_Z = self.alpha_Z * time_since_last_call

                self.theta_Z %= 360 * math.pi / 180

                a = t_force / self.MASS
                self.a = pol2cart(a, self.theta_Z)

                self.alpha_Z = torque_z / self.MOMENT_OF_INERTIA_Z

                # print torque_z, self.alpha_Z, self.omega_Z, np.rad2deg(self.theta_Z)

                clock.tick(self.simulation_rate)

        t = threading.Thread(target=simulate)
        t.setDaemon(True)

        self.running = True

        t.start()

    def stop_simulation(self):
        self.running = False

    def set_torque_data(self, l_torque, r_torque):
        if not self.running: raise StopIteration
        self.l_applied_torque = l_torque
        self.r_applied_torque = r_torque

    def get_current_data(self):
        if not self.running: raise StopIteration
        return self.pos, self.theta_Z
