
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

    @classmethod
    def delete_op(self, gr, c):
        # El gr ya viene flatten()
        for cell_grid in gr:
            if c.value in cell_grid.possible:
                cell_grid.possible.remove(c.value)
