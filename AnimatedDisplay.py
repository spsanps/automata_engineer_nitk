import math

import numpy as np

from easyWindow import *


class Display:
    def __init__(self):
        self.world = None
        self.p = None  # Path

        self.ui = Window()
        self.ui.aspectRatio = (1, 1)
        self.ui.SIZE = 600

        self.update_rate = 15

        self.cell_size = self.ui.SIZE / 8
        self.bot_size = 7.0 / 100
        self.len_cartesian = 2.4384

        self.running = False

    def set_world(self, w):
        self.world = w

    def map_to_pygame_grid(self, pos):
        new_p = pos / 2.4384 * self.ui.SIZE

        x = int(round(new_p[0]))
        y = int(round(self.ui.SIZE - new_p[1]))

        # print pos, new_p, m, n

        return x, y

    def draw_bg(self):
        for i in xrange(8):
            for j in xrange(8):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(self.ui.screen, WHITE,
                                     (self.cell_size * i, self.cell_size * j, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.ui.screen, BLACK,
                                     (self.cell_size * i, self.cell_size * j, self.cell_size, self.cell_size))

    def draw_bot(self, pos, angle):
        # print pos, self.bot_size

        x1, y1 = pos

        x2 = x1 + self.bot_size * math.cos(angle)
        y2 = y1 + self.bot_size * math.sin(angle)

        # print angle

        # print ((x1, y1), (x2, y2), 180 * angle / math.pi)

        pygame.draw.circle(self.ui.screen, RED, self.map_to_pygame_grid(pos),
                           int(self.bot_size / self.len_cartesian * self.ui.SIZE))

        pygame.draw.line(self.ui.screen, WHITE, self.map_to_pygame_grid(pos),
                         self.map_to_pygame_grid(np.array((x2, y2))), 3)

    def draw_points(self, points):
        for i in xrange(0, len(points) - 1):
            pygame.draw.line(self.ui.screen, BLUE, self.map_to_pygame_grid(points[i]),
                             self.map_to_pygame_grid(points[i + 1]), 3)

    def start_display(self):
        clock = pygame.time.Clock()
        self.ui.begin()

        def display_existence():
            while self.running:
                actual_pos, angle = self.world.get_current_data()
                pos = self.map_to_pygame_grid(actual_pos)
                self.draw_bg()
                self.draw_bot(actual_pos, angle)
                self.draw_points(self.p)
                pygame.display.flip()
                clock.tick(self.update_rate)

        t = threading.Thread(target=display_existence)
        t.setDaemon(True)

        self.running = True

        t.start()

    def stop_display(self):
        self.running = False
        self.ui.DONE = True
