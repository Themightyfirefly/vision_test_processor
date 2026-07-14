from statistics import median
import numpy as np
from itertools import product
from vision_test_processor.config import *

def translate_triangle(triangle: list[dict[str, float]]):
    p1 = np.array([triangle[0]['x'], triangle[0]['y'], triangle[0]['z']])
    p2 = np.array([triangle[1]['x'], triangle[1]['y'], triangle[1]['z']])
    p3 = np.array([triangle[2]['x'], triangle[2]['y'], triangle[2]['z']])        

    # Compute unit normal
    v1 = p2 - p1
    v2 = p3 - p1
    normal = np.cross(v1, v2)
    normal /= np.linalg.norm(normal)
    
    # Translate each marker
    p1 = p1 + MARKER_TRANS * normal
    p2 = p2 + MARKER_TRANS * normal
    p3 = p3 + MARKER_TRANS * normal
    
    triangle[0]={'x': p1[0], 'y': p1[1], 'z': p1[2]}
    triangle[1]={'x': p2[0], 'y': p2[1], 'z': p2[2]}
    triangle[2]={'x': p3[0], 'y': p3[1], 'z': p3[2]}
    
    return triangle

def extract_triangles(raw_data, obstacle: str, triangles_markers: list[list[str]]):
    keys = set([e for tr_list in triangles_markers for e in tr_list])
    marker_data = {}
    
    # We take the median position of each marker to clear any jitter
    for key, axis in product(keys, ['X', 'Y', 'Z']):
        existing_data = [float(val) for val in raw_data[f"{obstacle}:{key}_{axis}"] if val]
        marker_data[f"{key}_{axis}"] = median(existing_data)
    # Get marker positions for each marker in each triangle
    triangles = []
    for tr in triangles_markers:
        single_tr = []
        for marker in tr:
            point = {}
            for axis, out_axis in zip(['X', 'Y', 'Z'], ['x', 'y', 'z']):
                point[out_axis] = marker_data[f"{marker}_{axis}"]
            single_tr.append(point)
        triangles.append(single_tr)
    # Translate markers by half of their width, so that points are at their bottom (on the surface)
    triangles = [translate_triangle(tr) for tr in triangles]
    
    return triangles