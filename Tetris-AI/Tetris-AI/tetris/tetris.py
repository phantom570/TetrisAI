#!/usr/bin/env python2
import copy
import time
import threading
import random
from field import Field
from ai import Ai
import pygame, sys
from gui import Gui
import time
##
from ai2 import Ai2
from field2 import Field2

# The configuration
cell_size =    18
cols =        10
rows =        22
maxfps =     30
maxPiece = 500

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

def rotate_clockwise(shape):
    return [ [ shape[y][x]
        
            for y in range(len(shape)) ]
        for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board

def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy+off_y-1    ][cx+off_x] += val
    return mat1

def new_board():
    board = [ [ 0 for x in range(cols) ]
            for y in range(rows) ]
    # board += [[ 1 for x in range(cols)]]
    return board

class TetrisApp(object):
    def __init__(self, playWithUI, seed):
        self.win = 0
        self.width = cell_size*(cols+6)
        self.height = cell_size*rows
        self.rlim = cell_size*cols
        self.nbPiece = 0
        random.seed(seed)
        self.next_stone = tetris_shapes[random.randint(0, len(tetris_shapes)-1)]
        self.playWithUI = playWithUI
        self.fast_mode = True
        if playWithUI:
            self.gui = Gui()
            self.fast_mode = False
        self.init_game()

        ##
        self.width2 = cell_size*(cols+6)
        self.height2 = cell_size*rows
        self.rlim2 = cell_size*cols
        self.nbPiece2 = 0
        random.seed(seed)
        self.next_stone2 = tetris_shapes[random.randint(0, len(tetris_shapes)-1)]
        # self.playWithUI2 = playWithUI
        # self.fast_mode2 = True
        # if playWithUI:
        #     self.gui = Gui()
        #     self.fast_mode2 = False
        self.init_game2()

    def new_stone(self):
        self.stone = self.next_stone[:]
        random.seed(time.clock())
        self.next_stone = tetris_shapes[random.randint(0, len(tetris_shapes)-1)]
        self.stone_x = int(cols / 2 - len(self.stone[0])/2)
        self.stone_y = 0
        self.nbPiece += 1
        self.computed = False

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True
            self.win = 2

    ##
    def new_stone2(self):
        self.stone2 = self.next_stone2[:]
        random.seed(time.clock())
        self.next_stone2 = tetris_shapes[random.randint(0, len(tetris_shapes)-1)]
        self.stone2_x = int(cols / 2 - len(self.stone2[0])/2)
        self.stone2_y = 0
        self.nbPiece2 += 1
        self.computed2 = False

        if check_collision(self.board2,
                           self.stone2,
                           (self.stone2_x, self.stone2_y)):
            self.gameover = True
            self.win = 1

    def init_game(self):
        self.board = new_board()
       

        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0

    ##
    def init_game2(self):
        self.board2 = new_board()
       

        self.new_stone2()
        self.level2 = 1
        self.score2 = 0
        self.lines2 = 0

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level*6:
            self.level += 1

    ##
    def add_cl_lines2(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines2 += n
        self.score2 += linescores[n] * self.level2
        if self.lines2 >= self.level2*6:
            self.level2 += 1

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x
    
    ##
    def move2(self, delta_x):
        if not self.gameover and not self.paused:
            new2_x = self.stone2_x + delta_x
            if new2_x < 0:
                new2_x = 0
            if new2_x > cols - len(self.stone2[0]):
                new2_x = cols - len(self.stone2[0])
            if not check_collision(self.board2,
                                   self.stone2,
                                   (new2_x, self.stone2_y)):
                self.stone2_x = new2_x
            
           

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                  self.board,
                  self.stone,
                  (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0

                for i, row in enumerate(self.board):
                    if 0 not in row:
                        self.board = remove_row(
                          self.board, i)
                        cleared_rows += 1
                self.add_cl_lines(cleared_rows)
                return True
        return False

    ##
    def drop2(self, manual):
        if not self.gameover and not self.paused:
            self.score2 += 1 if manual else 0
            self.stone2_y += 1
            if check_collision(self.board2,
                               self.stone2,
                               (self.stone2_x, self.stone2_y)):
                self.board2 = join_matrixes(
                  self.board2,
                  self.stone2,
                  (self.stone2_x, self.stone2_y))
                self.new_stone2()
                cleared_rows2 = 0

                for i, row in enumerate(self.board2):
                    if 0 not in row:
                        self.board2 = remove_row(
                          self.board2, i)
                        cleared_rows2 += 1
                self.add_cl_lines2(cleared_rows2)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while(not self.drop(True)):
                pass

    ##
    def insta_drop2(self):
        if not self.gameover and not self.paused:
            while(not self.drop2(True)):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    ##
    def rotate_stone2(self):
        if not self.gameover and not self.paused:
            new_stone2 = rotate_clockwise(self.stone2)
            if not check_collision(self.board2,
                                   new_stone2,
                                   (self.stone2_x, self.stone2_y)):
                self.stone2 = new_stone2

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def quit(self):
        if self.playWithUI:
            self.gui.center_msg("Exiting...")
            pygame.display.update()
        exit()

    def speed_up(self):
        self.fast_mode = not self.fast_mode
        if self.fast_mode:
            pygame.time.set_timer(pygame.USEREVENT+1, 2000)
            self.insta_drop()
            ##
            self.insta_drop2()
        else:
            pygame.time.set_timer(pygame.USEREVENT+1, 25)

    def executes_move(self, moves):
        key_actions = {
            'ESCAPE':    self.quit,
            'LEFT':        lambda:self.move(-1),
            'RIGHT':    lambda:self.move(+1),
            # 'DOWN':        lambda:self.drop(True),
            'UP':        self.rotate_stone,
            'p':        self.toggle_pause,
            'SPACE':    self.start_game,
            # 'RETURN':    self.insta_drop,
            'a':        lambda:self.move2(-1),
            'd':    lambda:self.move2(+1),
            # 's':        lambda:self.drop2(True),
            'w':        self.rotate_stone2,
        }
        for action in moves:
            key_actions[action]()

        if self.fast_mode:
            self.insta_drop()
            self.insta_drop2()

    ##
    # def executes_moves2(self, moves):
    #     key_actions = {
    #         'ESCAPE':    self.quit,
    #         'a':        lambda:self.move2(-1),
    #         'd':    lambda:self.move2(+1),
    #         's':        lambda:self.drop2(True),
    #         'w':        self.rotate_stone2,
    #         'p':        self.toggle_pause,
    #         'SPACE':    self.start_game,
    #         'RETURN':    self.insta_drop2
    #     }
    #     for action in moves:
    #         key_actions[action]()

    #     if self.fast_mode:
    #         self.insta_drop2()

    def run(self, weights, limitPiece, win):
        self.gameover = False
        self.paused = False

        # dont_burn_my_cpu = pygame.time.Clock()
        while 1:

            if self.nbPiece >= limitPiece and limitPiece > 0:
                
                self.gameover = True
                
            
            if self.nbPiece2 >= limitPiece and limitPiece > 0:
                
                self.gameover = True
                

            if self.playWithUI:
                self.gui.update(self)

            if self.gameover:
                if self.win == 1:
                    # print(self.win)
                    print("The Winner is AI 1")
                    return self.lines*1000 + self.nbPiece
                # print(self.win)
                print("The Winner is AI 2")
                return self.lines2*1000 + self.nbPiece2

            if not self.computed:
                self.computed = True
                Ai.choose(self.board, self.stone, self.next_stone, self.stone_x, weights, self)
            
            if not self.computed2:
                self.computed2 = True
                Ai2.choose(self.board2, self.stone2, self.next_stone2, self.stone2_x, weights, self)

            if self.playWithUI:
                for event in pygame.event.get():
                    if event.type == pygame.USEREVENT+1:
                        self.drop(False)
                        self.drop2(False)
                    elif event.type == pygame.QUIT:
                            self.quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == eval("pygame.K_s"):
                            self.speed_up()
                        elif event.key == eval("pygame.K_p"):
                            self.toggle_pause()


            ##
            

            # if self.playWithUI:
            #     self.gui.update(self)

            # if self.gameover:
            #     return self.lines*1000 + self.nbPiece

            

            # if self.playWithUI:
            #     for event in pygame.event.get():
            #         if event.type == pygame.USEREVENT+1:
            #             self.drop(False)
            #         elif event.type == pygame.QUIT:
            #                 self.quit()
            #         elif event.type == pygame.KEYDOWN:
            #             if event.key == eval("pygame.K_s"):
            #                 self.speed_up()
            #             elif event.key == eval("pygame.K_p"):
            #                 self.toggle_pause()

            #dont_burn_my_cpu.tick(maxfps)


if __name__ == '__main__':
    weights = [0.39357083734159515, -1.8961941343266449, -5.107694873375318, -3.6314963941589093, -2.9262681134021786, -2.146136640641482, -7.204192964669836, -3.476853402227247, -6.813002842291903, 4.152001386170861, -21.131715861293525, -10.181622180279133, -5.351108175564556, -2.6888972099986956, -2.684925769670947, -4.504495386829769, -7.4527302422826, -6.3489634714511505, -4.701455626343827, -10.502314845278828, 0.6969259450910086, -4.483319180395864, -2.471375907554622, -6.245643268054767, -1.899364785170105, -5.3416512085013395, -4.072687054171711, -5.936652569831475, -2.3140398163110643, -4.842883337741306, 17.677262456993276, -4.42668539845469, -6.8954976464473585, 4.481308299774875] #21755 lignes
    result = TetrisApp(True, 4).run(weights, -1, 0)
    # result2 = TetrisApp(True, 5).run(weights, -1)
    # print("Winner is AI "+ str(winner))
    print("With Score: "+str(result))
