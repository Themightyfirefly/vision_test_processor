import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import json

def plot_system_diagnostics(bag_path: Path):
    with open(bag_path / 'results/system_diagnostics.json', 'r') as f:
        diag = json.load(f)

    plt.plot(diag["time"], diag["cpu"])
    plt.ylim(0, 100)
    plt.xlabel("time in s")
    plt.ylabel("cpu usage in %")
    plt.show()

def plot_heightmap(bag_path: Path):
    hmap = np.load(bag_path / 'results/heightmap.npy', allow_pickle=True)
    
    xs = np.unique(hmap[:, 0])
    ys = np.unique(hmap[:, 1])

    X, Y = np.meshgrid(xs, ys)

    Z = np.full((len(ys), len(xs)), np.nan)
    Error = np.full((len(ys), len(xs)), np.nan)
    
    x_idx = {x: i for i, x in enumerate(xs)}
    y_idx = {y: i for i, y in enumerate(ys)}

    for x, y, z, err in hmap:
        Z[y_idx[y], x_idx[x]] = z
        Error[y_idx[y], x_idx[x]] = err
    
    # Low error = green, high error = red
    cmap = plt.colormaps["RdYlGn_r"]
    #cmap.set_bad(color="blue")
    valid_errors = Error[np.isfinite(Error)]
    if valid_errors.size == 0:
        raise ValueError("No valid error values found.")
    norm = colors.Normalize(
        vmin=0,
        vmax=np.max(valid_errors),
    )
    facecolors = cmap(norm(Error))
    facecolors[np.isnan(Error)] = (0, 0, 1, 1)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z, facecolors=facecolors, linewidth=0.15, edgecolor="k", antialiased=True,) #, facecolors=facecolors
    ax.set_xlabel('X in m')
    ax.set_ylabel('Y in m')
    ax.set_zlabel('Height in m')

    # Add colorbar explaining the error colors
    color_mapping = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    color_mapping.set_array([])
    fig.colorbar(color_mapping, ax=ax, label="Error in mm", shrink=0.7, pad=0.1)

    # Matching axes to look realistic
    ax.set_box_aspect((
        np.ptp(xs),
        np.ptp(ys),
        np.ptp(Z[np.isfinite(Z)])
    ))
    ax.view_init(elev=35, azim=-60)
    
    plt.show()

def plot_odom(bag_path):
    with open(bag_path / 'results/odom_errors.json', 'r') as f:
        odom = json.load(f)
        
    _, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    
    keys = [k for k in odom.keys() if k != 'time']
    y_lables = ['error in mm']*3 + ['error in rad']*3
    for ax, key, y_lable in zip(axes.flat, keys, y_lables):
        ax.plot(odom['time'], odom[key])
        ax.set_title(key)
        ax.set_xlabel("time in s")
        ax.set_ylabel(y_lable)
        ax.grid(True)
        
    plt.show()