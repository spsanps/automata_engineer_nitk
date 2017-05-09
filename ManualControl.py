from time import sleep,time
import pickle

import pygame

from easyWindow import Window
from SystemOut import Out, VirtualOut
from AnimatedDisplay import Display
from WorldProcessing import World
from InternalModelReality import Simulation
from MeasureWorld import VirtualSensor
import numpy as np

def real_control():
    com = Out()
    com.latest_data = (0, 0)
    com.start_com()
    com.send_rate = 1000

    ui = Window()
    ui.aspectRatio = (1, 1)
    ui.SIZE = 600
    ui.begin()

    sleep(0.5)

    while True:
        if ui.DONE:
            com.stop_com()
            break

        if pygame.key.get_pressed()[pygame.K_UP] != 0:
            com.latest_data = (100, 100)

        elif pygame.key.get_pressed()[pygame.K_DOWN] != 0:
            com.latest_data = (-100, -100)

        elif pygame.key.get_pressed()[pygame.K_LEFT] != 0:
            com.latest_data = (-100, 100)

        elif pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
            com.latest_data = (100, -100)

        else:
            com.latest_data = (0, 0)


def virtual_control():
    #w = World()
    #w.simulation_rate = 100
    #w.start_simulation()

    w = Simulation()
    w.simulation_rate = 100
    w.start_simulation()

    sensor = VirtualSensor()
    sensor.set_stream(w)
    sensor.data = (w.pos, 0, (0, 0), 0)
    sensor.rate = 20
    sensor.start_sensor()

    disp = Display()
    disp.set_world(w)
    disp.p = []
    disp.start_display()

    sleep(0.5)

    com = VirtualOut(w)
    com.latest_data = (0, 0)
    com.start_com()
    com.send_rate = 50

    point_record = []
    record = True

    start_t = time()

    while True:
        if disp.ui.DONE:
            break

        if pygame.key.get_pressed()[pygame.K_UP] != 0:
            com.latest_data = (100, 100)

        elif pygame.key.get_pressed()[pygame.K_DOWN] != 0:
            com.latest_data = (-100, -100)

        elif pygame.key.get_pressed()[pygame.K_LEFT] != 0:
            com.latest_data = (-100, 100)

        elif pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
            com.latest_data = (100, -100)

        else:
            com.latest_data = (0, 0)

        print np.rad2deg(w.theta_Z), np.rad2deg(sensor.measure_world_data()[1])

        #print w.pos
     #   point_record.append(list(w.pos))

#        if time() - start_t > 5:
 #           break

        sleep(0.02)

  #  f = open("record_data.txt", 'wb')
   # print point_record
    print "Dumping..."
    #pickle.dump(point_record, f)
    #f.close()

    com.stop_com()
    w.stop_simulation()
    disp.stop_display()

#virtual_control()
real_control()
