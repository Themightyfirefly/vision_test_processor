import argparse
from pathlib import Path
import json
import re 

from vision_test_processor_.eval import (
    eval_heightmap,
    eval_odom,
    eval_system_diagnostics,
    eval_individual_effects,
    eval_dual_effects
)
from vision_test_processor_.exporter import (
    export_camera_pos,
    export_eval,
    export_init_position,
    export_triangles,
    export_test_area,
    clear_ground_truths,
    clear_test_area,
    export_starting_times
)
from vision_test_processor_.ground_truths import extract_triangles
from vision_test_processor_.join_results import join_results, match_ids_to_bags, get_results_per_id
from vision_test_processor_.plotting import plot_heightmap, plot_system_diagnostics, plot_odom, plot_odom_raw
from vision_test_processor_.processing import get_camera_positions, load_mocap_data, get_test_area

from vision_test_processor.config import *


def cli():
    """Command line interface definitions for the vision_test application."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)

    # Prep is used to exctract data from a mocap csv file and to write json test descriptions.
    # It can then be tested by the vision tests in rise-os-core.
    prep_parser = commands.add_parser('prep')
    prep_parser.set_defaults(func=prep)
    prep_parser.add_argument('directory_location', help='Path to the directory that includes csv, bag and such.')
    prep_parser.add_argument('starting_time_bag', type=float, nargs="?", help='Starting time of the camera bag in s.')
    prep_parser.add_argument('starting_time_mocap', type=float, nargs="?", help='Starting time of the mocap in s.')


    # The 'plot' command visualises all kinds of analysis results
    plot_parser = commands.add_parser('plot')
    plot_parser.set_defaults(func=plot)
    plot_commands = plot_parser.add_subparsers(dest='target', required=True)

    heightmap_parser = plot_commands.add_parser('heightmap')
    heightmap_parser.add_argument('directory_location', help='Path to the bag directory that includes the results directory.')

    heightmap_corr_parser = plot_commands.add_parser('heightmap_corrected')
    heightmap_corr_parser.add_argument('directory_location', help='Path to the bag directory that includes the results directory.')

    system_parser = plot_commands.add_parser('diagnostics')
    system_parser.add_argument('directory_location', help='Path to the bag directory that includes the results directory.')
    
    odom_error_parser = plot_commands.add_parser('odom_error')
    odom_error_parser.add_argument('directory_location', help='Path to the bag directory that includes the results directory.')
    
    odom_raw_parser = plot_commands.add_parser('odom_raw')
    odom_raw_parser.add_argument('directory_location', help='Path to the bag directory that includes the results directory.')


    # The 'eval' commad calculates single result values
    eval_parser = commands.add_parser('eval')
    eval_parser.set_defaults(func=eval)
    eval_parser.add_argument('directory_location', nargs='+', help='Path to the bag directory that includes the results directory.')
    eval_parser.add_argument('--all', action='store_true', help='Instead of passing a single bag, pass a directory with multiple bags inside.')


    # Generate joint test results for all tests in a directory
    joint_parser = commands.add_parser('join_results')
    joint_parser.set_defaults(func=call_join)
    joint_parser.add_argument('test_bag_locations', nargs='+', help='Paths to the directories that includes the test bag directories')
    joint_parser.add_argument('--write_to', default='joint_test_results.csv', help='Path to the output csv file. Default is ./joint_test_results.csv')
    joint_parser.add_argument('--factors', default='', help='Path to a file containing the experiment factors.')

    args = parser.parse_args()
    args.func(args)

        
def plot(args):
    """Processing cli arguments given with vision_test call.
    
    Arguments:
        args: argparse arguments
    """
    match args.target:
        case 'heightmap':
            plot_heightmap(Path(args.directory_location))
        case 'heightmap_corrected':
            plot_heightmap(Path(args.directory_location), corrected=True)
        case 'diagnostics':
            plot_system_diagnostics(Path(args.directory_location))
        case 'odom_error':
            plot_odom(Path(args.directory_location))
        case 'odom_raw':
            plot_odom_raw(Path(args.directory_location))
        case _:
            pass


def prep(args):
    """Reading mocap data and writing the ground truths for a testcase.
    
    Arguments:
        args: argparse arguments
    """
    dir_path = Path(args.directory_location)
    csv_files = [f.name for f in list(dir_path.glob("*.csv"))]
    mocap_name = ""
    if "mocap_raw.csv" in csv_files:
        mocap_name = "mocap_raw.csv"
    elif len(csv_files) == 1:
        mocap_name = csv_files[0]
    else:
        raise ValueError("More than one csv file found. Rename the mocap file to 'mocap_raw.csv'")

    raw_data = load_mocap_data(f'{args.directory_location}/{mocap_name}', args.starting_time_mocap)
    # Calculate times from frames in ms
    raw_data['time'] = [int(frame) / MOCAP_FREQUENCY if frame else -1 for frame in raw_data['_Frame']]
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

def eval(args):
    """Combine the test results from one testcase into single numbers.
    
    Arguments:
        args: argparse arguments
    """
    dirs_to_eval = []
    if len(args.directory_location) == 0:
        raise IndexError('Path to bag directory required.')
    if args.all:
        dirs_to_eval += [
            bag for dir in args.directory_location for bag in Path(dir).iterdir()
            if bag.is_dir()
            and (bag / "results").exists()
        ]
    else:
        dirs_to_eval.append(Path(args.directory_location[0]))

    for dir_path in dirs_to_eval:
        print(f"Evaluating {dir_path}")
        results = {}
        results |= eval_system_diagnostics(dir_path)
        results |= eval_odom(dir_path)
        results |= eval_heightmap(dir_path)
        export_eval(dir_path, results)

def call_join(args):
    """Use the results from bags to generate an overall experiment result.
    
    Arguments:
        args: argparse arguments
    """
    test_dirs = [Path(test_dir) for test_dir in args.test_bag_locations]
    results = join_results(test_dirs, Path(args.write_to))
    
    if args.factors:
        # Factor information is given, so effects between factors can be investigated
        with open(args.factors, 'r') as f:
            factors = json.load(f)
        bags_per_id = match_ids_to_bags(test_dirs, factors)
        res_per_id = get_results_per_id(bags_per_id)
        indiv_results = eval_individual_effects(res_per_id, factors)
        print(indiv_results)
        pair_effects = eval_dual_effects(res_per_id, factors)
        print(pair_effects)