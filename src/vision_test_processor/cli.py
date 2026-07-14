import argparse
from pathlib import Path
import json
from vision_test_processor_.processing import get_camera_positions, load_mocap_data, get_test_area
from vision_test_processor.config import *
from vision_test_processor_.exporter import (
    export_camera_pos,
    export_init_position,
    export_triangles,
    export_test_area,
    clear_ground_truths,
    clear_test_area,
    export_starting_times
)
from vision_test_processor_.ground_truths import extract_triangles
from vision_test_processor_.plotting import plot_heightmap, plot_system_diagnostics, plot_odom

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory_location', help='Path to the directory that includes csv, bag and such.')
    parser.add_argument('starting_time_bag', type=float, nargs="?", help='Starting time of the camera bag in s.')
    parser.add_argument('starting_time_mocap', type=float, nargs="?", help='Starting time of the mocap in s.')
    parser.add_argument('--plot_heightmap', action='store_true', help='Plot the heightmap in 3D including measured errors.')
    parser.add_argument('--plot_system_diagnostics', action='store_true', help='Plot the cpu usage during test.')
    parser.add_argument('--plot_odom', action='store_true', help='Plot the errors of the odometry.')
    
    
    args = parser.parse_args()
    dir_path = Path(args.directory_location)
    if args.plot_heightmap:
        plot_heightmap(dir_path)
    if args.plot_system_diagnostics:
        plot_system_diagnostics(dir_path)
    if args.plot_odom:
        plot_odom(dir_path)
    
    
    if not (args.starting_time_bag and args.starting_time_mocap):
        print("No postprocessing of test results. To start processing include values for starting_time_camera and starting_time_mocap")
        return
    raw_data = load_mocap_data(f'{args.directory_location}/mocap_raw.csv', args.starting_time_mocap)
    # Calculate times from frames in ms
    raw_data['time'] = [1 / MOCAP_FREQUENCY * int(frame) if frame else -1 for frame in raw_data['_Frame']]
    camera_pos = get_camera_positions(raw_data, args.starting_time_mocap)

    # Clear all keys that can remain empty
    clear_ground_truths(dir_path)
    clear_test_area(dir_path)

    export_camera_pos(dir_path, camera_pos)
    export_starting_times(dir_path, args.starting_time_bag, args.starting_time_mocap)
    
    
    init_pos = {
        'x': camera_pos['x'][0],
        'y': camera_pos['y'][0],
        'z': camera_pos['z'][0],
        'roll': camera_pos['roll'][0],
        'pitch': camera_pos['pitch'][0],
        'yaw': camera_pos['yaw'][0]
    }
    export_init_position(dir_path, init_pos)
    
    if any([key.startswith(HIGHSTEP) for key in raw_data.keys()]):
        triangles = extract_triangles(raw_data, HIGHSTEP, HIGHSTEP_TRIANGLES)
        export_triangles(dir_path, triangles)
        test_area = get_test_area(triangles)
        export_test_area(dir_path, test_area)
        
    