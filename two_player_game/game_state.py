
import pygame
from server import *
import pickle

# radius of players
RAD = 10
# radiu of bullets
BRAD = 5
# speed of players
SPEED = 5


def add_tuple(a, b):
    return a[0] + b[0], a[1] + b[1]


class GameState:
    def __init__(self):
        self.server = 'Server()'
        self.data = {"players":[], "bullets":[]}
        self.thisPlayer = (0, 0)
        self.fired = 0
        self.client = 'ServerClient()'

    def selection_screen(self, screen, clock):
        # make background blue
        screen.fill((0, 0, 255))
        pygame.draw.rect(screen,  (0, 255, 0), (0, 300, 800, 300))
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # self.thisPlayer = (600, 300)
                    self.client = ServerClient()
                    self.client.handle_connection()
                    waiting = False
                    while not self.client.data.get("running", True):
                        clock.tick(30)
                        pass
            clock.tick(30)
            pygame.display.update()

    def redraw(self, screen):
        # make background black
        screen.fill((0, 0, 0))

        # Draw other players
        players = self.data["players"]
        for i in range(self.data["current"]):
            pygame.draw.circle(screen, (255,15,15), players[i], RAD)
        for i in range(self.data["current"]+1, 2):
            pygame.draw.circle(screen, (255,15,15), players[i], RAD)
        
        # Draw the player being controlled
        pygame.draw.circle(screen, (0,0,255), self.thisPlayer, RAD)

        self._draw_bullets(screen)

        pygame.display.update()

    def _draw_bullets(self, screen):
        bullets = self.data["bullets"]
        for b in bullets:
            pygame.draw.circle(screen, (255, 0, 0), b, BRAD)

    def controll_player(self, keys):
        if keys[pygame.K_UP]:
            self.thisPlayer = add_tuple(self.thisPlayer, (0, -SPEED))
        elif keys[pygame.K_DOWN]:
            self.thisPlayer = add_tuple(self.thisPlayer, (0, SPEED))
        if keys[pygame.K_RIGHT]:
            self.thisPlayer = add_tuple(self.thisPlayer, (SPEED, 0))
        elif keys[pygame.K_LEFT]:
            self.thisPlayer = add_tuple(self.thisPlayer, (-SPEED, 0))

        if self.thisPlayer[1]-RAD < 0:
            self.thisPlayer = (self.thisPlayer[0], RAD)
        elif self.thisPlayer[1] + RAD > 600:
            self.thisPlayer = (self.thisPlayer[0], 600-RAD)

        if self.thisPlayer[0] < 0:
            self.thisPlayer = (RAD, self.thisPlayer[1])
        elif self.thisPlayer[0] > 800:
            self.thisPlayer = (800-RAD, self.thisPlayer[1])

    def fire_bullets(self):
        self.fired = 1

    def update(self, keys):
        # TODO: do merge controll and update, do control and then send data
        bullets = self.data["bullets"]
        for b in bullets:
            if (self.thisPlayer[0]-b[0])**2 + (self.thisPlayer[1]-b[1])**2\
                    <= (RAD+ BRAD)**2:
                pygame.quit()
                sys.exit()

        self.data = self.client.data
        self.thisPlayer = self.data["players"][self.data["current"]]

        self.controll_player(keys)

        self.send_data()

    def send_data(self):
        d = {"pos": self.thisPlayer, "fired": self.fired}
        self.client.send(d)
        self.fired = 0

    def shutdown(self):
        self.client.running = False
