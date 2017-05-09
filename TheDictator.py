from time import sleep

from WorldProcessing import World
from SystemOut import VirtualOut, Out
from AnimatedDisplay import Display
from MeasureWorld import VirtualSensor, Sensor
from RobotBrain import Control
from RobotPath import get_path, get_follow_line
from Misc import *

"""
def virtual():
    w = World()
    w.simulation_rate = 100
    w.start_simulation()

    sensor = VirtualSensor()
    sensor.set_stream(w)
    sensor.data = (w.pos, 0, (0, 0), 0)
    sensor.start_sensor()

    imr = Simulation()
    imr.simulation_rate = 100
    imr.start_simulation()

    # print p
    # pygame.display.flip()

    world_disp = Display()
    world_disp.set_world(imr)
    world_disp.p = p
    world_disp.start_display()
    # world_disp.draw_points(p)

    sleep(2)

    com = VirtualOut(w)
    com.latest_data = (0, 0)
    com.send_rate = 100
    com.start_com()

    path = zip(p, generate_speed(p))

    # sleep(0.5)

    brain = Brain()
    brain.think_rate = 100
    brain.set_imr(imr)
    brain.set_out(com)
    brain.set_sensor(sensor)
    brain.set_path(path)
    brain.come_alive()

    sleep(1.5)

    while True:
        pass


# virtual()
"""

from random import randint


def virtual2():
    p = get_path((3,3), (0,7))
    path = get_follow_line(p)

    w = World()
    w.simulation_rate = 100
    w.pos = map_to_meters(p[0])
    w.start_simulation()

    sleep(0.5)

    world_disp = Display()
    world_disp.set_world(w)
    world_disp.p = path
    world_disp.start_display()

    #    sleep(5)

    sensor = VirtualSensor()
    sensor.set_stream(w)
    sensor.data = (w.pos, 0, (0, 0), 0)
    sensor.rate = 20
    sensor.start_sensor()

    com = VirtualOut(w)
    com.latest_data = (0, 0)
    com.send_rate = 20
    com.start_com()

    # com1 = Out()
    # com1.latest_data = (0, 0)
    # com1.start_com()
    # com1.send_rate = 1000


    # sleep(0.5)

    brain = Control()
    brain.simulation = 100
    brain.set_out(com)
    # brain.out2 = com1
    brain.set_sensor(sensor)
    brain.set_path(path)
    brain.come_alive()

    sleep(1.5)

    while True:
        pass


virtual2()


def real():
    sensor = Sensor()
    sensor.max_rate = 50
    sensor.set_calibration_data((0, 0), (500, 500))
    sensor.initialise_stream()
    sensor.auto_set_calibration_data()

    print 'Camera feed initialized...'

    com = Out()
    com.latest_data = (0, 0)
    com.send_rate = 50
    com.start_com()

    print 'Communication link established...'

    brain = Control()
    brain.rate = 100
    brain.set_out(com)
    brain.set_sensor(sensor)

    raw_input('Press enter to begin.')

    # Finding start end positions---------------------------------------------------------------------------------------
    start = map_to_cell(sensor.find_initial_position())

    import random

    end = random.choice([(0, 0), (7, 7), (0, 7), (7, 0)])

    print start, end

    print "Found End Position..."
    follow_line = get_follow_line(get_path(start, end))
    # ------------------------------------------------------------------------------------------------------------------

    print 'Path calculated...'

    sensor.start_sensor()
    sleep(0.5)
    print 'Robot positioning started...'

    brain.set_path(follow_line)
    brain.come_alive()

    print 'Alive and running...'

    while True:
        if not brain.running:
            print 'Path end reached; Shut Down in progress...'
            break
        sleep(0.1)

    sensor.stop_sensor()
    com.stop_com()


real()
