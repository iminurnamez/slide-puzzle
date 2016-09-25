import pygame as pg

from .. import tools, prepare
from ..components.puzzle import Puzzle


class Puzzling(tools._State):
    def __init__(self):
        super(Puzzling, self).__init__()
        self.background_color = (187, 187, 187)
        
    def startup(self, persistent):
        self.persist = persistent
        print self.persist
        img = self.persist["image"]
        num_moves = self.persist["num moves"]
        grid_size = self.persist["grid size"]
        self.puzzle = Puzzle((800, 600), grid_size, img, num_moves)
        
    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.puzzle.get_event(event)
        
    def update(self, dt):
        self.puzzle.update(dt)

    def draw(self, surface):
        surface.fill(self.background_color)
        self.puzzle.draw(surface)
        