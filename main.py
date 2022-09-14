import pygame

from random import randrange


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.figures = []

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def add_figure(self, figure):
        self.figures.append(figure)

    def render(self, screen):
        pygame.draw.rect(screen, pygame.Color("white"), (
            self.left, self.top, self.cell_size * self.width, self.cell_size * self.height))
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, pygame.Color("black"), (self.left + self.cell_size * x,
                                                                 self.top + self.cell_size * y,
                                                                 self.cell_size,
                                                                 self.cell_size), 1)
            for figure in self.figures:
                figure.render(self, screen)


class Figure:
    def __init__(self, color):
        self.color = color
        self.current_pos = 3, 0
        self.shapes = []
        self.current_shape = randrange(4)

    def render(self, board, screen):
        for x in range(len(self.shapes[self.current_shape][0])):
            for y in range(len(self.shapes[self.current_shape])):
                if self.shapes[self.current_shape][y][x]:
                    pygame.draw.rect(screen, pygame.Color(self.color), (
                        board.left + board.cell_size * (self.current_pos[0] + x),
                        board.top + board.cell_size * (self.current_pos[1] + y),
                        board.cell_size,
                        board.cell_size))

    def rotate_left(self):
        self.current_shape = (self.current_shape + 1) % 4

    def rotate_right(self):
        self.current_shape = (self.current_shape - 1) % 4

    def move_left(self):
        self.current_pos = (self.current_pos[0] - 1, self.current_pos[1])

    def move_right(self):
        self.current_pos = (self.current_pos[0] + 1, self.current_pos[1])

    def move_down(self):
        self.current_pos = (self.current_pos[0], self.current_pos[1] + 1)


class TFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.shapes = [[[1, 1, 1], [0, 1, 0]],
                       [[1, 0], [1, 1], [1, 0]],
                       [[0, 1, 0], [1, 1, 1]],
                       [[0, 1], [1, 1], [0, 1]]]


class QFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.current_shape = 0
        self.shapes = [[[1, 1], [1, 1]]]

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass


class IFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.current_shape = randrange(2)
        self.shapes = [[[1], [1], [1], [1]],
                       [[1, 1, 1, 1]]]

    def rotate_left(self):
        self.current_shape = (self.current_shape + 1) % 2

    def rotate_right(self):
        self.current_shape = (self.current_shape - 1) % 2


class ZFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.current_shape = randrange(2)
        self.shapes = [[[1, 1, 0], [0, 1, 1]],
                       [[0, 1], [1, 1], [1, 0]]]

    def rotate_left(self):
        self.current_shape = (self.current_shape + 1) % 2

    def rotate_right(self):
        self.current_shape = (self.current_shape - 1) % 2


class SFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.current_shape = randrange(2)
        self.shapes = [[[0, 1, 1], [1, 1, 0]],
                       [[1, 0], [1, 1], [0, 1]]]

    def rotate_left(self):
        self.current_shape = (self.current_shape + 1) % 2

    def rotate_right(self):
        self.current_shape = (self.current_shape - 1) % 2


class JFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.shapes = [[[0, 1], [0, 1], [1, 1]],
                       [[1, 1, 1], [0, 0, 1]],
                       [[1, 1], [1, 0], [1, 0]],
                       [[1, 0, 0], [1, 1, 1]]]


class LFigure(Figure):
    def __init__(self, color):
        super().__init__(color)
        self.shapes = [[[1, 0], [1, 0], [1, 1]],
                       [[0, 0, 1], [1, 1, 1]],
                       [[1, 1], [0, 1], [0, 1]],
                       [[1, 1, 1], [1, 0, 0]]]


def main():
    pygame.init()
    pygame.display.set_caption("Тетрис")
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    board = Board(10, 15)
    board.set_view(75, 100, 23)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("grey"))
        board.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
