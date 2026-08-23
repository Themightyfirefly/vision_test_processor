from pathlib import Path
import json

def join_results(targets: list[Path], write_to: Path):
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
    bags_per_id = {}
    for factor in factors.keys():
        bags_per_id[factor] = [
            dir for target in targets for dir in target.iterdir()
            if dir.is_dir() and dir.name.startswith(f'{factor}_')
            and (dir / "results/test_results.json").exists()
        ]
    return bags_per_id


def get_results_per_id(bags_per_id: dict):
    """Combines the results so that we have single values for each id."""
    res_per_id = {}
    # Extract results from individual files
    for id in bags_per_id:
        results = []
        for bag in bags_per_id[id]:
            with open(bag / "results/test_results.json", 'r') as f:
                results.append(json.load(f))
        
        # Build averages over individual results
        res_per_id[id] = {}
        mean_cpu_usages = [res['mean_cpu_usage'] for res in results]
        res_per_id[id]['mean_of_mean_cpu_usage'] = sum(mean_cpu_usages) / len(mean_cpu_usages)
        res_per_id[id]['max_cpu_usage'] = max([res['max_cpu_usage'] for res in results])
        
        mean_odom_error = [res['mean_odom_error'] for res in results]
        res_per_id[id]['mean_of_mean_odom_error'] = sum(mean_odom_error) / len(mean_odom_error)
        res_per_id[id]['max_odom_error'] = max([res['max_odom_error'] for res in results])
        
        mean_heightmap_error = [res['mean_heightmap_error'] for res in results]
        res_per_id[id]['mean_of_mean_heightmap_error'] = sum(mean_heightmap_error) / len(mean_heightmap_error)
        res_per_id[id]['max_heightmap_error'] = max([res['max_heightmap_error'] for res in results])
    
    return res_per_id