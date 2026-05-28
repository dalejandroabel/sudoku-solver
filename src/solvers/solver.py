import numpy as np
import os, sys
import copy
from itertools import permutations
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models import cell
from models.board import Board
from models.cell import Cell

class Solver:

    digits = list(range(1, 10))

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
        row_id, col_id = divmod(cell.ID, 9)
        col = self.board.columns[col_id]
        row = self.board.rows[row_id]
        grid = self.board.grids[row_id//3*3 + col_id//3]
        for group in [col, row, grid]:
            group.delete_option(value)
            for cell_in_group in group.cells:
                if len(cell_in_group.possible) == 1:
                    self.set_cell_value(cell_in_group, cell_in_group.possible[0])


    def set_cell_value(self, cell, value):
        cell.set_value(value)
        self.delete_option(cell, value)
        row_id, col_id = divmod(cell.ID, 9)
        grid_id = row_id//3*3 + col_id//3

        self.board.rows[row_id].delete_possible_in(value)
        self.board.columns[col_id].delete_possible_in(value)
        self.board.grids[grid_id].delete_possible_in(value)

    def get_group_position(self, axis, ids):
        rows, cols = np.array([divmod(i, 9) for i in ids]).T
        if axis == 0:  
            return cols
        elif axis == 1:
            return rows
        elif axis == 2:
            return (rows%3)*3 + (cols%3)
        else:
            raise ValueError("Axis must be 0 (rows), 1 (columns), or 2 (grids).")   
        
    def naked_single(self):
        for cell in self.board.cells:
            if cell.value != 0:
                continue
            if len(cell.possible) == 1:
                row_id, col_id = divmod(cell.ID, 9)
                self.set_cell_value(cell, cell.possible[0])
        return self.board

    def hidden_single(self):

        for cell in self.board.cells:
            if cell.value != 0:
                continue
            row_id, col_id = divmod(cell.ID, 9)
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
                    row_id, col_id = divmod(cell.ID, 9)
                    self.set_cell_value(cell, rest_possible[0])
                    break
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
    
    def naked_twins(self):
            
        groups = [[0, self.board.rows], [1, self.board.columns], [2, self.board.grids]]
        for axis, group in groups:
            for n_group in group:
                possible_in_group = [sorted(cell.possible) for cell in n_group.cells]
                for possible in possible_in_group:
                    if possible_in_group.count(possible) == 2 and len(possible) == 2:
                        ids_with_possible = [cell.ID for cell in n_group.cells if sorted(cell.possible) == possible]
                        group_position = self.get_group_position(axis, ids_with_possible)
                        for value in possible:  
                            n_group.delete_option(value, pos=group_position)
                    possible_in_group.remove(possible)
        return self.board

    def hidden_twins(self):
        groups = [[0,self.board.rows], [1, self.board.columns], [2, self.board.grids]]
        for axis, group in groups:
            for n_group in group:
                available_cells = [cell for cell in n_group.cells if cell.value == 0]
                available_digits = set().union(*[cell.possible for cell in available_cells])
                possibles_count = {}
                for i in available_digits:
                    cells_ids = sorted([cell.ID for cell in available_cells if i in cell.possible])
                    if cells_ids in possibles_count.values() and len(cells_ids) == 2:
                        digit_to_delete = [key for key, value in possibles_count.items() if value == cells_ids][0]
                        self.board.cells[cells_ids[0]].possible = [digit_to_delete,i]
                        self.board.cells[cells_ids[1]].possible = [digit_to_delete,i]
                    possibles_count[i] = cells_ids
        return self.board

    def naked_triplets(self):
        groups = [[0,self.board.rows], [1, self.board.columns]]
        for axis, group in groups:
            for n_group in group:
                available_cells = [cell for cell in n_group.cells if (cell.value == 0) and len(cell.possible) in [2, 3]]
                if len(available_cells) < 3:
                    continue
                triplets_ids = permutations([i for i in range(len(available_cells))], 3)
                options_in_triplet = set()
                for triplet in triplets_ids:
                    options_in_triplet.update(set().union(*[set(available_cells[i].possible) for i in triplet]))
                if len(options_in_triplet) == 3:
                    group_positions = self.get_group_position(axis, sorted([available_cells[i].ID for i in triplet]))
                    for option in options_in_triplet:
                        n_group.delete_option(option, pos=group_positions)
        return self.board


    def hidden_triplets(self):
        groups = [[0,self.board.rows], [1, self.board.columns], [2, self.board.grids]]
        for axis, group in groups:
            for n_group in group:
                available_cells = [cell for cell in n_group.cells if cell.value == 0]
                available_digits = set().union(*[cell.possible for cell in available_cells])
                possibles_count = {}
                for i in available_digits:
                    cells_ids = sorted([cell.ID for cell in available_cells if i in cell.possible])
                    if cells_ids in possibles_count.values() and len(cells_ids) in [2, 3]:

                        digit_to_delete = [key for key, value in possibles_count.items() if value == cells_ids][0]
                        self.board.cells[cells_ids[0]].possible = [digit_to_delete,i]
                        self.board.cells[cells_ids[1]].possible = [digit_to_delete,i]
                    possibles_count[i] = cells_ids
        return self.board
    
    def hidden_strategy(self, N):
        groups = [[0,self.board.rows], [1, self.board.columns], [2, self.board.grids]]
        for axis, group in groups:
            for n_group in group:
                available_cells = [cell for cell in n_group.cells if cell.value == 0]
                available_digits = set().union(*[cell.possible for cell in available_cells])
                possibles_count = {}
                for i in available_digits:
                    cells_ids = sorted([cell.ID for cell in available_cells if i in cell.possible])
                    possibles_count[i] = cells_ids
                digits_combinations = permutations(available_digits, N)
                for combination in digits_combinations:
                    cells_ids = set().union(*[possibles_count[digit] for digit in combination])
                    if len(cells_ids) == N:
                        digits_to_delete = available_digits.difference(set(combination))
                        cells_position = list(set(range(0, 9)).difference(set(self.get_group_position(axis, cells_ids))))
                        for digit in digits_to_delete:
                            n_group.delete_option(digit, pos=cells_position)
                        break
        return self.board
    
    
    def solve(self):
        it = 0
        while True:
            before = copy.deepcopy(self.board)
            self.backtracking()
            self.naked_single()
            self.hidden_single()
            self.locked_candidate()
            self.naked_twins()
            self.naked_triplets()
            self.hidden_strategy(2)
            self.hidden_strategy(3)
            self.hidden_strategy(4)
            after = self.board
            it += 1
            print(f"Iteration {it} completed.")
            if before == after:
                print("No more progress can be made with current techniques.")
                break
        return self.board


# Techniques tests

    @staticmethod
    def test_naked_twins():
        board_naked_twins = np.array(
            [[4, 0, 0, 2, 7, 0, 6, 0, 0],
             [7, 9, 8, 1, 5, 6, 2, 3, 4],
             [0, 2, 0, 8, 4, 0, 0, 0, 7],
             [2, 3, 7, 4, 6, 8, 9, 5, 1],
             [8, 4, 9, 5, 3, 1, 7, 2, 6],
             [5, 6, 1, 7, 9, 2, 8, 4, 3],
             [0, 8, 2, 0, 1, 5, 4, 7, 9],
             [0, 7, 0, 0, 2, 4, 3, 0, 0],
             [0, 0, 4, 0, 8, 7, 0, 0, 2]])
        solver = Solver(Board(board_naked_twins))
        solver.backtracking() 
        solver.show()
        solver.naked_twins()
        solver.show()
    
    @staticmethod
    def test_hidden_twins():
        board_hidden_twins = np.array(
            [[0, 0, 9, 0, 3, 2, 0, 0, 0],
             [0, 0, 0, 7, 0, 0, 0, 0, 0],
             [1, 6, 2, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 2, 0, 5, 6, 0],
             [0, 0, 0, 9, 0, 0, 0, 0, 0],
             [0, 5, 0, 0, 0, 0, 1, 0, 7],
             [0, 0, 0, 0, 0, 0, 4, 0, 3],
             [0, 2, 6, 0, 0, 9, 0, 0, 0],
             [0, 0, 5, 8, 7, 0, 0, 0, 0]])
        solver = Solver(Board(board_hidden_twins))
        solver.backtracking()
        solver.show()
        solver.hidden_twins()
        solver.show()
    
    @staticmethod
    def test_naked_triplets():
        board_naked_single = np.array(
            [[9, 0, 8, 0, 0, 5, 4, 2, 3],
            [0, 0, 0, 0, 0, 4, 9, 5, 0],
            [0, 4, 0, 0, 0, 9, 0, 6, 0],
            [0, 5, 0, 9, 3, 2, 8, 1, 6],
            [8, 1, 0, 5, 4, 0, 3, 0, 2],
            [0, 0, 2, 0, 8, 0, 5, 0, 4],
            [0, 0, 3, 0, 0, 8, 0, 4, 5],
            [0, 0, 0, 0, 5, 3, 2, 8, 9],
            [0, 8, 0, 4, 0, 0, 0, 3, 0]])
        solver = Solver(Board(board_naked_single))
        solver.backtracking()
        solver.show()
        solver.naked_triplets()
        solver.show()

    @staticmethod
    def test_hidden_triplets():
        board_hidden_triplets = np.array(
            [[5, 2, 8, 6, 0, 0, 0, 4, 9],
             [1, 3, 6, 4, 9, 0, 0, 2, 5],
             [7, 9, 4, 2, 0, 5, 6, 3, 0],
             [0, 0, 0, 1, 0, 0, 2, 0, 0],
             [0, 0, 7, 8, 2, 6, 3, 0, 0],
             [0, 0, 2, 5, 0, 9, 0, 6, 0],
             [2, 4, 0, 3, 0, 0, 9, 7, 6],
             [8, 0, 9, 7, 0, 2, 4, 1, 3],
             [0, 7, 0, 9, 0, 4, 5, 8, 2]])
        solver = Solver(Board(board_hidden_triplets))
        solver.backtracking()
        solver.show()
        solver.hidden_triplets()
        solver.show()

    @staticmethod
    def test_hidden_strategy_twins():

        board_hidden_N2 = np.array(
            [[0, 0, 9, 0, 3, 2, 0, 0, 0],
             [0, 0, 0, 7, 0, 0, 0, 0, 0],
             [1, 6, 2, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 2, 0, 5, 6, 0],
             [0, 0, 0, 9, 0, 0, 0, 0, 0],
             [0, 5, 0, 0, 0, 0, 1, 0, 7],
             [0, 0, 0, 0, 0, 0, 4, 0, 3],
             [0, 2, 6, 0, 0, 9, 0, 0, 0],
             [0, 0, 5, 8, 7, 0, 0, 0, 0]])
        solver = Solver(Board(board_hidden_N2))
        solver.backtracking()
        solver.show()
        solver.hidden_strategy(3)
        solver.show()

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
    
    test_sudoku_1 = np.array([[4, 0, 0, 0, 0, 0, 0, 9, 0],
                            [0, 0, 0, 0, 0, 3, 0, 0, 0],
                            [0, 9, 0, 2, 0, 7, 0, 0, 1],
                            [0, 0, 0, 0, 6, 0, 0, 0, 0],
                            [0, 0, 8, 0, 0, 0, 5, 0, 0],
                            [0, 4, 0, 1, 0, 9, 0, 0, 7],
                            [0, 0, 0, 0, 4, 0, 0, 0, 6],
                            [5, 0, 0, 6, 0, 2, 7, 0, 0],
                            [0, 2, 0, 0, 3, 0, 0, 0, 0]])
    


    test_sudoku_2 = np.array([[7, 0, 0, 0, 0, 9, 0, 0, 0],
                            [0, 0, 0, 0, 0, 5, 0, 0, 8],
                            [0, 0, 1, 7, 8, 0, 3, 0, 0],
                            [1, 0, 0, 4, 6, 0, 0, 0, 9],
                            [0, 0, 3, 0, 0, 0, 0, 2, 0],
                            [0, 0, 0, 0, 0, 7, 0, 0, 0],
                            [4, 0, 0, 8, 1, 0, 0, 0, 6],
                            [0, 0, 0, 0, 5, 0, 0, 0, 0],
                            [0, 6, 0, 0, 0, 0, 9, 0, 0]])

    test_sudoku_3 = np.array([[0, 0, 6, 0, 8, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 3],
                            [1, 0, 0, 0, 0, 7, 2, 4, 0],
                            [4, 0, 0, 0, 0, 2, 1, 5, 0],
                            [0, 0, 0, 0, 0, 0, 9, 0, 0],
                            [0, 2, 0, 7, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 5, 0, 0, 9],
                            [0, 0, 1, 6, 0, 0, 5, 3, 0],
                            [3, 0, 0, 0, 0, 0, 0, 0, 7]])

    # Solver.test_naked_twins()
    # Solver.test_hidden_twins()
    # Solver.test_naked_triplets()
    # Solver.test_hidden_strategy_twins()
    solver = Solver(Board(test_sudoku_2))
    solver.solve()
    solver.show()

