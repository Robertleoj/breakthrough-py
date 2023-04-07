import numpy as np
import pygame
from sys import argv
import time
import signal
import os

PW = 1
PB = -1

class Board:
    def __init__(self):

        self.turn = PW
        self.history = [np.zeros((8, 8))]
        self.grid_idx = 0
        self.alternate_history = None
        self.alternate_idx = None

        self.grid[:, :2] = PB
        self.grid[:, -2:] = PW
        self.over = False

    @property
    def grid(self):
        """I'm the 'x' property."""
        if self.alternate_idx is not None:
            print("Returning altenate history")
            return self.alternate_history[self.alternate_idx]
        return self.history[self.grid_idx]

    def add_move(self):
        if self.alternate_idx is not None:
            self.alternate_history.append(self.alternate_history[-1].copy())
            self.alternate_idx += 1
        elif self.grid_idx < len(self.history) - 1:
            self.alternate_history = [self.grid.copy()]
            self.alternate_idx = 0
            print("adding to alternate history")
        else:
            self.history.append(self.history[-1].copy())
            self.grid_idx += 1

    def move(self, f, t):

        if not self.is_legal(f, t):
            raise Exception(f"Illegal move, at {self.grid_idx}, from {f} to {t}")

        self.add_move()
        # self.history.append(self.grid.copy())
        # self.grid_idx += 1

        x1, y1 = f
        x2, y2 = t
        
        curr = self.grid[x1][y1]

        self.grid[x1][y1] = 0

        self.grid[x2][y2] = curr

        if y2 == 0 and curr == PW:
            self.over = True

        if y2 == 7 and curr == PB:
            self.over = True

        self.turn *= -1

    def undo(self):
        if self.alternate_idx is not None:
            if self.alternate_idx > 0:
                self.alternate_idx -= 1
                self.alternate_history.pop()
            else:
                self.alternate_idx = None
                self.alternate_history = None
            self.turn *= -1

        elif self.grid_idx > 0:
            self.grid_idx -= 1
            self.turn *= -1

    def redo(self):
        if self.alternate_idx is not None:
            return

        if self.grid_idx < len(self.history) - 1:
            self.grid_idx += 1
            self.turn *= -1

    def beginning(self):
        self.alternate_history = None
        self.alternate_idx = None
        self.grid_idx = 0
        self.turn = PW

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8


    def is_legal(self, f, t):
        if self.over:
            return False

        x1, y1 = f
        x2, y2 = t

        # can not move more than 1 cell in x
        if abs(x1 - x2) > 1:
            return False

        # needs to be in bounds
        if not self.in_bounds(x1, y1) or not self.in_bounds(x2, y2):
            return False

        # can not move empty piece
        if self.grid[x1][y1] == 0:
            return False

        # can not kill own piece
        if abs(x1 - x2) == 1 and self.grid[x2][y2] == self.grid[x1][y1]:
            return False
        
        # cannot capture forward
        if x1 == x2 and self.grid[x2][y2] != 0:
            return False


        # wite pieces move one forward
        if self.grid[x1][y1] == PW and y1 != y2 + 1:
            return False

        # black pieces move one forward
        if self.grid[x1][y1] == PB and y1 != y2 - 1:
            return False

        return True

    def in_alternate(self):
        return self.alternate_idx is not None

    def reset(self):
        self.__init__()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)



class Game:
    def __init__(self):
        self.board = Board()
        pygame.init()
        self.screen_width = 800
        self.screen_height = 800
        self.board_width = 600
        self.board_height = 600

        self.board_start = (self.screen_width - self.board_width) // 2
        self.cell_width = self.board_width // 8

        self.board_surface = pygame.Surface((self.board_width, self.board_height))

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        self.last_cell_clicked = None

        self.wpawn = self.get_pawn("white")
        self.bpawn = self.get_pawn("black")

        pygame.display.set_caption("Breakthrough")

    def get_pawn(self, color):
        img_path = f"assets/pawn_{color}.png"
        pawn = pygame.image.load(img_path)
        pawn = pygame.transform.scale(pawn, (self.cell_width, self.cell_width))
        return pawn


    def draw_coordinates(self):
        # coordinates are like chess
        for i in range(8):
            text = pygame.font.SysFont("comicsans", 40).render(
                chr(ord('A') + i), 1, WHITE
            )
            # draw below the board
            self.screen.blit(
                text,
                (
                    self.board_start + i * self.cell_width + self.cell_width // 2 - text.get_width() // 2,
                    self.board_start + self.board_height + 10,
                ),
            )

        # draw the numbers
        for i in range(8):
            text = pygame.font.SysFont("comicsans", 40).render(
                str(8 - i), 1, WHITE
            )
            # draw to the left of the board, 1 on the botton
            self.screen.blit(
                text,
                (
                    self.board_start - text.get_width() - 10,
                    self.board_start + i * self.cell_width + self.cell_width // 2 - text.get_height() // 2,
                ),
            )



    def draw_board(self):

        self.screen.fill(BLACK)
        self.draw_coordinates()
        
        # chessboard pattern with light and dark brown squares
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(
                        self.board_surface,
                        LIGHT_BROWN,
                        (i * self.cell_width, j * self.cell_width, self.cell_width, self.cell_width),
                    )
                else:
                    pygame.draw.rect(
                        self.board_surface,
                        DARK_BROWN,
                        (i * self.cell_width, j * self.cell_width, self.cell_width, self.cell_width),
                    )

        # draw number of moves above board
        text = pygame.font.SysFont("comicsans", 40).render(
            f"Moves: {self.board.grid_idx}", 1, WHITE
        )

        self.screen.blit(
            text,
            (
                self.board_start + self.board_width // 2 - text.get_width() // 2,
                self.board_start - text.get_height() - 10,
            ),
        )

        # above number of moves, print if we are in alternate history
        if self.board.in_alternate():
            text = pygame.font.SysFont("comicsans", 40).render(
                f"(Alternate history)", 1, WHITE
            )

            self.screen.blit(
                text,
                (
                    self.board_start + self.board_width // 2 - text.get_width() // 2,
                    self.board_start - text.get_height() * 2 - 10,
                ),
            )

        self.screen.blit(self.board_surface, (self.board_start, self.board_start))

        # draw the pieces
        for i in range(8):
            for j in range(8):
                if self.board.grid[i][j] == PW:
                    self.screen.blit(
                        self.wpawn,
                        # (i * self.cell_width + self.cell_width // 2 - self.wpawn.get_width() // 2, j * self.cell_width + self.cell_width // 2 - self.wpawn.get_height() // 2),
                        (self.board_start + i * self.cell_width, self.board_start + j * self.cell_width),
                    )
                    # pygame.draw.circle(
                    #     self.board_surface,
                    #     WHITE,
                    #     (i * self.cell_width + self.cell_width // 2, j * self.cell_width + self.cell_width // 2),
                    #     self.cell_width // 2 - 10,
                    # )
                elif self.board.grid[i][j] == PB:
                    self.screen.blit(
                        self.bpawn,
                        # (i * self.cell_width + self.cell_width // 2 - self.bpawn.get_width() // 2, j * self.cell_width + self.cell_width // 2 - self.bpawn.get_height() // 2),
                        ( self.board_start + i * self.cell_width, self.board_start + j * self.cell_width),
                    )
                    # pygame.draw.circle(
                    #     self.board_surface,
                    #     BLACK,
                    #     (i * self.cell_width + self.cell_width // 2, j * self.cell_width + self.cell_width // 2),
                    #     self.cell_width // 2 - 10,
                    # )


    def handle_click(self, pos):
        x, y = pos
        x -= self.board_start
        y -= self.board_start

        x //= self.cell_width
        y //= self.cell_width

        if not self.board.in_bounds(x, y):
            return

        if self.last_cell_clicked is None:
            if ( int(self.board.grid[x,y]) == 0 
                or int(self.board.grid[x,y]) != self.board.turn
            ):
                return

            self.last_cell_clicked = (x, y)
            print(self.last_cell_clicked)
        else:
            if self.board.is_legal(self.last_cell_clicked, (x, y)):
                print("moving")
                self.board.move(self.last_cell_clicked, (x, y))
                self.last_cell_clicked = None


            elif self.board.grid[x,y] == self.board.turn:
                self.last_cell_clicked = (x, y)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

                # reset board on 'r'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.board.reset()

                    if event.key == pygame.K_RIGHT:
                        self.board.redo()
                    if event.key == pygame.K_LEFT:
                        self.board.undo()

            self.draw_board()
            pygame.display.update()

    def get_coords(self, move_str):
        split_str = 'x' if 'x' in move_str else '-'

        fr, to = move_str.split(split_str)

        fr_x = ord(fr[0]) - ord('a')
        fr_y = 8 - int(fr[1])

        to_x = ord(to[0]) - ord('a')
        to_y = 8 - int(to[1])

        return (fr_x, fr_y), (to_x, to_y)


    def get_clock(self):
        return pygame.time.Clock()

    def play(self, game_str):
        clock = self.get_clock()
        moves = game_str.split(';')

        coords = [self.get_coords(move) for move in moves]
        print(coords)

        for fr, to in coords:
            self.board.move(fr, to)

        self.board.beginning()

        self.draw_board()
        pygame.display.update()

        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

                if event.type == pygame.KEYDOWN:
                    # right arrow to see next move
                    if event.key == pygame.K_RIGHT:
                        self.board.redo()

       
                    if event.key == pygame.K_LEFT:
                        self.board.undo()

            self.draw_board()
            pygame.display.update()
            clock.tick(60)

if __name__ == "__main__":

    def sigint_handler(signal, frame):
        print('Exiting...')
        os._exit(0) # force exit

    signal.signal(signal.SIGINT, sigint_handler)


    print(argv)
    if len(argv) == 2 and argv[1] == 'str':
        print("Game string mode")
        game_str = input()
        print(game_str)
        game = Game()
        game.play(game_str)
    else:
        game = Game()
        game.run()