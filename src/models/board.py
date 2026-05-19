import numpy as np
from .cell import Cell
from .row import Row
from .column import Column
from .grid import Grid

class Board():

    def __init__(self, board):
        if board.shape != (9, 9):
            raise ValueError("Wrong Sudoku Shape")
        digits = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        cols_index, rows_index = np.meshgrid(digits, digits)

        self.cells = np.array(list(map(Cell, board.flatten(),
                                       rows_index, cols_index)))
        self.array = np.array(np.split(self.cell_list, 9))

        self.rows = []
        self.columns = []
        self.grids = []

        for i in digits-1:
            row_slice = slice((i//3)*3, (i//3)*3+3)
            col_slice = slice((i%3)*3, (i%3)*3+3)
            self.grids.append(Grid(self.array[row_slice, col_slice], i))
            self.rows.append(Row(self.array[i, :], i))
            self.columns.append(Column(self.array[:, i], i))

    def __repr__(self):
        return str(self.array)

    def __eq__(self, other):
        values_1 = list(map(Cell.getValue, self.array.flatten()))
        possibles_1 = list(map(Cell.getPossible, self.array.flatten()))
        values_2 = list(map(Cell.getValue, other.array.flatten()))
        possibles_2 = list(map(Cell.getPossible, other.array.flatten()))
        return values_1 == values_2 and possibles_1 == possibles_2
