from random import shuffle

import pygame as pg

from ..components.animation import Animation


class Piece(object):
    def __init__(self, index, topleft, image):
        self.home_index = index
        self.index = index
        self.image = image
        self.rect = self.image.get_rect(topleft=topleft)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
    
class GridCell(object):
    def __init__(self, index, topleft, size, occupant):
        self.index = index
        self.rect = pg.Rect(topleft, size)
        self.occupant = occupant
 
       
class Puzzle(object):
    def __init__(self, size, grid_size, image, num_moves):
        self.size = size
        self.width, self.height = size
        self.num_columns, self.num_rows = grid_size 
        self.cell_size = self.width // self.num_columns, self.height // self.num_rows
        self.image = image
        self.complete = False
        self.grabbed = None
        
        self.empty_index = self.num_columns - 1, 0
        self.empty_rect = pg.Rect((self.empty_index[0] * self.cell_size[0], 0),
                                              self.cell_size)
        self.make_pieces()
        self.shuffle_pieces(num_moves)
        self.animations = pg.sprite.Group()
        
    def make_pieces(self):
        w, h = self.cell_size
        self.pieces = []
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
                    
    def make_rows(self):
        rows = []
        for y in range(self.num_rows):
            row = []
            for x in range(self.num_columns):
                row.append(self.grid[(x, y)].occupant)
            rows.append(row)
        return rows

    def make_columns(self):
        columns = [] 
        for x in range(self.num_columns):
            column = []
            for y in range(self.num_rows):
                column.append(self.grid[(x, y)].occupant)
            columns.append(column)
        return columns
        
    def shift_row(self, row, grabbed, direction):
        indx = row.index(grabbed)
        empty = row.index(None)
        print "row: {}".format(row)
        print "indx: {}".format(indx)
        print "empty: {}".format(empty)
        if direction == -1:
            movers = row[empty + 1:indx + 1]
        else:
            movers = row[indx:empty]        
        self.empty_rect = self.grabbed.rect.copy()
        self.empty_index = self.grabbed.index
        self.grid[self.empty_index].occupant = None
        for m in movers:
            x, y = m.rect.topleft
            mx = x + (self.cell_size[0] * direction)
            ani = Animation(x=mx, duration=250, round_values=True)
            ani.start(m.rect)
            self.animations.add(ani)
            m.index = m.index[0] + direction, m.index[1]
            self.grid[m.index].occupant = m
            
    def shift_column(self, column, grabbed, direction):
        indx = column.index(grabbed)
        if direction == -1:
            movers = column[self.empty_index[1] + 1:indx+1]
        else:
            movers = column[indx:self.empty_index[1]]
        self.empty_rect = self.grabbed.rect.copy()
        self.empty_index = self.grabbed.index
        self.grid[self.empty_index].occupant = None
        for m in movers:
            x, y = m.rect.topleft
            my = y + (self.cell_size[0] * direction)
            ani = Animation(y=my, duration=250, round_values=True)
            ani.start(m.rect)
            self.animations.add(ani)
            m.index = m.index[0], m.index[1] + direction
            self.grid[m.index].occupant = m
            
    def shuffle_pieces(self, num_moves):
        moved = []
        for _ in range(num_moves):
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            shuffle(offsets)
            neighbors = []
            for off in offsets:
                new_index = self.empty_index[0] + off[0], self.empty_index[1] + off[1]
                try:
                    piece = self.grid[new_index].occupant
                    neighbors.append(piece)
                except KeyError:
                    pass
            to_move = sorted(neighbors, key=lambda x: moved.count(x))[0]    
            former = to_move.index
            to_move.index = self.empty_index
            self.empty_index = former
            to_move.rect = self.empty_rect
            self.empty_rect = pg.Rect((self.empty_index[0] * self.cell_size[0],
                                                  self.empty_index[1] * self.cell_size[1]),
                                                  self.cell_size)
            self.grid[former].occupant = None
            self.grid[to_move.index].occupant = to_move            
            moved.append(to_move)
            
    def unit_diff(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        try:
            ux = dx / abs(dx)
        except ZeroDivisionError:
            ux = 0
        try:
            uy = dy / abs(dy)
        except ZeroDivisionError:
            uy = 0
        return ux, uy
        
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:    
            if not self.grabbed:
                for piece in self.pieces:
                    if piece.rect.collidepoint(event.pos):
                        print "grabbed"
                        self.grabbed = piece
                        self.grab_pos = event.pos
                        print self.grab_pos
                        break

        elif event.type == pg.MOUSEBUTTONUP:
            if self.grabbed is not None:
                print "mouse up"
                rows = self.make_rows()
                columns = self.make_columns()    
                in_row = self.empty_index[1] == self.grabbed.index[1]
                in_column = self.empty_index[0] == self.grabbed.index[0]
                unit_diff = self.unit_diff(self.grab_pos, event.pos)
                empty_diff = self.unit_diff(self.grabbed.rect.topleft, self.empty_rect.topleft)
                print "unit {}".format(unit_diff)
                print "empty {}".format(empty_diff)
                if in_row:
                    print rows[self.grabbed.index[1]]
                    if unit_diff[0] == empty_diff[0]:
                        self.shift_row(rows[self.grabbed.index[1]], self.grabbed, unit_diff[0])
                elif in_column:
                    print columns[self.grabbed.index[0]]
                    if unit_diff[1] == empty_diff[1]:
                        self.shift_column(columns[self.grabbed.index[0]], self.grabbed, unit_diff[1])
                        columns[self.grabbed.index[0]]
            self.grabbed = None
            self.grab_pos = None
            
    def update(self, dt):
        self.animations.update(dt)
        mouse_pos = pg.mouse.get_pos()
        if not self.complete and all((x.index == x.home_index for x in self.pieces)):
            self.complete = True
            self.pieces.append(self.missing_piece)

    def draw(self, surface):
        for piece in self.pieces:
            piece.draw(surface)
        #pg.draw.rect(surface, pg.Color("red"), self.empty_rect, 2)
