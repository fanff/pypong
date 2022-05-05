import logging
import time
import numpy as np
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
        self.gamezone_w = screen_w


        self.mid_w = screen_w // 2


        self.score_pl = 0
        self.score_pr = 0

        self.left_paddle = .5
        self.left_paddle_velocity = 0

        self.right_paddle = .5
        self.right_paddle_velocity = 0

        self.max_paddle_velocity = 0.03

        self.paddle_accel = 0.015

        self.paddle_relative_extend = .1

        self.ball_loc = None
        self.ball_velocity = None

        self.init_ball_spd_factor=.01

        self.ball_spd_factor = self.init_ball_spd_factor


        self.ball_width = self.gamezone_w // 50
        self.ball_half_width = self.ball_width // 2

        self.round_frame = 0
        self.round_started = False

        self.current_game_mode = GM_MENU
        self.previous_game_mode = GM_MENU
        self.game_events=[]



        self.paddle_state:set = set()

        self.sound_bank = {}





    @property
    def ball_x(self): return self.ball_loc[0]

    @property
    def ball_y(self): return self.ball_loc[1]

    def init(self):
        pygame.init()
        self.score_font = SysFont("monospace", 30)
        self.menu_font = SysFont("monospace", 30)

        self.sound_bank = {"bip": pygame.mixer.Sound('assets/fx13.wav'),
                           "bop": pygame.mixer.Sound('assets/fx16.wav'),
                           "bup": pygame.mixer.Sound('assets/fx22.wav'), }

        # pygame.display.set_icon(logo)
        pygame.display.set_caption("Fanf's Pong")

        #
        self.screen = pygame.display.set_mode((screen_w, screen_h),pygame.FULLSCREEN )

        # pygame.SHOWN

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

                        self.sound_bank["bop"].play()
                        current_menu.item_up()
                    case pygame.KEYDOWN, "down":
                        self.sound_bank["bop"].play()
                        current_menu.item_down()
                    case pygame.KEYDOWN, "return":
                        self.sound_bank["bup"].play()

                        current_menu.functions[current_menu.current_item](self)
            self.game_events = []

        elif self.current_game_mode in [GM_TWO_PLAYER,GM_ONE_PLAYER]:
            remain = []
            for evt in self.game_events:
                match evt:

                    case pygame.KEYDOWN, "up":
                        self.paddle_state.add(PS_P1_UP)
                    case pygame.KEYUP, "up":
                        self.paddle_state.discard(PS_P1_UP)

                    case pygame.KEYDOWN, "down":
                        self.paddle_state.add(PS_P1_DOWN)
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

            # recalc paddle velocities

            #right paddle
            if (PS_P1_UP not in self.paddle_state) and (PS_P1_DOWN not in self.paddle_state):
                self.right_paddle_velocity = self.right_paddle_velocity *0.7
            else:
                if not self.round_started and self.round_started_right:
                    self.round_started = True

                if PS_P1_UP in self.paddle_state:
                    self.right_paddle_velocity -=self.paddle_accel

                if PS_P1_DOWN in self.paddle_state:
                    self.right_paddle_velocity += self.paddle_accel


            if self.right_paddle_velocity >self.max_paddle_velocity:
                self.right_paddle_velocity = self.max_paddle_velocity
            elif self.right_paddle_velocity < - self.max_paddle_velocity:
                self.right_paddle_velocity = - self.max_paddle_velocity


            self.right_paddle += self.right_paddle_velocity

            # left paddle
            if (PS_P2_UP not in self.paddle_state) and (PS_P2_DOWN not in self.paddle_state):
                self.left_paddle_velocity = self.left_paddle_velocity *0.7
            else:
                if not self.round_started and not self.round_started_right:
                    self.round_started = True

                if PS_P2_UP in self.paddle_state:

                    self.left_paddle_velocity -= self.paddle_accel
                elif PS_P2_DOWN in self.paddle_state:
                    self.left_paddle_velocity += self.paddle_accel

            if self.left_paddle_velocity >self.max_paddle_velocity:
                self.left_paddle_velocity = self.max_paddle_velocity
            elif self.left_paddle_velocity < - self.max_paddle_velocity:
                self.left_paddle_velocity = - self.max_paddle_velocity

            self.left_paddle += self.left_paddle_velocity

            # cap paddle location
            self.right_paddle = min(self.right_paddle, 1.0 - self.paddle_relative_extend)
            self.right_paddle = max(self.right_paddle, self.paddle_relative_extend)

            self.left_paddle = min(self.left_paddle, 1.0 - self.paddle_relative_extend)
            self.left_paddle = max(self.left_paddle, self.paddle_relative_extend)


            # ball moves
            if self.round_started:
                self.round_frame +=1



            if self.round_frame == 12:
                paddle_toball_velocity = 16

                if self.round_started_right:
                    self.sound_bank["bip"].play()
                    self.ball_velocity = np.array([-1,self.right_paddle_velocity*paddle_toball_velocity])
                else:
                    self.sound_bank["bop"].play()
                    self.ball_velocity = np.array([1,self.left_paddle_velocity*paddle_toball_velocity])

            else:
                self.ball_loc = self.ball_loc+self.ball_velocity *self.ball_spd_factor

                ball_relative_thinkness = self.ball_half_width/self.gamezone_h
                if self.ball_y< ball_relative_thinkness:
                    self.ball_velocity[1] = np.abs(self.ball_velocity[1])
                elif self.ball_y>1-ball_relative_thinkness:
                    self.ball_velocity[1] = - np.abs(self.ball_velocity[1])

                if self.ball_x< ball_relative_thinkness:
                    if self.in_paddle_left():
                        dist_tocenter = abs(self.left_paddle - self.ball_y )/(self.paddle_relative_extend)


                        self.ball_velocity[0] = np.abs(self.ball_velocity[0])

                        self.ball_velocity = self.ball_velocity * (1.0 + (dist_tocenter)/10)

                        self.sound_bank["bop"].play()
                    else:

                        #credit score paddle_right
                        self.score_pr += 1
                        # reinit round
                        self.new_round_2P_game()


                elif self.ball_x>1-ball_relative_thinkness:

                    if self.in_paddle_right():
                        self.sound_bank["bip"].play()

                        dist_tocenter = abs(self.left_paddle - self.ball_y) / (self.paddle_relative_extend)
                        self.ball_velocity[0] = - np.abs(self.ball_velocity[0])
                        self.ball_velocity = self.ball_velocity * (1.0 + (dist_tocenter) / 10)
                    else:

                        #credit score
                        self.score_pl += 1
                        self.new_round_2P_game(right=False)



    def in_paddle_right(self):
        return self.right_paddle -self.paddle_relative_extend < self.ball_y <self.right_paddle +self.paddle_relative_extend

    def in_paddle_left(self):
        return self.left_paddle - self.paddle_relative_extend < self.ball_y < self.left_paddle + self.paddle_relative_extend
    def re_init_2P_game(self):
        self.score_pl = 0
        self.score_pr = 0

        self.right_paddle = .5
        self.left_paddle = .5



        self.ball_spd_factor = self.init_ball_spd_factor
        self.new_round_2P_game(right=True)


    def new_round_2P_game(self, right=True):

        ball_init_shift = (self.ball_half_width / self.gamezone_w)*3
        self.round_started = False
        self.round_started_right = right
        if right :

            self.ball_loc = np.array([(1.0-ball_init_shift),self.right_paddle])
            self.ball_velocity = np.array([0.0,0.0])
        else:

            self.ball_loc = np.array([( ball_init_shift), self.left_paddle])
            self.ball_velocity = np.array([0.0, 0.0])
        self.round_frame = 0
    def render(self):

        self.render_background()
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



        lscore = self.score_font.render("%d" % self.score_pl, 1, WHITE)
        lscore_rect = lscore.get_rect()

        rscore = self.score_font.render("%d" % self.score_pr, 1, WHITE)

        self.screen.blit(lscore, (self.mid_w - lscore_rect[2] - 10, 0))
        self.screen.blit(rscore, (self.mid_w + 10, 0))

    def render_paddles(self):

        paddle_height = int(self.gamezone_h * self.paddle_relative_extend*2)
        paddle_half_height = paddle_height // 2
        paddle_width = self.ball_half_width

        pygame.draw.rect(self.screen, WHITE, (
        0, self.net_start + (self.left_paddle*self.gamezone_h) - paddle_half_height,

        paddle_width, paddle_height))

        pygame.draw.rect(self.screen, WHITE, (
        screen_w - paddle_width, self.net_start + self.gamezone_h * self.right_paddle - paddle_half_height,
        paddle_width, paddle_height))

    def render_ball(self):


        ballw = self.ball_x * screen_w
        ballh = self.net_start+  self.ball_y * self.gamezone_h

        pygame.draw.rect(self.screen, WHITE, (ballw - self.ball_half_width, ballh - self.ball_half_width
                                              , self.ball_width, self.ball_width))


    def render_background(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, screen_w, screen_h))

        pygame.draw.rect(self.screen, LIGHT_GREY, (0, self.net_start, screen_w, self.gamezone_h),width=2)


        net_w = screen_w // 70
        net_h = screen_h // 15
        netgap = net_h // 2

        i = 0
        drawnet = True
        while drawnet:
            net_start_at = self.net_start + i * (net_h + netgap)
            if net_start_at > screen_h:
                break
            pygame.draw.rect(self.screen, LIGHT_GREY, (self.mid_w - net_w // 2, net_start_at, net_w, net_h))
            i += 1


def render_overlay(screen, game):
    loop_duration = .00001 if game.loop_duration == 0 else game.loop_duration
    print_debug(screen, "%.0f fps" % (1.0 / loop_duration))


def main():
    game = Pong()
    game.init()
    game.debug_events = False
    game.debug_overlay = False

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
def apply_2_Players(self:Pong):
    # right start
    self.re_init_2P_game()
    self.current_game_mode = GM_TWO_PLAYER

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