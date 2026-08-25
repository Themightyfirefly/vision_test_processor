from pathlib import Path
import json
import copy
from itertools import product

def export_camera_pos(dir_path: Path, camera_pos: dict):
    """Write the camera positions dictionary to a file.
    
    Arguments:
        dir_path: Path to the dictionary in which to write the file.
        camera_pos: Dictionary including the camera positions.
    """
    with open(dir_path / "camera_positions.json", "w") as f:
        json.dump(camera_pos, f)
        
def export_init_position(dir_path: Path, init_position: dict):
    """Write the initial camera position into a test description json file.
        
    Arguments:
        dir_path: Path to the dictionary in which the test_description.json file exists.
        init_position: Dictionary including the initial position.
    """
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr['initial_position'] = copy.deepcopy(init_position)
    # Convert positions from cm to m
    for axis in ['x', 'y', 'z']:
        descr['initial_position'][axis] /= 1000
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)

def clear_ground_truths(dir_path: Path):
    """Clear the ground_truths entry in a test description.
    
    Arguments:
        dir_path: Path to the directory in which to write the test description.
    """
    descr = {}
    if (dir_path / "test_description.json").exists():
        with open(dir_path / "test_description.json", "r") as f:
            descr = json.load(f)
        descr['ground_truths'] = {}
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def export_triangles(dir_path: Path, triangles: dict):
    """Write the triangles used as ground truths for the heightmap to the test description.
    
    Arguments:
        dir_path: Directory including the test description.
        triangles: The dictionary including the triangle information.
    """
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    if 'ground_truths' not in descr:
        descr['ground_truths'] = {}
    if 'triangles' not in descr['ground_truths']:
        descr['ground_truths']['triangles'] = []
    descr['ground_truths']['triangles'] += copy.deepcopy(triangles)
    # Convert all values to meter
    for tr in descr['ground_truths']['triangles']:
        for point, axis in product(tr, ['x', 'y', 'z']):
            point[axis] /= 1000
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def clear_test_area(dir_path: Path):
    """Generate a test_description with a cleared test_area entry.
    
    Arguments:
        dir_path: Dictionary in which to generate/ update the test description.
    """
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr.pop('test_area', None)
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def export_test_area(dir_path: Path, test_area: tuple[float, float, float, float]):
    """Export the test_area to the test description.
    
    The test area is the area in which the heightmap should be recorded during a test run.
    
    Arguments:
        dir_path: Path to the bag that includes the test description.
        test_area: Tuple of test area position in structure (max_x, min_x, max_y, min_y).
    """
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr['test_area'] = {}
    max_x, min_x, max_y, min_y = test_area
    # Save values in meters in dict
    descr['test_area']['max_x'] = max_x / 1000
    descr['test_area']['min_x'] = min_x / 1000
    descr['test_area']['max_y'] = max_y / 1000
    descr['test_area']['min_y'] = min_y / 1000
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def export_starting_times(dir_path, bag_start, mocap_start):
    """Write the test synchronisation times to the test description.
    
    Arguments:
        dir_path: Bag in which the test description exists.
        bag_start: Time in seconds at which the test starts in the bag.
        mocap_start: Time in seconds at which the test starts inn the mocap recording.
    """
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr["bag_start"] = bag_start
    descr['mocap_start'] = mocap_start
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)

def export_eval(dir_path: Path, results: dict):
    """Write the results from the evaluation to the bag.
    
    Arguments:
        dir_path: Bag in which to write results. 'results' subdir must exist.
        results: Results to be written.
    """
    with open(dir_path / "results/test_results.json", "w") as f:
        json.dump(results, f)