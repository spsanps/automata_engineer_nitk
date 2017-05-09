from random import random
import threading
import struct

import serial
import serial.tools.list_ports

import pygame

OUTPUT_ERROR = 1.0 / 100
MAX_OUT = 100


class VirtualOut:
    def __init__(self, w):
        self.world = w

        self.latest_data = None
        self.communicating = False
        self.send_rate = 1000

    def send(self):
        """
        Adds error to output to replicate effects of real outputs
        """
        l_torque, r_torque = self.latest_data

        l_torque *= (1 + OUTPUT_ERROR * (2 * random() - 1)) * 2  # 2 to make it realistic
        r_torque *= (1 + OUTPUT_ERROR * (2 * random() - 1)) * 2


        # print l_torque, r_torque
        self.world.set_torque_data(l_torque, r_torque)

    def start_com(self):
        """
        Starts communication thread.
        """

        if self.latest_data is None:
            print "Error. Data not available to send. Sending (0,0)..."
            self.latest_data = (0, 0)

        clock = pygame.time.Clock()

        def communicate():
            while self.communicating:
                self.send()
                clock.tick(self.send_rate)
                # sleep(1.0 / self.send_rate)

        t = threading.Thread(target=communicate)
        t.setDaemon(True)

        self.communicating = True

        t.start()

    def stop_com(self):
        self.communicating = False


class Out:
    def __init__(self):
        self.latest_data = None
        self.communicating = False
        self.send_rate = 1000

        self.arduino = None

    def initialise_connection(self):
        """
        Initialises port and serial com with arduino."

        :raise Exception: Arduino not Found.
        """
        try:
            self.arduino.close()
        except:
            pass

        ports = list(serial.tools.list_ports.comports())

        # print ports

        port_loc = None

        for p in ports:
            if "2341" in p[2].lower():
                port_loc = p[0]
                break

        if port_loc is None:
            # raise Exception("Arduino not found.")
            port_loc = "COM7"  # Bluetooth: It works, don't edit

        self.arduino = serial.Serial(port_loc, 9600, timeout=0.01)

    def send(self):
        l, r = self.latest_data

        l += 100  # Map to positive values
        r += 100

        if self.arduino:
            self.arduino.write(struct.pack('>B', int(l)))
            self.arduino.write(struct.pack('>B', int(r)))

    def start_com(self):
        """
        Starts communication thread.
        """

        if self.latest_data is None:
            print "Error. Data not available to send. Sending (0,0)..."
            self.latest_data = (0, 0)

        self.initialise_connection()
        clock = pygame.time.Clock()

        def communicate():
            while self.communicating:
                self.send()
                clock.tick(self.send_rate)
                # sleep(1.0 / self.send_rate)

        t = threading.Thread(target=communicate)
        t.setDaemon(True)

        self.communicating = True

        t.start()

    def stop_com(self):
        self.arduino.close()
        self.communicating = False
