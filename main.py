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


PS_P1_UP = 1
PS_P1_DOWN = 2

PS_P2_UP = 3
PS_P2_DOWN = 4


class Menu:

    def __init__(self,content,menu_fonctions):
        self.content = content
        self.current_item = 0
        self.functions = menu_fonctions


    def __len__(self): return len(self.content)

    def item_down(self):
        self.current_item = (self.current_item + 1 ) % len(self)
    def item_up(self):
        self.current_item = (self.current_item - 1 + len(self)) % len(self)

    def render_menu(self,game):
        pass





pause_menu_content = ["Resume","Quit"]


def print_debug(screen, txt):
    f = SysFont("Arial", 12)
    s = f.render(txt, 1, DEBUG_COL)
    # srect = s.get_rect()
    # pygame.draw.rect(screen, BLACK,srect)

    screen.blit(s, (0, 0))




class Pong():

    def __init__(self):
        self.running = True
        self.debug_events = False
        self.debug_overlay = False

        self.log = logging.getLogger("pong")
        self.screen = None
        self.loop_duration = 0.0001

        self.score_font:SysFont = None

        self.net_start = screen_h // 10

        self.gamezone_h = screen_h - self.net_start

        self.score_pl = 0
        self.score_pr = 0

        self.left_paddle = .5
        self.right_paddle = .5

        self.ball_x = .3
        self.ball_y = .3
        import numpy as np
        self.ball_velocity = np.

        self.current_game_mode = GM_MENU
        self.previous_game_mode = GM_MENU
        self.game_events=[]

        self.slide_paddle_speed = .01

        self.paddle_state:set = set()

    def init(self):
        pygame.init()
        self.score_font = SysFont("monospace", 30)
        self.menu_font = SysFont("monospace", 30)

        # pygame.display.set_icon(logo)
        pygame.display.set_caption("Fanf's Pong")


        self.screen = pygame.display.set_mode((screen_w, screen_h), )

        self.mid_w = screen_w // 2
        self.mid_h = screen_h // 2



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
                if event.type in [pygame.KEYDOWN,pygame.KEYUP]:
                    key_name = pygame.key.name(event.key)
                    # up or down
                    if key_name in ["up","down","return","x","s"]:
                        self.game_events.append((event.type,key_name))

                    pass
    def update(self):


        if self.current_game_mode in [GM_MENU,GM_PAUSED]:
            current_menu = menu_gm[self.current_game_mode]

            for evt in self.game_events:
                match evt:
                    case pygame.KEYDOWN, "up":
                        current_menu.item_up()
                    case pygame.KEYDOWN, "down":
                        current_menu.item_down()
                    case pygame.KEYDOWN, "return":

                        current_menu.functions[current_menu.current_item](self)
            self.game_events = []

        elif self.current_game_mode in [GM_TWO_PLAYER,GM_ONE_PLAYER]:
            remain = []
            for evt in self.game_events:
                match evt:

                    case pygame.KEYDOWN, "up":
                        self.paddle_state.add(PS_P1_UP)
                        self.paddle_state.discard(PS_P1_DOWN)
                    case pygame.KEYUP, "up":
                        self.paddle_state.discard(PS_P1_UP)

                    case pygame.KEYDOWN, "down":
                        self.paddle_state.add(PS_P1_DOWN)
                        self.paddle_state.discard(PS_P1_UP)
                    case pygame.KEYUP, "down":
                        self.paddle_state.discard(PS_P1_DOWN)

                    case pygame.KEYDOWN, "s":
                        self.paddle_state.add(PS_P2_UP)
                        self.paddle_state.discard(PS_P2_DOWN)
                    case pygame.KEYUP, "s":
                        self.paddle_state.discard(PS_P2_UP)

                    case pygame.KEYDOWN, "x":
                        self.paddle_state.add(PS_P2_DOWN)
                        self.paddle_state.discard(PS_P2_UP)
                    case pygame.KEYUP, "x":
                        self.paddle_state.discard(PS_P2_DOWN)


                    case pygame.KEYDOWN, "return":

                        self.previous_game_mode = self.current_game_mode
                        self.current_game_mode = GM_PAUSED



                    case _:
                        remain.append(evt)

            self.game_events = []
            
            # paddle moves
            if PS_P1_UP in self.paddle_state:
                self.right_paddle -= self.slide_paddle_speed
            elif PS_P1_DOWN in self.paddle_state:
                self.right_paddle += self.slide_paddle_speed

            if PS_P2_UP in self.paddle_state:
                self.left_paddle -= self.slide_paddle_speed
            elif PS_P2_DOWN in self.paddle_state:
                self.left_paddle += self.slide_paddle_speed

            paddle_extend = .05
            self.right_paddle = min(self.right_paddle, 1.0-paddle_extend)
            self.right_paddle = max(self.right_paddle, paddle_extend)

            self.left_paddle = min(self.left_paddle, 1.0-paddle_extend)
            self.left_paddle = max(self.left_paddle, paddle_extend)

            # ball moves
            
            


    def render(self):

        render_background(self.screen)
        self.render_score()

        self.render_paddles()

        if self.current_game_mode == GM_MENU:
            self.render_menu(main_menu)
        elif self.current_game_mode == GM_PAUSED:
            self.render_menu(pause_menu)
        else:
            self.render_ball()

        if self.debug_overlay:
            render_overlay(self.screen, self)

        pygame.display.update()

    def render_menu(self,menu:Menu):

        img_menu = [(idx,rend,rend.get_rect()[2:])
            for idx,rend in [(idx, self.menu_font.render(k, 1, WHITE,BLACK) )
                for idx,k in enumerate(menu.content)]]

        max_line_w = max(line_w for idx, rend, (line_w, line_h) in img_menu)

        menu_h = img_menu[0][-1][-1]
        menu_h = menu_h*len(img_menu) + menu_h//2 *(  len(img_menu)-1)

        menu_top = self.mid_h - menu_h//2

        menu_left = int(self.mid_w - max_line_w//2)

        menu_extend = int(max(max_line_w,menu_h)*.3)
        menu_extend2 = menu_extend*2

        pygame.draw.rect(self.screen, BLACK,
                         (menu_left-menu_extend, menu_top-menu_extend, max_line_w+menu_extend2, menu_h+menu_extend2),
                         width=0)

        pygame.draw.rect(self.screen, LIGHT_GREY, (
            menu_left-menu_extend, menu_top-menu_extend, max_line_w+menu_extend2, menu_h+menu_extend2),
                         width=menu_extend//6)



        for idx,rend,(line_w,line_h) in img_menu:

            at_h = int(menu_top + (idx * (line_h * 1.5)))
            at_w = self.mid_w - line_w//2

            self.screen.blit(rend, (at_w, at_h ))

            if idx == menu.current_item:
                pygame.draw.rect(self.screen, WHITE,
                                 (at_w - menu_extend//2, at_h ,
                                  menu_extend//6,line_h),
                                 width=0)

                pygame.draw.rect(self.screen, WHITE,
                                 (at_w + line_w + menu_extend // 2, at_h,
                                  menu_extend // 6, line_h),
                                 width=0)




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





def apply_solo(game:Pong):
    pass
    # start solo game
    # game.current_game_mode = GM_ONE_PLAYER
def apply_2_Players(game:Pong):

    game.score_pl = 0
    game.score_pr = 0

    game.right_paddle = .5
    game.left_paddle = .5

    game.current_game_mode = GM_TWO_PLAYER

def apply_quit(game):
    game.running = False


def apply_resume(game:Pong):
    game.current_game_mode = game.previous_game_mode
    game.previous_game_mode = GM_MENU

def apply_endgame(game):
    game.current_game_mode = GM_MENU


main_menu = Menu(content=["Solo", "2 Players", "Quit"],
                menu_fonctions = [
                    apply_solo,apply_2_Players,apply_quit
                ]
)

pause_menu = Menu(content=["Resume","Quit"],
                 menu_fonctions=[
                     apply_resume, apply_endgame
                 ]

                 )

menu_gm = {GM_MENU:main_menu,GM_PAUSED:pause_menu}

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()