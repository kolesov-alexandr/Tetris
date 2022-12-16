import sys
import pygame
import sqlite3

from random import randrange, choice

VOCABULARY = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
              'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
MELODIES = ["ghost_fight", "heartache", "bonetrousle", "spear_of_justice", "metal_crusher", "spider_dance",
            "death_by_glamour", "asgore", "hopes_and_dreams", "save_the_world", "battle_against_a_true_hero",
            "megalovania"]


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

    def make_passive(self, sound):
        self.passive_figures.append(self.current_figure)
        self.current_figure.make_passive()
        self.current_figure = None
        self.clear_full_rows(sound)

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

    def clear_full_rows(self, sound):
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
        if cleared_rows_count > 0:
            sound.play()
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

    def move_down(self, sound):
        self.current_pos = self.current_pos[0], self.current_pos[1] + 1
        if self.is_intersection():
            self.current_pos = self.current_pos[0], self.current_pos[1] - 1
            self.board.make_passive(sound)

    def move_to_bottom(self, sound):
        while self.is_active:
            self.move_down(sound)

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


def beginning():
    pygame.init()
    pygame.mixer.music.load("data/start_menu.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    pygame.display.set_caption("Тетрис")
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("grey"))
    running = True
    font_tetris = pygame.font.Font(None, 75)
    tetris_text = font_tetris.render("Тетрис", True, pygame.Color("red"))
    screen.blit(tetris_text, (300 - tetris_text.get_width() // 2, 150))
    font_buttons = pygame.font.Font(None, 30)
    begin_text = font_buttons.render("Начать", True, pygame.Color("red"))
    screen.blit(begin_text, (300 - begin_text.get_width() // 2, 300))
    pygame.draw.rect(screen, pygame.Color("red"), (300 - begin_text.get_width() // 2 - 10, 290,
                                                   begin_text.get_width() + 20, begin_text.get_height() + 20), 1)
    records_text = font_buttons.render("Рекорды", True, pygame.Color("red"))
    screen.blit(records_text, (300 - records_text.get_width() // 2, 360))
    pygame.draw.rect(screen, pygame.Color("red"), (300 - records_text.get_width() // 2 - 10, 350,
                                                   records_text.get_width() + 20, records_text.get_height() + 20), 1)
    exit_text = font_buttons.render("Выйти", True, pygame.Color("red"))
    screen.blit(exit_text, (300 - exit_text.get_width() // 2, 420))
    pygame.draw.rect(screen, pygame.Color("red"), (300 - exit_text.get_width() // 2 - 10, 410,
                                                   exit_text.get_width() + 20, exit_text.get_height() + 20), 1)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if 300 - begin_text.get_width() // 2 - 10 <= x <= 300 + begin_text.get_width() // 2 + 10 and \
                        290 <= y <= 300 + begin_text.get_height() + 10:
                    running = False
                if 300 - records_text.get_width() // 2 - 10 <= x <= 300 + records_text.get_width() // 2 + 10 and \
                        350 <= y <= 360 + records_text.get_height() + 10:
                    running = False
                    records()
                if 300 - exit_text.get_width() // 2 - 10 <= x <= 300 + exit_text.get_width() // 2 + 10 and \
                        410 <= y <= 420 + exit_text.get_height() + 10:
                    sys.exit(0)


def records():
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("grey"))
    running = True
    con = sqlite3.connect("data/bd.sqlite")
    cur = con.cursor()
    result = cur.execute("SELECT player, score FROM records ORDER BY score DESC").fetchall()
    con.close()
    font_records = pygame.font.Font(None, 30)
    font_records_text = pygame.font.Font(None, 40)
    records_player_text = font_records_text.render("Игрок", True, pygame.Color("red"))
    screen.blit(records_player_text, (150, 40))
    records_score_text = font_records_text.render("Счёт", True, pygame.Color("red"))
    screen.blit(records_score_text, (400, 40))
    height0 = 100
    for i in range(10):
        if i < len(result):
            player = font_records.render(result[i][0], True, pygame.Color("red"))
            screen.blit(player, (150 + records_player_text.get_width() // 2 - player.get_width() // 2, height0))
            score = font_records.render("{:04}".format(result[i][1]), True, pygame.Color("red"))
            screen.blit(score, (400 + records_score_text.get_width() // 2 - score.get_width() // 2, height0))

        else:
            player = font_records.render("---", True, pygame.Color("red"))
            screen.blit(player, (150 + records_player_text.get_width() // 2 - player.get_width() // 2, height0))
            score = font_records.render("{:04}".format(0), True, pygame.Color("red"))
            screen.blit(score, (400 + records_score_text.get_width() // 2 - score.get_width() // 2, height0))
        height0 += 40
    font_back = pygame.font.Font(None, 30)
    text_back = font_back.render("Вернуться", True, pygame.Color("red"))
    screen.blit(text_back, (300 - text_back.get_width() // 2, 510))
    pygame.draw.rect(screen, pygame.Color("red"), (300 - text_back.get_width() // 2 - 10, 500,
                                                   text_back.get_width() + 20, text_back.get_height() + 20), 1)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if 300 - text_back.get_width() // 2 - 10 <= x <= 300 + text_back.get_width() // 2 + 10 and \
                        500 <= y <= 510 + text_back.get_height() + 10:
                    running = False
                    beginning()


def player_name():
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("grey"))
    font_error = pygame.font.Font(None, 30)
    font_name = pygame.font.Font(None, 50)
    font_letter = pygame.font.Font(None, 100)
    text_name1 = font_name.render("ПОЖАЛУЙСТА,", True, pygame.Color("red"))
    screen.blit(text_name1, (300 - text_name1.get_width() // 2, 200))
    text_name2 = font_name.render("ВВЕДИТЕ СВОЁ ИМЯ", True, pygame.Color("red"))
    screen.blit(text_name2, (300 - text_name2.get_width() // 2, 240))
    text_empty = font_letter.render("_", True, pygame.Color("red"))
    screen.blit(text_empty, (300 - text_empty.get_width() // 2 - 20 - text_empty.get_width(), 300))
    screen.blit(text_empty, (300 - text_empty.get_width() // 2, 300))
    screen.blit(text_empty, (300 + text_empty.get_width() // 2 + 20, 300))
    text_error = font_error.render("НЕИЗВЕСТНЫЙ СИМВОЛ", True, pygame.Color("red"))
    text_letter1 = None
    text_letter2 = None
    text_letter3 = None
    name = ""
    is_error = False
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if not text_letter1:
                    try:
                        text_letter1 = font_letter.render(VOCABULARY[event.key - 97], True, pygame.Color("red"))
                        screen.blit(text_letter1, (300 - text_empty.get_width() // 2 - 20 -
                                                   text_empty.get_width(), 295))
                        name += VOCABULARY[event.key - 97]
                        is_error = False
                    except IndexError:
                        screen.blit(text_error, (300 - text_error.get_width() // 2, 500))
                        is_error = True
                elif not text_letter2:
                    try:
                        text_letter2 = font_letter.render(VOCABULARY[event.key - 97], True, pygame.Color("red"))
                        screen.blit(text_letter2, (300 - text_empty.get_width() // 2, 295))
                        name += VOCABULARY[event.key - 97]
                        is_error = False
                    except IndexError:
                        screen.blit(text_error, (300 - text_error.get_width() // 2, 500))
                        is_error = True
                else:
                    try:
                        text_letter3 = font_letter.render(VOCABULARY[event.key - 97], True, pygame.Color("red"))
                        screen.blit(text_letter3, (300 + text_empty.get_width() // 2 + 20, 295))
                        name += VOCABULARY[event.key - 97]
                        is_error = False
                        running = False
                    except IndexError:
                        screen.blit(text_error, (300 - text_error.get_width() // 2, 500))
                        is_error = True
        screen.fill(pygame.Color("grey"))
        screen.blit(text_name1, (300 - text_name1.get_width() // 2, 200))
        screen.blit(text_name2, (300 - text_name2.get_width() // 2, 240))
        screen.blit(text_empty, (300 - text_empty.get_width() // 2 - 20 - text_empty.get_width(), 300))
        screen.blit(text_empty, (300 - text_empty.get_width() // 2, 300))
        screen.blit(text_empty, (300 + text_empty.get_width() // 2 + 20, 300))
        if text_letter1:
            screen.blit(text_letter1, (300 - text_empty.get_width() // 2 - 20 - text_empty.get_width(), 295))
        if text_letter2:
            screen.blit(text_letter2, (300 - text_empty.get_width() // 2, 295))
        if text_letter3:
            screen.blit(text_letter3, (300 + text_empty.get_width() // 2 + 20, 295))
        if is_error:
            screen.blit(text_error, (300 - text_error.get_width() // 2, 500))
        pygame.display.flip()
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    return name


def main():
    while True:
        beginning()
        name = player_name()
        full_sound = pygame.mixer.Sound("data/full.wav")
        music = choice(MELODIES)
        pygame.mixer.music.load("data/" + music + ".mp3")
        pygame.mixer.music.play(-1)
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
                    running = False
                pygame.time.set_timer(pygame.USEREVENT, 1000)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        current_figure.move_left()
                    if event.key == pygame.K_d:
                        current_figure.move_right()
                    if event.key == pygame.K_s:
                        current_figure.move_down(full_sound)
                    if event.key == pygame.K_f:
                        current_figure.move_to_bottom(full_sound)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        current_figure.rotate_left()
                    if event.button == 3:
                        current_figure.rotate_right()
                if event.type == pygame.USEREVENT:
                    current_figure.move_down(full_sound)
            screen.fill(pygame.Color("grey"))
            board.render(screen)
            count_number_text = font_number_text.render(str(board.score), True, pygame.Color("red"))
            screen.blit(count_text, (400, 100))
            screen.blit(count_number_text,
                        (400 + count_text.get_width() // 2 - count_number_text.get_width() // 2, 150))
            pygame.display.flip()
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        con = sqlite3.connect("data/bd.sqlite")
        cur = con.cursor()
        player = cur.execute("SELECT player, score FROM records WHERE player = ?", (name,)).fetchone()
        if not player:
            cur.execute("INSERT INTO records(player, score) VALUES(?, ?)", (name, board.score))
        elif board.score > player[1]:
            cur.execute("UPDATE records SET score = ? WHERE player = ?", (board.score, name))
        con.commit()
        con.close()
        ending(board.score)


def ending(score):
    pygame.mixer.music.load("data/determination.mp3")
    pygame.mixer.music.play(-1)
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("grey"))
    font_score = pygame.font.Font(None, 50)
    score_text = font_score.render("ВАШ СЧЁТ:", True, pygame.Color("red"))
    screen.blit(score_text, (300 - score_text.get_width() // 2, 230))
    score_number = font_score.render(str(score), True, pygame.Color("red"))
    screen.blit(score_number, (300 - score_number.get_width() // 2, 300))
    font_back = pygame.font.Font(None, 30)
    text_back = font_back.render("Вернуться", True, pygame.Color("red"))
    screen.blit(text_back, (300 - text_back.get_width() // 2, 400))
    pygame.draw.rect(screen, pygame.Color("red"), (300 - text_back.get_width() // 2 - 10, 390,
                                                   text_back.get_width() + 20, text_back.get_height() + 20), 1)
    running = True
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if 300 - text_back.get_width() // 2 - 10 <= x <= 300 + text_back.get_width() // 2 + 10 and \
                        390 <= y <= 400 + text_back.get_height() + 10:
                    running = False
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()


if __name__ == '__main__':
    main()
