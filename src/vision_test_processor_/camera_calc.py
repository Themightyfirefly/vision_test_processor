import numpy as np
from scipy.spatial.transform import Rotation
from vision_test_processor.config import *

def create_frame(
    right: np.ndarray,
    left: np.ndarray,
    top: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Create a right-handed coordinate frame from three points.

    The created frame will have the right marker as origin.
    The y axis is parallel to the vector from right to left marker.
    The z axis is parallel to the vector from the middle of right, left to the top marker.
    The x axis follows the right hand rule considering y and z axis.

    Arguments:
        right: Position in space of the right mocap marker
        left: Position in space of the left mocap marker
        top: Position in space of the top mocap marker

    Returns:
        origin in shape (3,)
        rotation_matrix in shape (3, 3)
    """
    right = np.asarray(right, dtype=float)
    left = np.asarray(left, dtype=float)
    top = np.asarray(top, dtype=float)

    if right.shape != (3,) or left.shape != (3,) or top.shape != (3,):
        raise ValueError("Each point must contain exactly three coordinates.")

    center = (right + left) / 2.0

    # Z axis points from center to top.
    z_axis = top - center
    # Normalize the Z axis vector
    z_length = np.linalg.norm(z_axis)
    if z_length < 1e-12:
        raise ValueError("center and top must not be the same point.")
    z_axis = z_axis / z_length

    # Y points from center to left.
    y_cand = left - center
    # Ensure that the Y axis is orthogonal to the Z axis
    y_axis = y_cand - np.dot(y_cand, z_axis) * z_axis
    # Normalize the Y axis vector
    y_length = np.linalg.norm(y_axis)
    if y_length < 1e-12:
        raise ValueError("center and left must not be the same point.")
    y_axis = y_axis / y_length

    # X is orthogonal to the plane.
    x_axis = np.cross(y_axis, z_axis)
    x_length = np.linalg.norm(x_axis)
    if x_length < 1e-12:
        raise ValueError("center, left, and top must not be collinear.")
    x_axis = x_axis / x_length

    # Recompute Y to guarantee an orthonormal frame
    y_axis = np.cross(z_axis, x_axis)
    y_axis /= np.linalg.norm(y_axis)

    rotation_matrix = np.column_stack((x_axis, y_axis, z_axis))

    return right, rotation_matrix


def local_to_global(
    local_point: np.ndarray,
    origin: np.ndarray,
    rotation_matrix: np.ndarray,
) -> np.ndarray:
    """
    Convert a point from the constructed local frame into global coordinates.
    
    Arguments:
        local_point: Position of the point to be converted.
        origin: Origin of the local frame in global coordinates.
        rotation_matrix: Describing rotation of the local frame in respect of global frame.
    
    Returns:
        The global coordinates
    """
    local_point = np.asarray(local_point, dtype=float)

    if local_point.shape != (3,):
        raise ValueError(
            "The local point must contain exactly three coordinates."
        )

    return origin + rotation_matrix @ local_point


def global_to_local(
    global_point: np.ndarray,
    origin: np.ndarray,
    rotation_matrix: np.ndarray,
) -> np.ndarray:
    """
    Convert a point from global coordinates into the local frame.
    
    Arguments:
        local_point: Position of the point to be converted.
        origin: Origin of the local frame in global coordinates.
        rotation_matrix: Describing rotation of the local frame in respect of global frame.
    
    Returns:
        The local coordinates
    """
    global_point = np.asarray(global_point, dtype=float)

    if global_point.shape != (3,):
        raise ValueError(
            "The global point must contain exactly three coordinates."
        )

    return rotation_matrix.T @ (global_point - origin)

def markers_to_camera(right: list[float], left: list[float], top: list[float]):
    """Calculate the position and rotation of the camera based on the given markers.
    
    It is assumed that an upside down T shape is used as the markerset.
    
    Arguments:
        right: Position of the right marker.
        left: Position of the left marker.
        top: Position of the top marker.
    
    Returns:
        Position of the camera in global space.
        Roll of the camera.
        Pitch of the camera.
        Yaw of the camera.
    """   
    # Calculate the position of the right mocap marker,
    # and the rotation so that x is corresponding to the x axis of the camera (pointing to the front)
    origin, rotation_matrix = create_frame(np.array(right), np.array(left), np.array(top))
    # Apply the translation onto the right marker to get the camera position
    global_point = local_to_global(np.array(CAMERA_TRANSLATION), origin, rotation_matrix)
    roll, pitch, yaw = Rotation.from_matrix(
        rotation_matrix
    ).as_euler("xyz", degrees=False)
    return global_point, roll, pitch, yaw