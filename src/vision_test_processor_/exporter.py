from pathlib import Path
import json
import copy
from itertools import product

def export_camera_pos(dir_path: Path, camera_pos: dict):
    with open(dir_path / "camera_positions.json", "w") as f:
        json.dump(camera_pos, f)
        
def export_init_position(dir_path: Path, init_position: dict):
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr['initial_position'] = copy.deepcopy(init_position)
    # Convert positions from cm to m
    for axis in ['x', 'y', 'z']:
        descr['initial_position'][axis] /= 1000
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)

def clear_ground_truths(dir_path: Path):
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr['ground_truths'] = {}
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def export_triangles(dir_path: Path, triangles: dict):
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
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr.pop('test_area', None)
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)
        
def export_test_area(dir_path: Path, test_area: tuple[float, float, float, float]):
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
    with open(dir_path / "test_description.json", "r") as f:
        descr = json.load(f)
    descr["bag_start"] = bag_start
    descr['mocap_start'] = mocap_start
    with open(dir_path / "test_description.json", "w") as f:
        descr = json.dump(descr, f)