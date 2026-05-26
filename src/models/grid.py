
class Grid():

    def __init__(self, cells, position):

        self.cells = cells
        self.pos = position

    def __repr__(self):
        return str(self.cells)

    @classmethod
    def getGrid(self, grids, c):
        row = c.pos[0]
        col = c.pos[1]
        id_grid = 3*((row-1)//3)+(col-1)//3+1
        grid = grids[id_grid-1]
        return grid.cells.flatten()
    # Funcion usada para eliminar posibles valores  de todo el grid dada
    # una celda y la lista de grids

    def delete_option(self, value, pos=-1):

        if isinstance(pos, list):
            for i in range(9):
                if i in pos:
                    continue
                cell = self.cells[i]
                if value in cell.possible:
                    cell.possible.remove(value)
        else:
            for cell_grid in self.cells:
                if value in cell_grid.possible:
                    cell_grid.possible.remove(value)
        

