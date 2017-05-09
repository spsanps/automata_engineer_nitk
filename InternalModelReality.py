import math
import threading
from time import time

import numpy as np
import pygame

mag = lambda x: math.sqrt(sum([math.pow(i, 2) for i in x]))


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])


class Simulation:
    def __init__(self):
        """Constants, initial position and orientation for simulation."""

        # --------------------------State Variables----------------------------

        MEASURED_WHEEL_DIAMETER = 10.0 / 100

        self.L_WHEEL_DIAMETER = MEASURED_WHEEL_DIAMETER
        self.R_WHEEL_DIAMETER = MEASURED_WHEEL_DIAMETER

        self.MASS = 500.0 / 1000
        self.MOMENT_OF_INERTIA_Z = 2 * self.MASS / 1000 * (10.0 / 100) * (10.0 / 100) / 5

        RADIUS = 10.0 / 100
        self.L_RADIUS = RADIUS
        self.R_RADIUS = RADIUS

        self.FORCE_DUE_TO_FRICTION = 100.0 / 100 * (
            1.0 / 40) * 10  # 100% of velocity times the max torque required converted to force
        self.TORQUE_DUE_TO_SPIN = 700.0 / 100 * (1.0 / 40) * 10

        self.pos = np.array((1.2, 1.2))  # Use cartesian, not matrix
        self.v = np.array((0, 0))
        self.a = np.array((0, 0))

        self.theta_Z = 0
        self.omega_Z = 0  # In radians
        self.alpha_Z = 0

        self.time_at_last_call = 0

        self.l_applied_torque = 0
        self.r_applied_torque = 0

        self.l_correction_term = 1
        self.r_correction_term = 1

        # -----------------------Other Function Variables-----------------------
        self.simulation_rate = 100
        self.running = False
        self.to_update = False
        self.update_data = None

    def load_data(self):
        raise NotImplementedError

    def save_data(self):
        raise NotImplementedError

    def update(self):
        dp_real, dp_simulate, l_correction, r_correction = self.update_data

        self.l_correction_term, self.r_correction_term = l_correction, r_correction

        de = dp_real - dp_simulate

        xr, tr, vr, omr, tt = dp_real
        # xs, ts, vs, os, _ = dp_simulate
        _, _, ve, oe, _ = de

        """
        self.v += ve
        self.omega_Z += oe

        self.pos = self.pos + ve * (time() - tt)
        self.theta_Z = self.theta_Z + oe * (time() - tt)
        """
        self.pos = xr
        self.theta_Z = tr
        self.v = vr
        self.omega_Z = omr

    def start_simulation(self):

        def simulate():
            """Error free simulation. Does one step."""

            clock = pygame.time.Clock()
            self.time_at_last_call = time()

            while self.running:
                if self.to_update: self.update()

                # -----------------------------Physics Simulation---------------------------------

                t_now = time()
                time_since_last_call = t_now - self.time_at_last_call
                self.time_at_last_call = t_now

                self.pos += self.v * time_since_last_call + 0.5 * self.a * math.pow(time_since_last_call, 2)
                self.v += self.a * time_since_last_call

                l_force = self.l_correction_term * self.l_applied_torque * self.L_WHEEL_DIAMETER / 2
                r_force = self.r_correction_term * self.r_applied_torque * self.R_WHEEL_DIAMETER / 2

                t_force = (l_force + r_force) / (
                    self.simulation_rate * time_since_last_call * mag(self.v) * self.FORCE_DUE_TO_FRICTION + 1)

                torque_z = (-l_force * self.L_RADIUS + r_force * self.R_RADIUS) / (
                    self.simulation_rate * time_since_last_call * abs(
                        self.omega_Z * self.TORQUE_DUE_TO_SPIN) + 1) / 1000

                self.theta_Z += self.omega_Z * time_since_last_call + 0.5 * self.alpha_Z * math.pow(
                    time_since_last_call,
                    2)

                self.theta_Z %= 360 * math.pi / 180

                self.omega_Z = self.alpha_Z * time_since_last_call

                a = t_force / self.MASS
                self.a = pol2cart(a, self.theta_Z)

                self.alpha_Z = torque_z / self.MOMENT_OF_INERTIA_Z

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
        # if not self.running: raise StopIteration
        return self.pos, self.theta_Z
