import sys
import csv
from turtle import left

# Main frequency of the mocap system (could be either cameras or pressure plates)
SYSTEM_FREQUENCY = 1000
# Frequency of the cameras in the mocap system
MOCAP_FREQUENCY = 1000

DELIMITER = ';'

# Prefixes for csv headers
CAMERA = 'Realsense_Camera'
HIGHSTEP = 'cybathlon_highstep'

def vic_to_m(num: int | float) -> float:
    """Convert a number exported to csv from Vicon Nexus to meter.
    
    It seems the measurements exported in the csv export pipeline are saved in nanometers,
    even though the column headers say they are in millimeter."""
    return float(num) / 1e9

def load_mocap_data(path : str) -> dict[str, list[str]]:
    trj_reached = False
    header = []
    data = {}
    
    with open(path, 'r', encoding="utf-8-sig") as f:
        csv_data = csv.reader(f, delimiter=DELIMITER)

        while (row := next(csv_data, None)) is not None:
            # Find the start of the marker positions (after pressure plate values)
            if not trj_reached and 'Trajectories' in row:
                trj_reached = True
                next(csv_data) # Skip the empty row after 'Trajectories' title
                continue
            # Figure out what markers there are
            if trj_reached and not header:
                subheader = next(csv_data)
                header = ['']*len(subheader)
                curr_header = ''
                for n_col in range(len(subheader)):
                    if len(row) > n_col and row[n_col]:
                        curr_header = row[n_col]
                    if subheader[n_col]:
                        header[n_col] = f'{curr_header}_{subheader[n_col]}'
                        data[header[n_col]] = []
                next(csv_data) # Skip the row including the units
                continue
            # Extract data
            if header:
                for n_col in range(len(row)):
                    if header[n_col]:
                        data[header[n_col]].append(row[n_col])
        return data                       

def get_shapes(data):
    shapes = ['triangle', 'camera']
    

def translate_triangle():
    pass

def get_camera_origin(data, starting_time: float = 0.0):
    """Get the translation and rotation of the camera at the starting time."""
    


def process():
    if len(sys.argv) < 2:
    	print("Script for processing mocap data of a vision test case.")
    	print("Usage: python process_mocap.py <path_to_mocap_data.csv>")
    	sys.exit(1)
    raw_data = load_mocap_data(sys.argv[1])
    print(raw_data.keys())

    from vision_test_processor_.util import create_frame, local_to_global, global_to_local
    from scipy.spatial.transform import Rotation
    import numpy as np

    right = np.array([raw_data["Realsense_Camera:right_X"][11], raw_data["Realsense_Camera:right_Y"][11], raw_data["Realsense_Camera:right_Z"][11]])
    left = np.array([raw_data["Realsense_Camera:left_X"][11], raw_data["Realsense_Camera:left_Y"][11], raw_data["Realsense_Camera:left_Z"][11]])
    top = np.array([raw_data["Realsense_Camera:top_X"][11], raw_data["Realsense_Camera:top_Y"][11], raw_data["Realsense_Camera:top_Z"][11]])

    origin, rotation_matrix = create_frame(right, left, top)

    local_point = np.array([0.0, 0.0, 0.0])

    global_point = local_to_global(
        local_point,
        origin,
        rotation_matrix,
    )

    print("Local point:", local_point)
    print("Global point:", global_point)

    roll, pitch, yaw = Rotation.from_matrix(
        rotation_matrix
    ).as_euler("xyz", degrees=False)
        
    print("Roll:", roll)
    print("Pitch:", pitch)
    print("Yaw:", yaw)
    
    qx, qy, qz, qw = Rotation.from_matrix(rotation_matrix).as_quat()

    print("Quaternion [x, y, z, w]:")
    print(qx, qy, qz, qw)