import csv
import numpy as np

from vision_test_processor.config import *
from vision_test_processor_.camera_calc import create_frame, local_to_global, markers_to_camera


def load_mocap_data(path : str, start_time: float) -> dict[str, list[str]]:
    trj_reached = False
    header = []
    data = {"time": []}
    
    with open(path, 'r', encoding="utf-8-sig") as f:
        csv_data = csv.reader(f, delimiter=DELIMITER)

        while (row := next(csv_data, None)) is not None and any(entry for entry in row):
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
                # Only start extracting if start time has been reached
                if float(row[header.index('_Frame')]) * 1 / MOCAP_FREQUENCY < start_time:
                    continue
                for n_col in range(len(row)):
                    if header[n_col]:
                        data[header[n_col]].append(row[n_col])
        return data                       

def get_camera_positions(raw_data, mocap_start):
    camera_pos = {
        'time': [],
        'x': [],
        'y': [],
        'z': [],
        'roll': [],
        'pitch': [],
        'yaw': [],
    }
    for i in range(len(raw_data["time"])):
        if raw_data["time"][i] < mocap_start:
            continue
        right = [raw_data[f"{CAMERA}:{RIGHT}_X"][i], raw_data[f"{CAMERA}:{RIGHT}_Y"][i], raw_data[f"{CAMERA}:{RIGHT}_Z"][i]]
        left = [raw_data[f"{CAMERA}:{LEFT}_X"][i], raw_data[f"{CAMERA}:{LEFT}_Y"][i], raw_data[f"{CAMERA}:{LEFT}_Z"][i]]
        top = [raw_data[f"{CAMERA}:{TOP}_X"][i], raw_data[f"{CAMERA}:{TOP}_Y"][i], raw_data[f"{CAMERA}:{TOP}_Z"][i]]
        # Skip the current values if a marker is missing
        if not all([pos[i] for i in range(3) for pos in [right, left, top]]):
            continue
        global_point, roll, pitch, yaw = markers_to_camera(right, left, top)
        camera_pos['time'].append(raw_data['time'][i])
        camera_pos['x'].append(global_point[0])
        camera_pos['y'].append(global_point[1])
        camera_pos['z'].append(global_point[2])
        camera_pos['roll'].append(roll)
        camera_pos['pitch'].append(pitch)
        camera_pos['yaw'].append(yaw)
    return camera_pos

def get_test_area(triangles):
    max_x = max([tr[i]['x'] for tr in triangles for i in range(3)]) + TEST_AREA_PADDING_X
    min_x = min([tr[i]['x'] for tr in triangles for i in range(3)]) - TEST_AREA_PADDING_X
    max_y = max([tr[i]['y'] for tr in triangles for i in range(3)]) + TEST_AREA_PADDING_Y
    min_y = min([tr[i]['y'] for tr in triangles for i in range(3)]) - TEST_AREA_PADDING_Y
    return (max_x, min_x, max_y, min_y)