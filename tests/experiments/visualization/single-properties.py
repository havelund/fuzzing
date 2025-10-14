
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

# First dataset
y1 = [10, 20, 30, 40, 45, 50, 60, 65, 70, 75]

# Second dataset
y2 = [10, 30, 40, 50, 60, 85, np.nan, np.nan, np.nan, np.nan]

# Third dataset
y3 = [15, 32, 45, 52, 63, 86, 90, 95, np.nan, np.nan]

plt.plot(x, y1, label='p7', marker='x', linestyle='-')
plt.plot(x, y2, label='p8', marker='x', linestyle=':')
plt.plot(x, y3, label='p9', marker='x', linestyle='--')

plt.xlabel('Number of commands in a test')
plt.ylabel('Seconds per generated test (avg.)')
plt.title('Performance of fuzz per for properties p7, p8, p9')
plt.legend()
plt.grid(True)
plt.show()


if __name__ == '__main__':
    pass