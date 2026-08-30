from pathlib import Path
import json
import pandas as pd

from vision_test_processor_.eval import calc_mean

def join_results(targets: list[Path], write_to: Path):
    """Combine the results of multiple tests in one csv file.
    
    Arguments:
        targets: List of Paths to bags to be included.
        write_to: csv file where the results are written to.
    
    Returns:
        Combined results.
    """
    # For each dir
    all_results = []
    for target in targets:
        # Get all test dirs if result is in dir
        test_dirs = [
            d for d in target.iterdir() if d.is_dir()
            and (d / "results/test_results.json").exists()
        ]

    for dir in test_dirs:
        # Read the test results
        with open(dir / "results/test_results.json", "r") as f:
            results = json.load(f)
            results["test_name"] = dir.name
        # Append the results to a list
        all_results.append(results)
    # Get all keys
    keys = set([k for result in all_results for k in result.keys()])
    # Make it to a csv header
    header = ["test_name"] + list(keys)
    # Go through each dict
    rows = []
    for result in all_results:
        # Start with a row full of Nones
        row = [None] * len(header)
        # Write each value into correct column
        for k, v in result.items():
            index = header.index(k)
            row[index] = v
        rows.append(row)

    # write to joint_test_results.csv
    print(f'Writing a csv file with all testcase results to {write_to}.')
    with open(write_to, "w") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(v) for v in row) + "\n")

    return all_results


def match_ids_to_bags(targets: list[Path], factors: dict):
    """Extract a list of bags that belong to a test id.
    
    Arguments:
        targets: List of bags to be matched.
        factors: Dictionary including the ids as keys.
    
    Returns:
        Dictionary matching ids to lists of the corresponding bags.
    """
    bags_per_id = {}
    for factor in factors.keys():
        bags_per_id[factor] = [
            dir for target in targets for dir in target.iterdir()
            if dir.is_dir() and dir.name.startswith(f'{factor}_')
            and (dir / "results/test_results.json").exists()
        ]
    return bags_per_id


def get_results_per_id(bags_per_id: dict):
    """Combines the results so that we have single values for each id.
    
    Arguments:
        bags_per_id: Dictionary with structure id -> list of corresponding bags.
        
    Returns:
        Dictionary with structure id -> results.
    """
    res_per_id = {}
    # Extract results from individual files
    for id in bags_per_id:
        results = []
        for bag in bags_per_id[id]:
            with open(bag / "results/test_results.json", 'r') as f:
                results.append(json.load(f))
        
        # Build averages over individual results
        res_per_id[id] = {}
        res_per_id[id]['mean_cpu_usage'] = calc_mean([res['mean_cpu_usage'] for res in results])
        res_per_id[id]['variance_cpu_usage'] = calc_mean([res['variance_cpu_usage'] for res in results])
        
        res_per_id[id]['mean_odom_error'] = calc_mean([res['mean_odom_error'] for res in results])
        res_per_id[id]['variance_odom_error'] = calc_mean([res['variance_odom_error'] for res in results])
        
        res_per_id[id]['mean_heightmap_error'] = calc_mean([res['mean_heightmap_error'] for res in results])
        res_per_id[id]['variance_heightmap_error'] = calc_mean([res['variance_heightmap_error'] for res in results])
    
    return res_per_id


def generate_experiment_df(bags_per_id: dict, factors: dict):
    """Generates a dataframe in which each row represents one test.
    
    Arguments:
        bags_per_id:
        factors:
    
    Returns:
        data frame
    """
    keys = ["mean_cpu_usage", "variance_cpu_usage", "mean_odom_error", "variance_odom_error", "mean_heightmap_error", "max_heightmap_error"]
    data = []
    for id in bags_per_id:
        for bag in bags_per_id[id]:
            row = factors[str(id)].copy()
            # Convert factor range from 0/1 to -1/1, will help with analysis
            row = [1 if val == 1 else -1 for val in row]
            with open(bag / "results/test_results.json", 'r') as f:
                result = json.load(f)
            
            row += [result[key] for key in keys]
            data.append(row)
    
    column_names = [f"F_{i+1}" for i in range(len(factors[list(factors.keys())[0]]))] + keys
    return pd.DataFrame(data, columns=column_names)