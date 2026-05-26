class Cell():
    # identifier of the cell, used to know the position on the board
    ID = 1

    def __init__(self, value, row, col):
        self.ID = Cell.ID
        self.value = int(value)
        self.pos = [row, col]
        self.possible = [] if value != 0 else [1,2,3,4,5,6,7,8,9]
        Cell.ID += 1

    def __repr__(self):
        return str(self.value)


    def delete_possible(self, value):
        self.possible.remove(value)
        if len(self.possible) == 1:
            self.setValue(self.possible[0])
    

    @classmethod
    def get_value(self, cell):
        return cell.value

    def set_value(self, value):
        self.value = value
        self.possible = []

    @classmethod
    def get_id(self, cell):
        return cell.ID

    @classmethod
    def get_possible(self, cell):
        return list(sorted(cell.possible))
