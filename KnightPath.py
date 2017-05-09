import numpy as np

poss_moves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, 2), (-1, -2)]


def validPos(x, y):
    if 0 <= x < 8 and 0 <= y < 8: return True
    return False


def legs(pos):
    x, y = pos
    return [(x + xa, y + ya) for xa, ya in poss_moves if validPos(x + xa, y + ya)]


def get_main_points(start_p, end_p):
    level_pos = [start_p]
    prev_pos_rec = [[0 for i in xrange(8)] for j in xrange(8)]

    flag = True

    while flag:

        new_pos = []

        for pos in level_pos:
            current_legs = legs(pos)

            for x, y in current_legs:
                if prev_pos_rec[x][y] == 0: prev_pos_rec[x][y] = pos

            if end_p in current_legs:
                flag = False
                break

            new_pos.extend(current_legs)

        level_pos = new_pos

    i = 0
    p = end_p

    chain = range(10)

    while True:
        chain[i] = p

        if p == start_p: break

        p = prev_pos_rec[p[0]][p[1]]
        i += 1

    return chain[:i + 1]


def iter_to(x):
    if x > 0:
        return xrange(1, x + 1)
    else:
        return xrange(-1, x - 1, -1)


def link_ending_horizontally(p1, p2):
    points = []
    xd, yd = tuple(np.subtract(p2, p1))
    x, y = p1
    for i in iter_to(yd):
        points.append((x, y + i))

    y += i
    for i in iter_to(xd):
        points.append((x + i, y))

    return points


def link_ending_vertically(p1, p2):
    points = []
    xd, yd = tuple(np.subtract(p2, p1))
    x, y = p1

    for i in iter_to(xd):
        points.append((x + i, y))

    x += i
    for i in iter_to(yd):
        points.append((x, y + i))

    return points


def connect(chain):
    points = []

    xa, ya = tuple(np.subtract(chain[2], chain[1]))

    if abs(ya) > abs(xa):
        end = 'V'
        points.extend(link_ending_vertically(chain[0], chain[1]))
    else:
        end = 'H'
        points.extend(link_ending_horizontally(chain[0], chain[1]))

    for i in xrange(1, len(chain) - 1):
        if end == 'H':
            end = 'V'
            points.extend(link_ending_vertically(chain[i], chain[i + 1]))
        else:
            end = 'H'
            points.extend(link_ending_horizontally(chain[i], chain[i + 1]))

    return points


def connect_no_reverse(chain):
    points = []

    xa, ya = tuple(np.subtract(chain[2], chain[1]))

    if abs(ya) > abs(xa):
        end = 'V'
        new_points = link_ending_vertically(chain[0], chain[1])
        points.extend(new_points)
    else:
        end = 'H'
        new_points = link_ending_horizontally(chain[0], chain[1])
        points.extend(new_points)

    prev_points = new_points

    for i in xrange(1, len(chain) - 1):
        if end == 'H':
            end = 'V'
            new_points = link_ending_vertically(chain[i], chain[i + 1])
            if new_points[0] in prev_points:
                end = 'H'
                new_points = link_ending_horizontally(chain[i], chain[i + 1])
            points.extend(new_points)
            prev_points = new_points
        else:
            end = 'H'
            new_points = link_ending_horizontally(chain[i], chain[i + 1])
            if new_points[0] in prev_points:
                end = 'V'
                new_points = link_ending_vertically(chain[i], chain[i + 1])
            points.extend(new_points)
            prev_points = new_points

    return points


def get_path(start, end):
    chain = get_main_points(end, start)
    if len(chain) <= 2:
        return [start] + link_ending_horizontally(start, end)
    else:
        return [start] + connect_no_reverse(chain)
