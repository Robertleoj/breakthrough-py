import numpy as np
import pygame
from sys import argv
import time

PW = 1
PB = -1

class Board:
    def __init__(self):
        self.grid = np.zeros((8, 8))
        self.grid[:, :2] = PB
        self.grid[:, -2:] = PW
        self.over = False

    def move(self, f, t):
        x1, y1 = f
        x2, y2 = t
        
        curr = self.grid[x1][y1]

        self.grid[x1][y1] = 0

        self.grid[x2][y2] = curr

        if y2 == 0 and curr == PW:
            self.over = True

        if y2 == 7 and curr == PB:
            self.over = True

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def is_legal(self, f, t):
        if self.over:
            return False

        x1, y1 = f
        x2, y2 = t
        if abs(x1 - x2) > 1:
            return False

        if not self.in_bounds(x1, y1) or not self.in_bounds(x2, y2):
            return False

        if self.grid[x1][y1] == 0:
            return False


        if self.grid[x1][y1] == PW:
            if y1 != y2 + 1:
                return False

            if x1 == x2 and self.grid[x2][y2] != 0:
                return False

        if self.grid[x1][y1] == PB:
            if y1 != y2 - 1:
                return False

            if x1 == x2 and self.grid[x2][y2] != 0:
                return False


        return True

    def reset(self):
        self.__init__()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = PW
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

        self.draw_coordinates()

        pygame.display.set_caption("Breakthrough")

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

        # draw the pieces
        for i in range(8):
            for j in range(8):
                if self.board.grid[i][j] == PW:
                    pygame.draw.circle(
                        self.board_surface,
                        WHITE,
                        (i * self.cell_width + self.cell_width // 2, j * self.cell_width + self.cell_width // 2),
                        self.cell_width // 2 - 10,
                    )
                elif self.board.grid[i][j] == PB:
                    pygame.draw.circle(
                        self.board_surface,
                        BLACK,
                        (i * self.cell_width + self.cell_width // 2, j * self.cell_width + self.cell_width // 2),
                        self.cell_width // 2 - 10,
                    )

        self.screen.blit(self.board_surface, (self.board_start, self.board_start))

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
                or int(self.board.grid[x,y]) != self.turn
            ):
                return

            self.last_cell_clicked = (x, y)
            print(self.last_cell_clicked)
        else:
            if self.board.is_legal(self.last_cell_clicked, (x, y)):
                self.board.move(self.last_cell_clicked, (x, y))
                self.last_cell_clicked = None

                self.turn *= -1

            elif self.board.grid[x,y] == self.turn:
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
                        self.turn = PW

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



    def play(self, game_str):
        moves = game_str.split(';')

        coords = list(reversed([self.get_coords(move) for move in moves]))
        print(coords)

        self.draw_board()
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if len(coords) == 0:
                            continue
                        fr, to = coords.pop()

                        self.board.move(fr, to)

                        self.draw_board()
                        pygame.display.update()
       

if __name__ == "__main__":

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