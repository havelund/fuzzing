
"""
Reproducible plotting script for test-generation experiments (with vs without strings).

Figures produced (saved as PNG and PDF under ./figures):
  1) all_exec_time: Execution time vs test length (All properties)
  2) all_sat_time: Total SAT time vs test length (All properties)
  3) all_formula_time: Formula generation time vs test length (All properties)
  4) per_property_exec: Execution time per property (P1–P10)
  5) per_property_sat: Total SAT time per property (P1–P10)
  6) all_sat_time_combined: Total SAT time vs test length (All properties combined only)
  7) all_decomposition: Execution time decomposition (Formula vs SAT) at selected lengths

Style (consistent, color+line-type and B/W friendly):
  - Without strings = green, solid line, filled markers
  - With strings = red, dashed line, open markers
  - Stacked bars use neutral grays with hatching to avoid color confusion

Usage:
  python generate_plots.py
"""

import os
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import pandas as pd

# Ensure output dir
OUTDIR = "figures"
os.makedirs(OUTDIR, exist_ok=True)

# ------------------------------
# Data: All properties (series)
# ------------------------------
length_ws = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 250, 300]
exec_ws   = [0.379, 1.275, 3.247, 6.047, 11.083, 20.166, 29.281, 39.065, 53.807, 84.830, 121.071, 165.672, 173.875, 226.967, 586.001, 740.176, 507.659, 710.689, 1418.201, 2611.269, 2885.336, 3649.141, 8105.692]
formula_ws= [0.268, 0.840, 2.028, 4.099, 7.351, 11.988, 18.442, 26.692, 37.341, 50.268, 65.805, 84.223, 107.588, 132.296, 161.554, 198.512, 233.020, 275.260, 324.467, 376.380, 434.889, 721.795, 1263.936]
sat_ws    = [0.110, 0.433, 1.218, 1.947, 3.730, 8.177, 10.837, 12.371, 16.463, 34.560, 55.264, 81.447, 66.284, 94.668, 424.445, 541.661, 274.634, 435.426, 1093.731, 2234.885, 2450.442, 2927.341, 6841.751]

length_s  = [10, 20, 30, 40, 50]
exec_s    = [1.060, 24.288, 61.618, 137.228, 1780.839]
formula_s = [0.286, 0.812, 1.994, 4.092, 7.299]
sat_s     = [0.773, 23.475, 59.624, 133.135, 1773.539]

df_without = pd.DataFrame({
    "length": length_ws, "execution": exec_ws, "formula": formula_ws, "sat_total": sat_ws, "experiment": "without strings"
})
df_with = pd.DataFrame({
    "length": length_s, "execution": exec_s, "formula": formula_s, "sat_total": sat_s, "experiment": "with strings"
})
df_all = pd.concat([df_without, df_with], ignore_index=True)

# ------------------------------
# Data: Per-property EXECUTION (10..100)
# ------------------------------
per_property_exec = {
    "without strings": {
        "P1": [0.196,0.298,0.404,0.474,0.567,0.696,0.830,0.943,1.189,1.144],
        "P2": [0.184,0.289,0.375,0.483,0.541,0.637,0.767,0.856,0.944,1.061],
        "P3": [0.166,0.231,0.304,0.375,0.447,0.522,0.586,0.663,0.753,0.833],
        "P4": [0.160,0.250,0.307,0.375,0.468,0.528,0.588,0.690,0.777,0.852],
        "P5": [0.187,0.299,0.480,0.681,0.904,1.164,1.476,1.836,2.181,2.661],
        "P6": [0.191,0.296,0.395,0.545,0.706,0.894,1.102,1.349,1.590,1.849],
        "P7": [0.236,0.571,1.257,2.374,4.077,6.540,9.527,14.196,19.357,27.685],
        "P8": [0.214,0.501,1.116,1.892,3.770,6.166,8.996,14.073,17.659,21.066],
        "P9": [0.192,0.393,0.804,1.503,2.490,3.907,6.244,9.758,11.827,15.700],
        "P10":[0.156,0.230,0.298,0.360,0.442,0.506,0.558,0.658,0.708,0.782]
    },
    "with strings": {
        "P1": [0.247,0.296,0.393,0.590,0.798,0.844,0.991,1.211,1.377,1.743],
        "P2": [0.201,0.290,1.020,0.526,1.841,0.901,0.949,1.180,1.368,1.693],
        "P3": [0.178,0.252,0.337,0.438,0.526,0.640,0.752,0.873,0.982,1.101],
        "P4": [0.163,0.258,0.347,0.428,0.520,0.629,0.752,0.839,0.970,1.110],
        "P5": [0.193,0.331,0.500,0.724,0.984,1.288,1.642,2.056,2.463,3.084],
        "P6": [0.173,0.294,0.413,0.596,0.783,0.993,1.241,1.542,1.867,2.196],
        "P7": [0.533,1.994,7.809,18.973,34.053,94.353,107.646,246.082,312.427,None],
        "P8": [0.846,2.342,4.462,6.631,11.898,14.151,36.793,28.020,48.580,189.204],
        "P9": [0.742,1.900,11.664,17.238,33.754,131.566,None,None,None,None],
        "P10":[0.163,0.253,0.314,0.435,0.510,0.604,0.714,0.850,0.924,1.043]
    }
}
lengths_10_100 = [10,20,30,40,50,60,70,80,90,100]

# ------------------------------
# Data: Per-property TOTAL SAT (10..100)
# ------------------------------
sat_without = {
    "P1": [0.045,0.105,0.171,0.203,0.256,0.327,0.410,0.484,0.701,0.618],
    "P2": [0.043,0.103,0.139,0.188,0.231,0.283,0.349,0.400,0.449,0.531],
    "P3": [0.035,0.071,0.105,0.140,0.176,0.209,0.244,0.286,0.330,0.379],
    "P4": [0.035,0.073,0.105,0.141,0.181,0.215,0.247,0.298,0.338,0.386],
    "P5": [0.039,0.083,0.138,0.200,0.270,0.353,0.447,0.574,0.649,0.822],
    "P6": [0.037,0.074,0.110,0.155,0.197,0.243,0.292,0.352,0.397,0.467],
    "P7": [0.054,0.143,0.335,0.616,0.924,1.334,1.665,2.794,3.382,6.092],
    "P8": [0.055,0.187,0.464,0.657,1.650,2.846,3.959,6.734,7.487,7.367],
    "P9": [0.043,0.103,0.193,0.355,0.520,0.695,1.302,2.414,1.766,2.462],
    "P10":[0.033,0.069,0.101,0.135,0.171,0.200,0.236,0.275,0.307,0.350],
}
sat_with = {
    "P1": [0.097,0.124,0.180,0.322,0.474,0.485,0.600,0.787,0.916,1.237],
    "P2": [0.054,0.118,0.793,0.270,1.531,0.551,0.556,0.750,0.886,1.184],
    "P3": [0.041,0.089,0.138,0.199,0.262,0.343,0.413,0.494,0.591,0.686],
    "P4": [0.039,0.091,0.143,0.198,0.254,0.326,0.421,0.482,0.584,0.677],
    "P5": [0.047,0.105,0.176,0.278,0.367,0.488,0.628,0.812,0.972,1.269],
    "P6": [0.041,0.088,0.135,0.215,0.283,0.361,0.444,0.576,0.699,0.825],
    "P7": [0.364,1.587,6.892,17.192,30.925,89.252,99.680,234.139,296.442,None],
    "P8": [0.696,2.028,3.828,5.435,9.832,10.842,31.706,20.711,38.499,175.495],
    "P9": [0.594,1.604,11.078,16.115,31.805,128.419,None,None,None,None],
    "P10":[0.045,0.087,0.129,0.204,0.258,0.313,0.405,0.516,0.555,0.638],
}

# ------------------------------
# Helpers: consistent style
# ------------------------------
def plot_series(x: List[int], y: List[float], label: str, color: str, linestyle: str, filled: bool):
    markerface = color if filled else "white"
    plt.plot(x, y, marker="o", label=label, color=color, linestyle=linestyle,
             markerfacecolor=markerface, markeredgecolor=color)

def savefig(name: str):
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, f"{name}.png"), dpi=300)
    plt.savefig(os.path.join(OUTDIR, f"{name}.pdf"))
    plt.close()

# ------------------------------
# 1) All properties: Execution
# ------------------------------
plt.figure(figsize=(10,6))
plot_series(df_without["length"].tolist(), df_without["execution"].tolist(), "without strings", "green", "-", True)
plot_series(df_with["length"].tolist(), df_with["execution"].tolist(), "with strings", "red", "--", False)
plt.yscale("log")
plt.xlabel("Test length (number of commands)")
plt.ylabel("Execution time (s, log)")
plt.title("Execution time vs. test length (All properties)")
plt.legend(title="Experiment")
savefig("all_exec_time")

# ------------------------------
# 2) All properties: SAT total
# ------------------------------
plt.figure(figsize=(10,6))
plot_series(df_without["length"].tolist(), df_without["sat_total"].tolist(), "without strings", "green", "-", True)
plot_series(df_with["length"].tolist(), df_with["sat_total"].tolist(), "with strings", "red", "--", False)
plt.yscale("log")
plt.xlabel("Test length (number of commands)")
plt.ylabel("Total SAT time (s, log)")
plt.title("Total SAT time vs. test length (All properties)")
plt.legend(title="Experiment")
savefig("all_sat_time")

# ------------------------------
# 3) All properties: Formula generation
# ------------------------------
plt.figure(figsize=(10,6))
plot_series(df_without["length"].tolist(), df_without["formula"].tolist(), "without strings", "green", "-", True)
plot_series(df_with["length"].tolist(), df_with["formula"].tolist(), "with strings", "red", "--", False)
plt.yscale("log")
plt.xlabel("Test length (number of commands)")
plt.ylabel("Formula generation time (s, log)")
plt.title("Formula generation time vs. test length (All properties)")
plt.legend(title="Experiment")
savefig("all_formula_time")

# ------------------------------
# 4) Per-property Execution (small multiples)
# ------------------------------
props = ["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10"]
fig, axes = plt.subplots(2, 5, figsize=(18, 8), sharex=True, sharey=True)
axes = axes.flatten()
for i, prop in enumerate(props):
    ax = axes[i]
    y_wo = per_property_exec["without strings"][prop]
    y_wi = per_property_exec["with strings"][prop]
    x_wo = lengths_10_100
    x_wi = [x for x, y in zip(lengths_10_100, y_wi) if y is not None]
    y_wi = [y for y in y_wi if y is not None]
    # without
    ax.plot(x_wo, y_wo, marker="o", color="green", linestyle="-",
            label="without strings", markerfacecolor="green", markeredgecolor="green")
    # with
    ax.plot(x_wi, y_wi, marker="o", color="red", linestyle="--",
            label="with strings", markerfacecolor="white", markeredgecolor="red")
    ax.set_title(prop)
    ax.set_yscale("log")
    if i % 5 == 0:
        ax.set_ylabel("Execution time (s, log)")
    if i >= 5:
        ax.set_xlabel("Test length")
axes[0].legend(title="Experiment")
plt.suptitle("Execution time per property — with vs without strings", y=1.02)
plt.tight_layout()
fig.savefig(os.path.join(OUTDIR, "per_property_exec.png"), dpi=300)
fig.savefig(os.path.join(OUTDIR, "per_property_exec.pdf"))
plt.close(fig)

# ------------------------------
# 5) Per-property SAT total (small multiples)
# ------------------------------
fig, axes = plt.subplots(2, 5, figsize=(18, 8), sharex=True, sharey=True)
axes = axes.flatten()
for i, prop in enumerate(props):
    ax = axes[i]
    y_wo = sat_without[prop]
    y_wi = sat_with[prop]
    x_wo = lengths_10_100
    x_wi = [x for x, y in zip(lengths_10_100, y_wi) if y is not None]
    y_wi = [y for y in y_wi if y is not None]
    # without
    ax.plot(x_wo, y_wo, marker="o", color="green", linestyle="-",
            label="without strings", markerfacecolor="green", markeredgecolor="green")
    # with
    ax.plot(x_wi, y_wi, marker="o", color="red", linestyle="--",
            label="with strings", markerfacecolor="white", markeredgecolor="red")
    ax.set_title(prop)
    ax.set_yscale("log")
    if i % 5 == 0:
        ax.set_ylabel("Total SAT time (s, log)")
    if i >= 5:
        ax.set_xlabel("Test length")
axes[0].legend(title="Experiment")
plt.suptitle("Total SAT time per property — with vs without strings", y=1.02)
plt.tight_layout()
fig.savefig(os.path.join(OUTDIR, "per_property_sat.png"), dpi=300)
fig.savefig(os.path.join(OUTDIR, "per_property_sat.pdf"))
plt.close(fig)

# ------------------------------
# 6) All properties combined: SAT total (single plot)
# ------------------------------
plt.figure(figsize=(10,6))
plot_series(df_without["length"].tolist(), df_without["sat_total"].tolist(), "without strings", "green", "-", True)
plot_series(df_with["length"].tolist(), df_with["sat_total"].tolist(), "with strings", "red", "--", False)
plt.yscale("log")
plt.xlabel("Test length (number of commands)")
plt.ylabel("Total SAT time (s, log)")
plt.title("Total SAT time vs. test length (All properties combined)")
plt.legend(title="Experiment")
savefig("all_sat_time_combined")

# ------------------------------
# 7) Stacked bars: formula vs SAT (neutral colors & hatching)
# ------------------------------
sel_lengths = [10,30,50,100]
# Without strings (selected)
formula_ws_sel = [0.268, 2.028, 7.351, 50.268]
sat_ws_sel     = [0.110, 1.218, 3.730, 34.560]
# With strings (selected; None becomes 0 for stacking)
formula_s_sel  = [0.286, 1.994, 7.299, 0.0]
sat_s_sel      = [0.773, 59.624, 1773.539, 0.0]

labels = [f"{l}\nwithout" for l in sel_lengths] + [f"{l}\nwith" for l in sel_lengths]
formulas = formula_ws_sel + formula_s_sel
sats     = sat_ws_sel + sat_s_sel

plt.figure(figsize=(10,6))
plt.bar(labels, formulas, label="Formula gen", color="lightgray", hatch="///")
plt.bar(labels, sats, bottom=formulas, label="SAT total", color="dimgray", hatch="\\\\\\")
plt.yscale("log")
plt.ylabel("Time (s, log)")
plt.title("Execution time decomposition (All properties, selected lengths)")
plt.xticks(rotation=0)
plt.legend()
savefig("all_decomposition")

print(f"Saved figures to: {os.path.abspath(OUTDIR)}")
