import threading

import pygame

from customArrays import ConstList

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)


class Window:
    def __init__(self):
        self.SIZE = 50
        self.aspectRatio = (16, 9)
        self.WINDOW_SIZE = None
        self.CAPTION = "WINDOW"
        self.FILL = WHITE

        self.screen = None

        self.DONE = False
        self.events = ConstList(25)
        self.fps = 15
        self.runningFunctionsInformation = {}

    def begin(self, eventCheckRate=None):

        self.WINDOW_SIZE = (self.aspectRatio[0] * self.SIZE, self.aspectRatio[1] * self.SIZE)

        if eventCheckRate is None: eventCheckRate = self.fps

        def exist():

            pygame.init()

            self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
            pygame.display.set_caption(self.CAPTION)
            self.screen.fill(self.FILL)

            clock = pygame.time.Clock()

            while not self.DONE:
                self.events.extend(pygame.event.get())
                for event in self.events.get():
                    if type(event) != int and event.type == pygame.QUIT:
                        self.DONE = True
                        pygame.quit()
                clock.tick(eventCheckRate)
            exit(0)

        t = threading.Thread(target=exist)
        t.setDaemon(True)
        t.start()

        while self.screen is None:
            pass

    def start(self, func, rate=None):
        if rate is None: rate = self.fps

        self.runningFunctionsInformation[func.__name__] = {'isRunning': True, 'updatesPerSec': rate}

        def decorated():

            clock = pygame.time.Clock()
            while not self.DONE and self.runningFunctionsInformation[func.__name__]['isRunning']:
                try:
                    func()
                except:
                    pass
                clock.tick(self.runningFunctionsInformation[func.__name__]['updatesPerSec'])

            self.runningFunctionsInformation[func.__name__]['isRunning'] = False

        s = threading.Thread(target=decorated)
        s.setDaemon(True)
        s.start()

    def stop(self, func):
        self.runningFunctionsInformation[func.__name__]['isRunning'] = False


if __name__ == '__main__':
    new = Window()
    new.begin()
    new.start(pygame.display.update)
    # pygame.draw.rect(new.screen,BLUE,(200,150,100,50))
