import pygame

from random import randrange, choice


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.passive_figures = []
        self.current_figure = None
        self.score = 0

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def add_figure(self, figure):
        self.current_figure = figure

    def make_passive(self):
        self.passive_figures.append(self.current_figure)
        self.current_figure.make_passive()
        self.current_figure = None
        self.clear_full_rows()

    def render(self, screen):
        pygame.draw.rect(screen, pygame.Color("white"), (
            self.left, self.top, self.cell_size * self.width, self.cell_size * self.height))
        for figure in self.passive_figures:
            figure.render(screen)
        if self.current_figure:
            self.current_figure.render(screen)
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, pygame.Color("black"), (self.left + self.cell_size * x,
                                                                 self.top + self.cell_size * y,
                                                                 self.cell_size,
                                                                 self.cell_size), 1)

    def get_current_figure(self):
        return self.current_figure

    def clear_full_rows(self):
        self.board = [[0] * self.width for _ in range(self.height)]
        for fig in self.passive_figures:
            for x in range(len(fig.shapes[fig.current_shape][0])):
                for y in range(len(fig.shapes[fig.current_shape])):
                    if fig.shapes[fig.current_shape][y][x] == 1:
                        self.board[fig.current_pos[1] + y][fig.current_pos[0] + x] = 1
        cleared_rows_count = 0
        for row in range(len(self.board)):
            if 0 not in self.board[row]:
                for fig in self.passive_figures:
                    fig.shapes[fig.current_shape].append([0] * len(fig.shapes[fig.current_shape][0]))
                    flag1 = False
                    flag2 = False
                    for y in range(len(fig.shapes[fig.current_shape]) - 2, -1, -1):
                        if fig.current_pos[1] + y == row:
                            fig.shapes[fig.current_shape][y] = [0] * len(fig.shapes[fig.current_shape][0])
                            flag1 = True
                        elif fig.current_pos[1] + y < row:
                            fig.shapes[fig.current_shape][y + 1] = fig.shapes[fig.current_shape][y]
                            flag2 = True
                    if flag2:
                        fig.shapes[fig.current_shape] = fig.shapes[fig.current_shape][1:]
                        fig.current_pos = fig.current_pos[0], fig.current_pos[1] + 1
                    if flag1 or not flag2:
                        fig.shapes[fig.current_shape].pop()
                cleared_rows_count += 1
        self.score += cleared_rows_count * 100


class Figure:
    def __init__(self, board, color):
        self.color = color
        self.current_pos = 3, 0
        self.shapes = []
        self.current_shape = randrange(4)
        self.is_active = True
        self.board = board

    def render(self, screen):
        for x in range(len(self.shapes[self.current_shape][0])):
            for y in range(len(self.shapes[self.current_shape])):
                if self.shapes[self.current_shape][y][x] and self.current_pos[1] + y >= 0:
                    pygame.draw.rect(screen, pygame.Color(self.color), (
                        self.board.left + self.board.cell_size * (self.current_pos[0] + x),
                        self.board.top + self.board.cell_size * (self.current_pos[1] + y),
                        self.board.cell_size,
                        self.board.cell_size))

    def rotate_left(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape + 1) % 4
        if self.is_intersection():
            self.current_shape = (self.current_shape - 1) % 4
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]

    def rotate_right(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape - 1) % 4
        if self.is_intersection():
            self.current_shape = (self.current_shape + 1) % 4
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]

    def move_left(self):
        self.current_pos = max(0, self.current_pos[0] - 1), self.current_pos[1]
        if self.is_intersection():
            self.current_pos = self.current_pos[0] + 1, self.current_pos[1]

    def move_right(self):
        self.current_pos = min(self.board.width - len(self.shapes[self.current_shape][0]),
                               self.current_pos[0] + 1), self.current_pos[1]
        if self.is_intersection():
            self.current_pos = self.current_pos[0] - 1, self.current_pos[1]

    def move_down(self):
        self.current_pos = self.current_pos[0], self.current_pos[1] + 1
        if self.is_intersection():
            self.current_pos = self.current_pos[0], self.current_pos[1] - 1
            self.board.make_passive()

    def move_to_bottom(self):
        while self.is_active:
            self.move_down()

    def make_passive(self):
        self.is_active = False

    def is_intersection(self):
        for fig in self.board.passive_figures:
            if self.current_pos[0] + len(self.shapes[self.current_shape][0]) - 1 >= fig.current_pos[0] and \
                    self.current_pos[1] + len(self.shapes[self.current_shape]) - 1 >= fig.current_pos[1] or \
                    self.current_pos[0] + len(self.shapes[self.current_shape][0]) - 1 >= fig.current_pos[0] and \
                    fig.current_pos[1] + len(fig.shapes[fig.current_shape]) - 1 >= self.current_pos[1] or \
                    fig.current_pos[0] + len(fig.shapes[fig.current_shape][0]) - 1 >= self.current_pos[0] and \
                    self.current_pos[1] + len(self.shapes[self.current_shape]) - 1 >= fig.current_pos[1] or \
                    fig.current_pos[0] + len(fig.shapes[fig.current_shape][0]) - 1 >= self.current_pos[0] and \
                    fig.current_pos[1] + len(fig.shapes[fig.current_shape]) - 1 >= self.current_pos[1]:
                pos = max(self.current_pos[0], fig.current_pos[0]), max(self.current_pos[1], fig.current_pos[1])
                current_figure_condition = []
                fig_condition = []
                for y in range(pos[1] - self.current_pos[1], min(
                        self.current_pos[1] + len(self.shapes[self.current_shape]),
                        fig.current_pos[1] + len(fig.shapes[fig.current_shape])) - self.current_pos[1]):
                    current_figure_condition.append([])
                    for x in range(pos[0] - self.current_pos[0], min(
                            self.current_pos[0] + len(self.shapes[self.current_shape][0]),
                            fig.current_pos[0] + len(fig.shapes[fig.current_shape][0])) - self.current_pos[0]):
                        current_figure_condition[-1].append(self.shapes[self.current_shape][y][x])
                for y in range(pos[1] - fig.current_pos[1], min(
                        self.current_pos[1] + len(self.shapes[self.current_shape]),
                        fig.current_pos[1] + len(fig.shapes[fig.current_shape])) - fig.current_pos[1]):
                    fig_condition.append([])
                    for x in range(pos[0] - fig.current_pos[0], min(
                            self.current_pos[0] + len(self.shapes[self.current_shape][0]),
                            fig.current_pos[0] + len(fig.shapes[fig.current_shape][0])) - fig.current_pos[0]):
                        fig_condition[-1].append(fig.shapes[fig.current_shape][y][x])
                for y in range(len(current_figure_condition)):
                    for x in range(len(current_figure_condition[0])):
                        if current_figure_condition[y][x] == fig_condition[y][x] == 1:
                            return True
        if self.current_pos[1] > self.board.height - len(self.shapes[self.current_shape]):
            return True
        return False


class TFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.shapes = [[[1, 1, 1], [0, 1, 0]],
                       [[1, 0], [1, 1], [1, 0]],
                       [[0, 1, 0], [1, 1, 1]],
                       [[0, 1], [1, 1], [0, 1]]]


class QFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.current_shape = 0
        self.shapes = [[[1, 1], [1, 1]]]

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass


class IFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.current_shape = randrange(2)
        self.shapes = [[[1], [1], [1], [1]],
                       [[1, 1, 1, 1]]]

    def rotate_left(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape + 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape - 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 1), self.current_pos[1]

    def rotate_right(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape - 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape + 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 1), self.current_pos[1]


class ZFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.current_shape = randrange(2)
        self.shapes = [[[1, 1, 0], [0, 1, 1]],
                       [[0, 1], [1, 1], [1, 0]]]

    def rotate_left(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape + 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape - 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]

    def rotate_right(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape - 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape + 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]


class SFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.current_shape = randrange(2)
        self.shapes = [[[0, 1, 1], [1, 1, 0]],
                       [[1, 0], [1, 1], [0, 1]]]

    def rotate_left(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape + 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape - 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]

    def rotate_right(self):
        old_length = len(self.shapes[self.current_shape][0])
        self.current_shape = (self.current_shape - 1) % 2
        if self.is_intersection():
            self.current_shape = (self.current_shape + 1) % 2
        else:
            new_length = len(self.shapes[self.current_shape][0])
            self.current_pos = min(self.current_pos[0],
                                   self.board.width - new_length + old_length - 2), self.current_pos[1]


class JFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.shapes = [[[0, 1], [0, 1], [1, 1]],
                       [[1, 1, 1], [0, 0, 1]],
                       [[1, 1], [1, 0], [1, 0]],
                       [[1, 0, 0], [1, 1, 1]]]


class LFigure(Figure):
    def __init__(self, board, color):
        super().__init__(board, color)
        self.shapes = [[[1, 0], [1, 0], [1, 1]],
                       [[0, 0, 1], [1, 1, 1]],
                       [[1, 1], [0, 1], [0, 1]],
                       [[1, 1, 1], [1, 0, 0]]]


FIGURES = [TFigure, QFigure, IFigure, ZFigure, SFigure, JFigure, LFigure]
COLORS = ["red", "blue", "violet", "yellow", "green", "lightblue"]


def main():
    pygame.init()
    pygame.display.set_caption("Тетрис")
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    board = Board(10, 15)
    board.set_view(75, 100, 23)
    running = True
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font_text = pygame.font.Font(None, 35)
    font_number_text = pygame.font.Font(None, 30)
    count_text = font_text.render("Счёт:", True, pygame.Color("red"))
    while running:
        if board.get_current_figure():
            current_figure = board.get_current_figure()
        else:
            current_figure = choice(FIGURES)(board, choice(COLORS))
            board.add_figure(current_figure)
            if current_figure.is_intersection():
                while current_figure.is_intersection():
                    current_figure.current_pos = current_figure.current_pos[0], current_figure.current_pos[1] - 1
            pygame.time.set_timer(pygame.USEREVENT, 1000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    current_figure.move_left()
                if event.key == pygame.K_d:
                    current_figure.move_right()
                if event.key == pygame.K_s:
                    current_figure.move_down()
                if event.key == pygame.K_f:
                    current_figure.move_to_bottom()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    current_figure.rotate_left()
                if event.button == 3:
                    current_figure.rotate_right()
            if event.type == pygame.USEREVENT:
                current_figure.move_down()
        screen.fill(pygame.Color("grey"))
        board.render(screen)
        count_number_text = font_number_text.render(str(board.score), True, pygame.Color("red"))
        screen.blit(count_text, (400, 100))
        screen.blit(count_number_text, (400 + count_text.get_width() // 2 - count_number_text.get_width() // 2, 150))
        pygame.display.flip()


if __name__ == '__main__':
    main()
