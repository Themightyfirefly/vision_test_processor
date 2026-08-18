import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import json
from pathlib import Path

def eval_system_diagnostics(bag_path: Path):
    with open(bag_path / 'results/system_diagnostics.json', 'r') as f:
        diag = json.load(f)
    result = {}
    result["mean_cpu_usage"] = sum(diag["cpu"]) / len(diag["cpu"])
    result["max_cpu_usage"] = max(diag["cpu"])
    squared_deviation = [(x - result["mean_cpu_usage"]) ** 2 for x in diag["cpu"]]
    result["variance_cpu_usage"] = sum(squared_deviation) / len(squared_deviation)
    result["std_error_cpu_usage"] = result["variance_cpu_usage"] ** 0.5
    return result

def eval_odom(bag_path: Path):
    with open(bag_path / 'results/odom_errors.json', 'r') as f:
        odom = json.load(f)
    odom_error = [
        np.sqrt(x**2 + y**2 + z**2)
        for x, y, z in zip(odom["x"], odom["y"], odom["z"])
    ]
    result = {}
    result["mean_odom_error"] = sum(odom_error) / len(odom_error)
    result["max_odom_error"] = max(odom_error)
    squared_deviation = [(x - result["mean_odom_error"]) ** 2 for x in odom_error]
    result["variance_odom_error"] = sum(squared_deviation) / len(squared_deviation)
    result["std_error_odom_error"] = result["variance_odom_error"] ** 0.5
    return result

def eval_heightmap(bag_path: Path):
    hmap = np.load(bag_path / f'results/heightmap_corrected.npy', allow_pickle=True)
    errors = [err for _, _, _, err in hmap if np.isfinite(err)]
    result = {}
    result["mean_heightmap_error"] = sum(errors) / len(errors)
    result["max_heightmap_error"] = max(errors)
    squared_deviation = [(x - result["mean_heightmap_error"]) ** 2 for x in errors]
    result["variance_heightmap_error"] = sum(squared_deviation) / len(squared_deviation)
    result["std_error_heightmap_error"] = result["variance_heightmap_error"] ** 0.5
    return result
