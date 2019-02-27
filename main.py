import pygame
import numpy as np
from random import randrange


def generate_field(w, h, m):
    w += 1
    h += 1
    field = np.zeros((h, w), dtype=int)
    while m:
        generate_mine(field, (randrange(1, h), randrange(1, w)), m)
    field[field > 9] = 9
    return field[1:, 1:]


def generate_mine(field, pos, counter):
    if field[pos] < 8:
        field[pos] = 8
        x = pos[0]
        y = pos[1]
        field[x - 1:x + 2, y - 1:y + 2] += 1
        counter.pop()


pygame.init()


class Cell(pygame.sprite.Sprite):
    font = pygame.font.Font(None, 26)
    font.set_bold(True)
    colors = {0: (50, 50, 50),
              1: (0, 200, 255),
              2: (0, 100, 0),
              3: (50, 200, 50),
              4: (255, 255, 0),
              5: (200, 200, 0),
              6: (255, 200, 0),
              7: (255, 155, 0),
              8: (255, 0, 0),
              9: (255, 0, 0)}
    bg_color = (50, 50, 50)
    fg_color = (255, 255, 255)
    md_color = (255, 255, 0)

    def __init__(self, mines_around, pos, index):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(Cell.fg_color)
        self.mine = False
        self.blank = False
        self.text = self._get_text(mines_around)
        self.pos = pos
        self.opened = False
        self.marked = False
        self.rect = self.image.get_rect(topleft=pos)
        self.index = index
        self.explode = False
        # print(self.index)

    def _get_text(self, mines):
        if mines in range(1, 9):
            txt = Cell.font.render(" " + str(mines), True, Cell.colors[mines], (50, 50, 50))
        elif mines == 9:
            txt = pygame.Surface((20, 20))
            txt.fill((255, 0, 0))
            self.mine = True
        elif mines == 0:
            txt = pygame.Surface((20, 20))
            txt.fill((50, 50, 50))
            self.blank = True
        return txt

    def open(self, group):
        if not self.opened:
            self.image.fill((50, 50, 50))
            self.image.blit(self.text, (0, 0))
            self.opened = True
            if self.mine:
                self.explode = True
            if self.blank:
                for n in self._get_neighbors(group):
                    n.open(group)

    def _get_neighbors(self, group):
        neighbors = []
        c_y = self.index[0]
        c_x = self.index[1]
        for s in group:
            n_x = s.index[0]
            n_y = s.index[1]
            if (n_x, n_y) in ((c_y - 1, c_x - 1),
                              (c_y - 1, c_x + 0),
                              (c_y - 1, c_x + 1),
                              (c_y + 0, c_x - 1),
                              (c_y + 0, c_x + 1),
                              (c_y + 1, c_x - 1),
                              (c_y + 1, c_x + 0),
                              (c_y + 1, c_x + 1),):
                neighbors.append(s)
        return neighbors

    def mark(self):
        if not self.opened:
            if not self.marked:
                self.image.fill(Cell.md_color)
                self.marked = True
            else:
                self.image.fill(Cell.fg_color)
                self.marked = False

    def open_neighbors(self, group):
        if self.opened:
            for n in self._get_neighbors(group):
                if not n.opened and not n.marked:
                        n.open(group)


h = 10
w = 15
m = [0] * (w * h // 9)
mines = str(w * h // 9)
marked_mines = 0
field = generate_field(w, h, m)
# print(field)
sep = 5

drawn_field = pygame.sprite.RenderPlain()
for (y, x), value in np.ndenumerate(field):
    # print(x, y, value)
    cell = Cell(value, (sep + x * (sep + 20), sep + y * (sep + 20)), (x, y))
    drawn_field.add(cell)


screen = pygame.display.set_mode(((20 + sep) * w, (20 + sep) * h))
pygame.display.set_caption("Miner")

mouse_pos = [-1, -1]
is_alive = True
while is_alive:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()  
            for s in drawn_field:
                if s.rect.collidepoint(mouse_pos):
                    if event.button == 1:
                        s.open(drawn_field)
                    elif event.button == 2:
                        s.open_neighbors(drawn_field)
                    elif event.button == 3:
                        s.mark()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                for s in drawn_field:
                    if s.blank and not s.opened:
                        #print("c")
                        s.open(drawn_field)
                        break

    marked_mines = 0
    for s in drawn_field:
        if s.mine and s.opened:
            is_alive = False
        if s.marked:
            marked_mines += 1
    if is_alive:
        for s in drawn_field:
            if s.opened and not s.mine:
                is_alive = False
            elif s.mine:
                pass
            else:
                is_alive = True
                break
    else:
        for s in drawn_field:
            if s.mine:
                s.open(drawn_field)
    pygame.display.set_caption("Miner   %s/%s" % (str(marked_mines), mines))
    drawn_field.draw(screen)

    pygame.display.flip()

pygame.quit()
