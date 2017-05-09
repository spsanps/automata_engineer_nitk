"""import math
import pickle
import numpy as np

mag = lambda x: math.sqrt(sum([math.pow(i, 2) for i in x]))  # Magnitude of vector


def radius(a, b, c):


    #:rtype : float

    A = mag(b - c)
    B = mag(a - c)
    C = mag(a - b)

    s = (A + B + C) / 2

    K = math.sqrt(s * (s - A) * (s - B) * (s - C))

    if K == 0: return 1000

    return A * B * C / K / 4


def path_function(x):
    return math.pow(x, 2)


#p = [np.array([x * 1.2 / (10 ** 3) + 1.2, path_function((x * 1.2 / (10 ** 3) + 1.2))], dtype=float) for x in
#     xrange(10 ** 3 + 1)]

f = open("record_data.txt", "rb")
p = pickle.load(f)
f.close()

p = [np.array(i) for i in p]
#print p



def generate_speed(path):
    r = [100] + [radius(path[i - 1], path[i], path[i + 1]) for i in xrange(1, len(path) - 1)] + [0]

    avg = sum(r) / len(r)

    speed = np.array(r) / avg * 100
    speed[speed >= 100] = 100
    speed[speed <= 50] = 50
    speed[len(speed) - 1] = 0

    #stop_rate = speed[-20] / 20
    #for i in xrange(-20, 0):
        speed[i] = speed[-20] - (21 + i) * stop_rate

    #return speed


def generate_spline(chain):
    raise NotImplementedError
"""

import numpy as np

from KnightPath import get_path


def map_to_meters(p):
    return (p + np.array((0.5, 0.5))) / 8 * 2.4384


def get_follow_line(p):
    new_path = []
    for i in xrange(1, len(p)):
        new_point = (np.array(p[i]) + np.array(p[i - 1])) / 2.0
        new_path.append(new_point)

    #print new_path
    usable_path = [map_to_meters(point) for point in new_path] + [map_to_meters(p[-1])]
    return usable_path


if __name__ == '__main__':
    p = get_path((0.0, 3.0), (6.0, 7.0))
    print p
    print get_follow_line(p)
