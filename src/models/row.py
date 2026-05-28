import numpy as np

class Row():
    def __init__(self, cells, position):

        self.digits = list(range(1, 10))
        self.cells = cells
        self.pos = position
        self.possible = list(range(1, 10))

    def __repr__(self):
        return str(self.cells)

    def delete_possible_in(self, value):
        if value in self.possible:
            self.possible.remove(value)

    def delete_option(self, value, pos=-1):

        if isinstance(pos, int) and pos != -1:
            mask = np.ones(9, dtype=bool)
            mask[(pos//3)*3:(pos//3)*3+3] = False
            row_without_grid = np.array(self.cells)[mask]
            for cell_in_row in row_without_grid:
                if value in cell_in_row.possible:
                    cell_in_row.possible.remove(value)

        # Seccion para X-Wings
        elif isinstance(pos, (list, np.ndarray, tuple)):
            for i in range(9):
                if i in pos:
                    continue
                if value in self.cells[i].possible:
                    self.cells[i].possible.remove(value)
        else:
            for cell_in_row in self.cells:
                if value in cell_in_row.possible:
                    cell_in_row.possible.remove(value)
