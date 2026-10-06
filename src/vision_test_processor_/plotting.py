import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import json
from pathlib import Path

def plot_system_diagnostics(bag_path: Path):
    """Plot the recorded system diagnostics.
    
    Arguments:
        bag_path: Bag which includes the to be plotted data.
    """
    with open(bag_path / 'results/system_diagnostics.json', 'r') as f:
        diag = json.load(f)

    plt.plot(diag["time"], diag["cpu"])
    plt.ylim(0, 100)
    plt.xlabel("time in s")
    plt.ylabel("cpu usage in %")
    plt.show()

def plot_heightmap(bag_path: Path, corrected = False):
    """Plot the recorded heightmap.
    
    Arguments:
        bag_path: Bag which includes the to be plotted data.
        corrected: Whether to use the corrected heightmap data (accounting for odom error).
    """
    plt.rcParams.update({'font.size': 18})
    filename = 'heightmap_corrected' if corrected else 'heightmap'
    hmap = np.load(bag_path / f'results/{filename}.npy', allow_pickle=True)

    filter = True
    if filter:
        mask = (
            (hmap[:, 0] >= -1.5) & (hmap[:, 0] <= -1) &
            (hmap[:, 1] >= -0.4) & (hmap[:, 1] <= 0.8)
        )
        hmap = hmap[mask]
    
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
        vmax=5, # used to be np.nanmax(valid_errors),
    )
    facecolors = cmap(norm(Error))
    facecolors[np.isnan(Error)] = (0, 0, 1, 1)
    
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot_surface(X, Y, Z, facecolors=facecolors, linewidth=0.15, edgecolor="k", antialiased=True)
    
    if not filter:
        ax.set_xlabel('X in m', labelpad=30)
        ax.set_ylabel('Y in m', labelpad=10)
        ax.set_zlabel('Height in m', labelpad=12)
        ax.tick_params(axis='x', pad=10)
        ax.set_xticks(np.arange(-2.5, 0, 0.5))
        ax.tick_params(axis='y', pad=0)
        ax.set_yticks(np.arange(-0.6, 0.8, 0.4))
        ax.set_zticks(np.arange(-0.0, 0.8, 0.2))
    else:
        ax.tick_params(axis='x', pad=20)
        ax.set_xlabel('X in m', labelpad=40)
        ax.set_ylabel('Y in m', labelpad=40)
        ax.set_xticks(np.arange(-1.5, -1, 0.1))
        ax.set_yticks(np.arange(-0.5, 0.8, 0.4))
        ax.set_zticklabels([])

    # Add colorbar explaining the error colors
    color_mapping = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    color_mapping.set_array([])
    cb = fig.colorbar(color_mapping, ax=ax, label="Error in mm", shrink=0.7, pad=0.1, orientation="horizontal")
    cb.ax.tick_params(labelsize=20)
    cb.set_label("Error in mm", fontsize=20)

    # Matching axes to look realistic
    ax.set_box_aspect((
        np.ptp(xs),
        np.ptp(ys),
        np.ptp(Z[np.isfinite(Z)])
    ))
    if not filter:
        ax.view_init(elev=24, azim=154)
    else:
        ax.view_init(elev=90, azim=180)

    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.show()

def plot_odom(bag_path: Path):
    """Plot the recorded odom error.
    
    Arguments:
        bag_path: Bag which includes the to be plotted data.
    """
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

def plot_odom_raw(bag_path: Path):
    """Plot the recorded ground truth and calculated odom.
    
    Arguments:
        bag_path: Bag which includes the to be plotted data.
    """
    with open(bag_path / 'results/odom_raw_rec.json', 'r') as f:
        odom_rec = json.load(f)
    with open(bag_path / 'results/odom_raw_truth.json', 'r') as f:
        odom_truth = json.load(f)
        
    _, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    
    keys = [
        k_rec for k_rec in odom_rec.keys() for k_truth in odom_truth.keys() 
        if k_rec == k_truth and k_rec != 'time'
    ]
    y_lables = ['position in mm']*3 + ['rotation in rad']*3
    for ax, key, y_lable in zip(axes.flat, keys, y_lables):
        ax.plot(odom_rec['time'], odom_rec[key], label='recording')
        ax.plot(odom_truth['time'], odom_truth[key], label='truth')
        ax.set_title(key)
        ax.set_xlabel("time in s")
        ax.set_ylabel(y_lable)
        ax.legend()
        ax.grid(True)
        
    plt.show()