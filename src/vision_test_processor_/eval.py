import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import json
from pathlib import Path
from itertools import product
from functools import reduce
from operator import xor

def calc_mean(values: list[float]):
    return sum(values) / len(values)

def calc_variance(values: list[float]):
    squared_deviation = [(x - calc_mean(values)) ** 2 for x in values]
    return calc_mean(squared_deviation)

def calc_std_error(values: list[float]):
    return calc_variance(values) ** 0.5

def eval_system_diagnostics(bag_path: Path):
    with open(bag_path / 'results/system_diagnostics.json', 'r') as f:
        diag = json.load(f)
    result = {}
    result["mean_cpu_usage"] = calc_mean(diag["cpu"])
    result["max_cpu_usage"] = max(diag["cpu"])
    result["variance_cpu_usage"] = calc_variance(diag["cpu"])
    result["std_error_cpu_usage"] = calc_std_error(diag["cpu"])
    return result

def eval_odom(bag_path: Path):
    with open(bag_path / 'results/odom_errors.json', 'r') as f:
        odom = json.load(f)
    odom_error = [
        np.sqrt(x**2 + y**2 + z**2)
        for x, y, z in zip(odom["x"], odom["y"], odom["z"])
    ]
    result = {}
    result["mean_odom_error"] = calc_mean(odom_error)
    result["max_odom_error"] = max(odom_error)
    result["variance_odom_error"] = calc_variance(odom_error)
    result["std_error_odom_error"] = calc_std_error(odom_error)
    return result

def eval_heightmap(bag_path: Path):
    hmap = np.load(bag_path / f'results/heightmap_corrected.npy', allow_pickle=True)
    errors = [err for _, _, _, err in hmap if np.isfinite(err)]
    result = {}
    result["mean_heightmap_error"] = calc_mean(errors)
    result["max_heightmap_error"] = max(errors)
    result["variance_heightmap_error"] = calc_variance(errors)
    result["std_error_heightmap_error"] = calc_std_error(errors)
    return result

def get_delta_by_fac(res_per_id, factors_per_id, facs: list[int]):
    # Find all ids that respond to high and low values of the factor
    deltas = {}
    high_ids, low_ids = [], []
    for id in res_per_id.keys():
        if reduce(xor, [factors_per_id[id][fac] for fac in facs]) == 1:
            high_ids.append(id)
        else:
            low_ids.append(id)

    # Combine results from each id and build difference
    high_res = [res_per_id[id] for id in high_ids]
    low_res = [res_per_id[id] for id in low_ids]

    for res_name in high_res[0].keys():
        high_val = calc_mean([res[res_name] for res in high_res])
        low_val = calc_mean([res[res_name] for res in low_res])
        deltas["\u0394_" + res_name] = high_val - low_val
    return deltas

def eval_individual_effects(res_per_id, factors_per_id: dict):
    num_factors = len(factors_per_id[list(factors_per_id.keys())[0]])
    # First evaluate effects for each individual factor
    indiv_effects= [{} for _ in range(num_factors)]
    for fac in range(num_factors):
        indiv_effects[fac] = get_delta_by_fac(res_per_id, factors_per_id, [fac])
    return indiv_effects

def eval_dual_effects(res_per_id, factors_per_id: dict[str, list[int]]):
    """Calculates effects between each pair of factors.
    
    Does not check whether factors are independent from each other in experiment.
    For partial factorial experiments those pairs must be ignored.
    
    Arguments:
        res_per_id: Dictionary with single number results from experiment.
        factors_per_id: Dictionary including the factors for each id, where 1 is high.
        
    Returns:
        Dictionary with effects for each pair of factors
    """
    num_factors = len(factors_per_id[list(factors_per_id.keys())[0]])
    factor_pairs = [(i, j) for i in range(num_factors) for j in range(i + 1, num_factors)]
    pair_effects = {}
    for i, j in factor_pairs:
        pair_effects[f'{i+1}_{j+1}'] = get_delta_by_fac(res_per_id, factors_per_id, [i, j])

    return pair_effects
