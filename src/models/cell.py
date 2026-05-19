class Cell():
    # identifier of the cell, used to know the position on the board
    ID = 1

    def __init__(self, value, row, col):
        self.ID = Cell.ID
        self.value = value
        self.pos = [row, col]
        self.possible = []
        if Cell.ID == 81:
            Cell.ID = 0
        Cell.ID += 1

    def __repr__(self):
        return str(self.value)


    def delete_possible(self, value):
        self.possible.remove(value)
        if len(self.possible) == 1:
            self.setValue(self.possible[0])

    @classmethod
    def getValue(self, cell):
        return cell.value

    def setValue(self, value):
        self.value = value
        self.possible = []

    @classmethod
    def getID(self, cell):
        return cell.ID

    @classmethod
    def getPossible(self, cell):
        return list(sorted(cell.possible))
