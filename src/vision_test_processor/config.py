# Main frequency of the mocap system (could be either cameras or pressure plates, depending on which is higher)
# SYSTEM_FREQUENCY = 1000
# Frequency of the cameras in the mocap system
MOCAP_FREQUENCY = 1000

DELIMITER = ';'

# Prefixes for csv headers
CAMERA = 'Realsense_Camera'
HIGHSTEP = 'cybathlon_highstep'
# Marker names
LEFT = 'left'
RIGHT = 'right'
TOP = 'top'

HIGHSTEP_TRIANGLES = [['top_front_left', 'top_front_right', 'top_back_left'], ['top_front_right', 'top_back_left', 'top_back_right']]

# Translation for each marker (distance center to base) in mm
MARKER_TRANS = 1

# Distance shown around the triangles in mm
TEST_AREA_PADDING_X = 1000
TEST_AREA_PADDING_Y = 300

# Translation in x, y, z from the right marker to the camera origin in cm (following the cameras axes)
# A visualisation for the axes: https://github.com/realsenseai/realsense-ros#ros2robot-vs-opticalcamera-coordination-systems
CAMERA_TRANSLATION = [0.0, 0.0, 0.0]