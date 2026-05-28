import matplotlib.pyplot as plt
from itertools import permutations

import numpy as np

def get_group(id):
    return divmod(id, 9)
print([get_group(i) for i in [23,26]])


a = range(0, 9)
b = [0, 1, 2]
print(set(a).difference(b))





