import numpy as np
import matplotlib.pyplot as plt
import textwrap
import os, sys
from .cell import Cell
from .row import Row
from .column import Column
from .grid import Grid

class Board():

    def __init__(self, board):
        if board.shape != (9, 9):
            raise ValueError("Wrong Sudoku Shape")
        digits = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        rows_index, cols_index = np.array([divmod(i, 9) for i in range(81)]).T
        self.cells = np.array(list(map(Cell, board.flatten(),
                                       rows_index, cols_index)))
        self.array = np.array(np.split(self.cells, 9))
        self.rows = []
        self.columns = []
        self.grids = []

        for i in digits-1:
            row_slice = slice((i//3)*3, (i//3)*3+3)
            col_slice = slice((i%3)*3, (i%3)*3+3)
            self.grids.append(Grid(self.array[row_slice, col_slice].flatten(), i))
            self.rows.append(Row(self.array[i, :], i))
            self.columns.append(Column(self.array[:, i], i))

    def __repr__(self):
        return str(self.array)

    def __eq__(self, other):
        values_1 = list(map(Cell.get_value, self.cells))
        possibles_1 = list(map(Cell.get_possible, self.cells))
        values_2 = list(map(Cell.get_value, other.cells))
        possibles_2 = list(map(Cell.get_possible, other.cells))
        return values_1 == values_2 and possibles_1 == possibles_2

    def show(self):
        N = 9
        fig, ax = plt.subplots(figsize=(9, 9))
        ax.set_xlim(0, N)
        ax.set_ylim(0, N)
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw grid lines
        for i in range(N + 1):
            lw = 2.5 if i % 3 == 0 else 0.8
            ax.axhline(y=i, color='black', lw=lw)
            ax.axvline(x=i, color='black', lw=lw)

        text_1 = list(map(lambda x: str(x.possible)[1:-1], self.cells))
        text_2 = list(map(lambda x: str(x.value), self.cells))

        all_possible = " ".join(str(j) for j in range(1, 10))

        for i in range(81):
            row, col = divmod(i, 9)
            cx = col + 0.5
            cy = N - row - 0.5  # invert so row 0 is at the top

            value = text_2[i]
            possible = text_1[i].replace(",", "")

            if possible == all_possible:
                possible = "[all]"

            # Only show possible values if cell is unsolved (value is 0 or empty)
            if value in ("0", "None", ""):
                possible = textwrap.fill(possible, width=6)
                ax.text(
                    cx, cy - 0.1, possible,
                    ha='center', va='center',
                    fontsize=12, color='darkgray',
                    fontfamily='monospace', wrap=True,
                )
            else:
                ax.text(
                    cx, cy, value,
                    ha='center', va='center',
                    fontsize=20, fontweight='bold', color='black'
                )

        plt.tight_layout()
        plt.show()

    
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
    
    def test_plot():
        board = Board(test_sudoku)
        board.show()
    
    test_plot()
    
