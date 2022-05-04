import logging
import time

import pygame
from pygame.font import SysFont

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
BLACK = (0, 0, 0)
DEBUG_COL = (0, 255, 0)

screen_w = 640
screen_h = 480

GM_PAUSED = 1
GM_MENU = 0
GM_ONE_PLAYER = 2
GM_TWO_PLAYER = 3


def print_debug(screen, txt):
    f = SysFont("Arial", 12)
    s = f.render(txt, 1, DEBUG_COL)
    # srect = s.get_rect()
    # pygame.draw.rect(screen, BLACK,srect)

    screen.blit(s, (0, 0))


menu_content = ["Solo", "2 Players", "Quit"]
pause_menu_content = ["resume","quit"]

class Pong():

    def __init__(self):
        self.running = True
        self.debug_events = False
        self.debug_overlay = False

        self.log = logging.getLogger("pong")
        self.screen = None
        self.loop_duration = 0.0001

        self.score_font = None

        self.net_start = screen_h // 10

        self.gamezone_h = screen_h - self.net_start

        self.score_pl = 0
        self.score_pr = 0

        self.left_paddle = .5
        self.right_paddle = .5

        self.ball_x = .3
        self.ball_y = .3

        self.current_game_mode = GM_MENU

        menu_item_selected = 0


        self.game_events=[]

    def init(self):
        pygame.init()
        self.score_font = SysFont("monospace", 30)
        self.menu_font = SysFont("monospace", 30)

        # pygame.display.set_icon(logo)
        pygame.display.set_caption("Fanf's Pong")
        self.screen = pygame.display.set_mode((screen_w, screen_h), )

    def hande_event(self):
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                self.running = False
            else:
                if self.debug_events:
                    self.log.debug(event)
                if event.type == pygame.KEYDOWN:

                    pygame.KEYDOWN
                    key_name = pygame.key.name(event.key)
                    # up or down
                    if key_name in ["up","down","return"]:
                        self.game_events.append(("down",key_name))

                    pass
    def update(self):
        pass

    def render(self):

        render_background(self.screen)
        self.render_score()

        self.render_paddles()

        if self.current_game_mode == GM_MENU:
            self.render_menu()
        elif self.current_game_mode == GM_PAUSED:
            self.render_paused_menu()
        else:
            self.render_ball()

        if self.debug_overlay:
            render_overlay(self.screen, self)

        pygame.display.update()

    def render_menu(self):



        menuStrs = [k if idx != self.menu_item_selected else f"> {k} <"
                    for idx,k in enumerate(menu_content) ]
        fullTxt = "\n\r".join(menuStrs)

        menubuff = self.score_font.render(fullTxt, 1, WHITE)
        menu_x,menu_y,menu_w,menu_h = menubuff.get_rect()

        mid_w = screen_w // 2
        mid_h = screen_h // 2

        self.screen.blit(menubuff, (mid_w - menu_w//2, mid_h - menu_h//2))


    def render_score(self):

        mid_w = screen_w // 2

        lscore = self.score_font.render("%d" % self.score_pl, 1, WHITE)
        lscore_rect = lscore.get_rect()

        rscore = self.score_font.render("%d" % self.score_pr, 1, WHITE)

        self.screen.blit(lscore, (mid_w - lscore_rect[2] - 10, 0))
        self.screen.blit(rscore, (mid_w + 10, 0))

    def render_paddles(self):

        paddle_height = self.gamezone_h // 7
        paddle_half_height = paddle_height // 2
        paddle_width = screen_w // 80

        pygame.draw.rect(self.screen, WHITE, (
        0, self.net_start + self.gamezone_h * self.left_paddle - paddle_half_height, paddle_width, paddle_height))

        pygame.draw.rect(self.screen, WHITE, (
        screen_w - paddle_width, self.net_start + self.gamezone_h * self.right_paddle - paddle_half_height,
        paddle_width, paddle_height))

    def render_ball(self):
        ball_width = screen_w // 50
        ball_half_width = ball_width // 2

        ballw = self.ball_x * screen_w
        ballh = self.ball_y * self.gamezone_h

        pygame.draw.rect(self.screen, WHITE, (ballw - ball_half_width, ballh - ball_half_width
                                              , ball_width, ball_width))


def render_background(screen):
    pygame.draw.rect(screen, BLACK, (0, 0, screen_w, screen_h))

    mid_w = screen_w // 2

    net_w = screen_w // 70
    net_h = screen_h // 15
    netgap = net_h // 2

    net_start = screen_h // 10

    i = 0
    drawnet = True
    while drawnet:
        net_start_at = net_start + i * (net_h + netgap)
        if net_start_at > screen_h:
            break
        pygame.draw.rect(screen, LIGHT_GREY, (mid_w - net_w // 2, net_start_at, net_w, net_h))
        i += 1


def render_overlay(screen, game):
    loop_duration = .00001 if game.loop_duration == 0 else game.loop_duration
    print_debug(screen, "%.0f fps" % (1.0 / loop_duration))


def main():
    game = Pong()
    game.init()
    game.debug_events = True
    game.debug_overlay = True

    target_loop_duration = 1.0 / 60

    # main loop
    while game.running:
        st = time.time()
        game.hande_event()
        game.update()
        game.render()

        dur = time.time() - st

        if dur < target_loop_duration:
            sleep_for = target_loop_duration - dur
            time.sleep(sleep_for)
        game.loop_duration = time.time() - st


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
