import pygame


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, pygame.Color("white"), (self.left + self.cell_size * x,
                                                                 self.top + self.cell_size * y,
                                                                 self.cell_size,
                                                                 self.cell_size), 1)


def main():
    pygame.init()
    pygame.display.set_caption("Тетрис")
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    board = Board(10, 20)
    board.set_view(150, 25, 23)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("royalblue"))
        board.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
