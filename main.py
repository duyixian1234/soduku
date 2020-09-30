import time
from typing import List

import pygame

pygame.font.init()
import random
import time
from typing import List

#Defining Board Size


class Board:
    BASE = set(range(1, 10))

    def getValidValues(self, x: int, y: int):
        row = self.board[x]
        column = self.columns[y]
        blockX = x // 3
        blockY = y // 3
        block = self.blocks[blockX * 3 + blockY]
        s = set((*row, *column, *block))
        return self.BASE - s

    def set(self, x: int, y: int, value: str):
        self.board[x][y] = value
        self.columns[y][x] = value
        self.blocks[x // 3 * 3 + y // 3][x % 3 * 3 + y % 3] = value

    def get_effect(self, x: int, y: int, n: int):
        value = self.board[x][y]
        effects = []
        for index in self.effect_rows[x]:
            if index > n:
                if value in self.targets[index][2]:
                    self.targets[index][2].remove(value)
                    effects.append(index)
        return effects

    def reset_effect(self, effects: int, value: int):
        for index in effects:
            self.targets[index][2].add(value)

    def dfs(self, n: int):
        if n >= len(self.targets):
            return True

        x, y, _ = self.targets[n]
        values = list(self.getValidValues(x, y))
        random.shuffle(values)
        for value in values:
            self.set(x, y, value)
            effects = self.get_effect(x, y, n)
            if self.dfs(n + 1):
                return True
            self.set(x, y, '.')
            self.reset_effect(effects, value)

    def prepare(self, board: List[List[str]]):
        self.board = board.copy()
        self.targets = []
        self.columns = [[row[i] for row in self.board] for i in range(9)]
        self.blocks = [[
            self.board[_x][_y] for _x in range(3 * x, 3 * x + 3)
            for _y in range(3 * y, 3 * y + 3)
        ] for x in range(3) for y in range(3)]
        self.targets = [(x, y, self.getValidValues(x, y)) for x in range(9)
                        for y in range(9) if self.board[x][y] == 0]
        self.targets.sort(key=lambda x: len(x[2]))
        self.effect_rows = [[] for _ in range(9)]
        self.effect_columns = [[] for _ in range(9)]
        self.effect_blocks = [[] for _ in range(9)]
        for index, value in enumerate(self.targets):
            x, y, _ = value
            self.effect_rows[x].append(index)
            self.effect_columns[y].append(index)
            self.effect_rows[x // 3 * 3 + y // 3].append(index)

    def gen_board(self, unknown: int = 45):
        self.prepare([[0] * 9 for _ in range(9)])
        self.dfs(0)
        unknowns = set([])
        for _ in range(unknown):
            while (pair:=(random.randint(0, 8), random.randint(0, 8))) in unknowns:
                pass
            unknowns.add(pair)

        for x, y in unknowns:
            self.board[x][y] = 0
        return self.board

    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        self.prepare([[0] * 9 for _ in range(9)])
        self.dfs(0)
        return self.board


class Grid:
    #defining titles
    def __init__(self, rows, cols, width, height, win):
        self.board = Board().gen_board(50)
        self.rows = rows
        self.cols = cols
        self.cubes = [[
            Cube(self.board[i][j], i, j, width, height) for j in range(cols)
        ] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.win = win
        self.BASE = set(range(1, 10))
        self.clock =pygame.time.Clock()

    def reset(self,rows:int=9,cols:int=9):
        self.board = Board().gen_board(50)
        self.cubes = [[
            Cube(self.board[i][j], i, j, self.width, self.height) for j in range(cols)
        ] for i in range(rows)]
        self.model = None
        self.update_model()
        self.selected = None

    def gen_board(self):
        self.boards = [[0] * 9 for _ in range(9)]
        self.columns = [[row[i] for row in self.board] for i in range(9)]
        self.blocks = [[
            self.board[_x][_y] for _x in range(3 * x, 3 * x + 3)
            for _y in range(3 * y, 3 * y + 3)
        ] for x in range(3) for y in range(3)]
        for x in range(9):
            for y in range(9):
                values = self.getValidValues(x, y)
                value = random.choice(list(values))
                self.board[x][y] = value
                self.columns[y][x] = value
                self.blocks[x // 3 * 3 + y // 3][x % 3 * 3 + y % 3] = value
        print(self.board)

    def getValidValues(self, x: int, y: int):
        row = self.board[x]
        column = self.columns[y]
        blockX = x // 3
        blockY = y // 3
        block = self.blocks[blockX * 3 + blockY]
        s = set((*row, *column, *block))
        return self.BASE - s

    def set(self, x: int, y: int, value: str):
        self.board[x][y] = value
        self.columns[y][x] = value
        self.blocks[x // 3 * 3 + y // 3][x % 3 * 3 + y % 3] = value
        self.cubes[x][y].set(value)
        if value:
            self.cubes[x][y].draw_change(self.win, True)
        self.update_model()
        if not value:
            self.cubes[x][y].draw_change(self.win, False)
        pygame.display.update()
        # time.sleep(0.1)
        self.clock.tick(1)

    def get_effect(self, x: int, y: int, n: int):
        value = self.board[x][y]
        effects = []
        for index in self.effect_rows[x]:
            if index > n:
                if value in self.targets[index][2]:
                    self.targets[index][2].remove(value)
                    effects.append(index)
        return effects

    def reset_effect(self, effects: int, value: int):
        for index in effects:
            self.targets[index][2].add(value)

    def prepare(self):
        self.targets = []
        self.columns = [[row[i] for row in self.board] for i in range(9)]
        self.blocks = [[
            self.board[_x][_y] for _x in range(3 * x, 3 * x + 3)
            for _y in range(3 * y, 3 * y + 3)
        ] for x in range(3) for y in range(3)]
        self.targets = [(x, y, self.getValidValues(x, y)) for x in range(9)
                        for y in range(9) if self.board[x][y] == 0]
        self.targets.sort(key=lambda x: len(x[2]))
        self.effect_rows = [[] for _ in range(9)]
        self.effect_columns = [[] for _ in range(9)]
        self.effect_blocks = [[] for _ in range(9)]
        for index, value in enumerate(self.targets):
            x, y, _ = value
            self.effect_rows[x].append(index)
            self.effect_columns[y].append(index)
            self.effect_rows[x // 3 * 3 + y // 3].append(index)

    def dfs(self, n: int):
        if n >= len(self.targets):
            return True

        x, y, _ = self.targets[n]
        values = list(self.getValidValues(x, y))
        random.shuffle(values)
        for value in values:
            self.set(x, y, value)
            effects = self.get_effect(x, y, n)
            if self.dfs(n + 1):
                return True
            self.set(x, y, 0)
            self.reset_effect(effects, value)

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)]
                      for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Drawing Grid Lines
        gap = self.width // 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0, 0, 0), (0, i * gap),
                             (self.width, i * gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0),
                             (i * gap, self.height), thick)

        # Drawing Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width // 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model = i

                if self.solve():
                    return True

                self.model = 0

        return False

    def solve_gui(self):
        self.prepare()
        self.dfs(0)


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width // 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x + 5, y + 5))
        elif not (self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap // 2 - text.get_width() // 2), y +
                            (gap // 2 - text.get_height() // 2)))

        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width // 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap // 2 - text.get_width() // 2), y +
                        (gap // 2 - text.get_height() // 2)))
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col

    return None


def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True


def redraw_window(win, board, time, strikes):
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    mat = " " + str(minute) + ":" + str(sec)
    return mat


#Title Portion
def main():
    win = pygame.display.set_mode((540, 600))
    pygame.display.set_caption("Sudoku Pygame (Press Space to do auto solve) ")
    board = Grid(9, 9, 540, 540, win)
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:

        play_time = round(time.time() - start)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    board.solve_gui()
                
                if event.key == pygame.K_r:
                    board.reset()   


# Click Event
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()

if __name__ == '__main__':
    main()
    pygame.quit()
