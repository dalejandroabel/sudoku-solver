import matplotlib.pyplot as plt
import numpy as np

a = np.arange(81)
for i in a:
    row, col = divmod(i, 9)
    grid = 3*((row)//3)+(col//3)
    grid_position = (row%3)*3 + (col%3)
    print(f"ID: {i}, Row: {row}, Col: {col}, Grid: {grid}, Grid Position: {grid_position}")










