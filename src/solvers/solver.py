import numpy as np
import os, sys
import copy
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models import cell
from models.board import Board
from models.cell import Cell

class Solver:

    
    def __init__(self, board):
        self.board = board
        self.show = board.show


    def backtracking(self):
        groups = [self.board.rows, self.board.columns, self.board.grids]
        for group in groups:
            for n_group in group:
                options = set()
                for cell in n_group.cells:
                    if cell.value == 0:
                        continue
                    options.update([int(cell.value)])
                for cell in n_group.cells:
                    if cell.value != 0:
                        continue
                    cell.possible = list(set(cell.possible).difference(options))
        return self.board
    
    def delete_option(self, cell, value):
        row_id, col_id = divmod(cell.ID -1, 9)
        col = self.board.columns[col_id]
        col.delete_option(value)

        row = self.board.rows[row_id]
        row.delete_option(value)
        
        grid = self.board.grids[row_id//3*3 + col_id//3]
        grid.delete_option(value)
    
    def naked_single(self):
        for cell in self.board.cells:
            if cell.value != 0:
                continue
            if len(cell.possible) == 1:
                cell.set_value(cell.possible[0])
                self.delete_option(cell, cell.value)
        return self.board

    def hidden_single(self):

        for cell in self.board.cells:
            if cell.value != 0:
                continue
            row_id, col_id = divmod(cell.ID -1, 9)
            row = self.board.rows[row_id]
            col = self.board.columns[col_id]
            grid = self.board.grids[row_id//3*3 + col_id//3]
            
            groups = [row, col, grid]
            cell_possible = set(cell.possible)
            for group in groups:
                options  = set()
                for c in group.cells:
                    if c.ID == cell.ID:
                        continue
                    options.update(set(c.possible))
                rest_possible = list(cell_possible.difference(options))
                if len(rest_possible) == 1:
                    cell.set_value(rest_possible[0])
                    self.delete_option(cell, cell.value)
        return self.board
    
    def locked_candidate(self):

        for grid in self.board.grids:
            possible_in_grid = set().union(*[cell.possible for cell in grid.cells])
            for possible in possible_in_grid:
                cells_with_possible = [cell for cell in grid.cells if possible in cell.possible]
                rows = set([int(cell.pos[0]) for cell in cells_with_possible])
                cols = set([int(cell.pos[1]) for cell in cells_with_possible])
                if len(rows) == 1:
                    row_id = rows.pop()
                    row = self.board.rows[row_id]
                    row.delete_option(possible, pos=list(cols)[0])
                elif len(cols) == 1:
                    col_id = cols.pop()
                    col = self.board.columns[col_id]
                    col.delete_option(possible, pos=list(rows)[0])
        return self.board
    
    def twins(self):

        def get_group_position(axis, ids):
            rows, cols = np.array([divmod(i, 9) for i in ids]).T
            if axis == 0:  
                return cols
            elif axis == 1:
                return rows
            elif axis == 2:
                return (rows%3)*3 + (cols%3)
            else:
                raise ValueError("Axis must be 0 (rows), 1 (columns), or 2 (grids).")
            
        groups = [[0, self.board.rows], [1, self.board.columns], [2, self.board.grids]]
        for axis, group in groups:
            for n_group in group:
                possible_in_group = [sorted(cell.possible) for cell in n_group.cells]
                for possible in possible_in_group:
                    if possible_in_group.count(possible) == 2 and len(possible) == 2:
                        ids_with_possible = [cell.ID for cell in n_group.cells if sorted(cell.possible) == possible]
                        group_position = get_group_position(axis, ids_with_possible)
                        n_group.delete_option(possible, pos=group_position)
                    possible_in_group.remove(possible)
        return self.board
    
    def triplets(self):
        # Similar a los twins pero buscando 3 celdas con las mismas 3 posibilidades
        pass

    def solve(self):
        while True:
            before = copy.deepcopy(self.board)
            self.backtracking()
            self.naked_single()
            self.hidden_single()
            self.locked_candidate()
            solver.twins()
            after = self.board
            if before == after:
                print("No more progress can be made with current techniques.")
                break
        return self.board

if __name__ == "__main__":

    test_sudoku=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 2],
                         [4, 8, 3, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 6, 0],
                         [0, 1, 0, 0, 4, 0, 5, 0, 0],
                         [6, 0, 0, 0, 2, 0, 0, 0, 0],
                         [0, 9, 0, 0, 6, 0, 0, 7, 1],
                         [0, 0, 5, 0, 9, 6, 0, 8, 0],
                         [0, 0, 4, 3, 0, 5, 0, 0, 0],
                         [9, 0, 0, 0, 0, 0, 2, 0, 5]])
    
    sudoku_hard = np.array([[4, 0, 0, 0, 0, 0, 0, 9, 0],
                            [0, 0, 0, 0, 0, 3, 0, 0, 0],
                            [0, 9, 0, 2, 0, 7, 0, 0, 1],
                            [0, 0, 0, 0, 6, 0, 0, 0, 0],
                            [0, 0, 8, 0, 0, 0, 5, 0, 0],
                            [0, 4, 0, 1, 0, 9, 0, 0, 7],
                            [0, 0, 0, 0, 4, 0, 0, 0, 6],
                            [5, 0, 0, 6, 0, 2, 7, 0, 0],
                            [0, 2, 0, 0, 3, 0, 0, 0, 0]])
    
    solver = Solver(Board(sudoku_hard))
    solver.solve()
    solver.show()

