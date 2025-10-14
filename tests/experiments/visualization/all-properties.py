
"""
Solid: Represented by '-' or 'solid'. This is the default line style.
Dashed: Represented by '--' or 'dashed'.
Dash-dot: Represented by '-.' or 'dashdot'.
Dotted: Represented by ':' or 'dotted'.
np.nan
"""

import matplotlib.pyplot as plt
import numpy as np

# X values
x = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# First dataset:
no_strings = [
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...
]

# Second dataset:
strings = [
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...,
    ...
]

plt.plot(x, no_strings, label='Without strings', marker='x', linestyle='-')
plt.plot(x, strings, label='With strings', marker='x', linestyle='--')

plt.xlabel('Number of commands in a test')
plt.ylabel('Seconds per generated test (avg.)')
plt.title('Performance of fuzz for all properties')
plt.legend()
plt.grid(True)
plt.show()


if __name__ == '__main__':
    pass