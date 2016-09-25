from random import shuffle

import pygame as pg

from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup
from ..components.animation import Animation
from ..components.puzzle import Piece, GridCell


class SlideTitle(object):
    def __init__(self, topleft, image, cell_size):
        self.topleft = topleft
        self.image = image
        self.animations = pg.sprite.Group()
        self.done = False
        self.cell_size = cell_size
        w, h = self.image.get_size()
        self.num_rows = h // self.cell_size[1]
        self.num_columns = w // self.cell_size[0]
        self.empty_index = self.num_columns-1, 0
        self.empty_rect = pg.Rect((self.empty_index[0] * self.cell_size[0],
                                              self.empty_index[1] * self.cell_size[1]),
                                              self.cell_size)
        self.make_pieces()
        self.shuffle_pieces(len(self.grid))
        
    def update(self, dt):
        self.animations.update(dt)
        if not self.moves:
            self.done = True
            self.pieces.append(self.missing_piece)
        elif not self.animations:
            piece, direction = self.moves.pop()
            x, y = piece.rect.topleft
            dx, dy = direction
            px, py = x + (dx * self.cell_size[0]), y + (dy * self.cell_size[1])
            ani = Animation(x=px, y=py, duration=250, round_values=True)
            ani.start(piece.rect)
            self.animations.add(ani)
            
    def make_pieces(self):
        w, h = self.cell_size
        self.pieces = []
        self.rows = []
        self.grid = {}
        for y in range(self.num_rows):
            row = []
            for x in range(self.num_columns):
                px, py = x * w, y * h
                img = self.image.subsurface((px, py), (w, h))
                piece = Piece((x, y), (px, py), img)
                if self.empty_index == (x, y):                    
                    self.missing_piece = piece
                    self.grid[(x, y)] = GridCell((x, y), (px, py), self.cell_size, None)
                else:
                    self.grid[(x, y)] = GridCell((x, y), (px, py), self.cell_size, piece)
                    self.pieces.append(piece)
                    
    def shuffle_pieces(self, num_moves):
        moved_report = []
        moves_report = []
        moved = []
        moves = []
        for _ in range(num_moves):
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            shuffle(offsets)
            neighbors = []
            for off in offsets:
                new_index = self.empty_index[0] + off[0], self.empty_index[1] + off[1]
                try:
                    piece = self.grid[new_index].occupant
                    if piece is not None:
                        neighbors.append((piece, off))
                except KeyError:
                    pass
            to_move = sorted(neighbors, key=lambda x: moved.count(x[0]))
            mover, offset = to_move[0]
            former = mover.index
            mover.index = self.empty_index
            self.empty_index = former
            mover.rect = self.empty_rect
            self.empty_rect = pg.Rect((self.empty_index[0] * self.cell_size[0],
                                                  self.empty_index[1] * self.cell_size[1]),
                                                  self.cell_size)
            self.grid[former].occupant = None
            self.grid[mover.index].occupant = mover
            moved.append(mover)
            moves.append((mover, (offset[0], offset[1])))
        self.moves = moves  
       
    def draw(self, surface):
        for p in self.pieces:
            surface.blit(p.image, p.rect.move(self.topleft))


class PuzzleIcon(object):
    def __init__(self, topleft, image):
        self.image = image
        self.icon_image = pg.transform.smoothscale(image, (80, 60))
        self.rect = self.icon_image.get_rect(topleft=topleft)
        
    def draw(self, surface):
        surface.blit(self.icon_image, self.rect)

        
class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        sr = prepare.SCREEN_RECT
        self.title = SlideTitle((sr.centerx - 120, sr.top), prepare.GFX["title-puzzle"], (24, 24))
        self.title2 = SlideTitle((sr.centerx - 120, 400), prepare.GFX["title-difficulty"], (24, 24))
        self.buttons = ButtonGroup()
        start_button = Button((sr.centerx - 64, sr.h - 50), self.buttons, text="Start", call=self.start)
        start_button.selected = False
        difficulties = [(12, (4, 3)), (16, (4, 3)), (24, (4, 3)), (48, (8, 6))]
        names = ("Easy", "Medium", "Hard", "Yikes")
        left = 100
        for difficulty, name in zip(difficulties, names):
            button = Button((left, 500), self.buttons, text=name, call=self.set_difficulty)
            button.args=(difficulty, button)
            button.selected = True if name == "Easy" else False
            left += 150
        self.make_icons()
        
        self.selected = self.icons[0]
        self.num_moves = 12
        self.grid_size = 4, 3
        
    def set_difficulty(self, args):
        difficulty, button = args
        print "diff: {}".format(difficulty)
        self.num_moves, self.grid_size = difficulty
        for b in self.buttons:
            b.selected = False
        button.selected = True        
    
    def start(self, *args):
        self.done = True
        self.next = "PUZZLING"
        self.persist["image"] = self.image
        self.persist["num moves"] = self.num_moves
        self.persist["grid size"] = self.grid_size
        
    def make_icons(self):
        sr = prepare.SCREEN_RECT
        self.icons = []
        left = 50
        top = 50
        for i, name in enumerate(prepare.PUZZLES): 
            img = prepare.PUZZLES[name]
            icon = PuzzleIcon((left, top), img)
            self.icons.append(icon)
            left += 100
            if left > sr.w - 100:
                left = 50
                top += 80

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_SPACE:
                self.start()            
        elif event.type == pg.MOUSEBUTTONUP:
            for icon in self.icons:
                if icon.rect.collidepoint(event.pos):
                    self.image = icon.image
                    self.selected = icon
        self.buttons.get_event(event)
        
    def update(self, dt):
        self.buttons.update(pg.mouse.get_pos())
        self.title.update(dt)
        self.title2.update(dt)

    def draw(self, surface):
        surface.fill(pg.Color("dodgerblue"))
        self.title.draw(surface)
        self.title2.draw(surface)
        for icon in self.icons:
            icon.draw(surface)
        self.buttons.draw(surface)
        pg.draw.rect(surface, pg.Color("white"), self.selected.rect, 2)
        for b in self.buttons:
            if b.selected:
                pg.draw.rect(surface, pg.Color("white"), b.rect, 2)