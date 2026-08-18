from pathlib import Path
import json

def join_results(targets: list[Path], write_to: Path = Path("joint_test_results.csv")):
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
    with open(write_to, "w") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(v) for v in row) + "\n")
