import numpy as np

pos = 1
start = (pos // 3) * 3
# example cells; replace with the actual cells sequence as needed
cells = np.arange(9)
mask = np.ones(9, dtype=bool)
mask[start:start + 3] = False
row_less_grid = cells[mask]