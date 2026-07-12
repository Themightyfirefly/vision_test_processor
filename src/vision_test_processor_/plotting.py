import numpy as np
import matplotlib.pyplot as plt
import sys

def plot_heightmap(hmap):
    xs = np.unique(hmap[:, 0])
    ys = np.unique(hmap[:, 1])

    X, Y = np.meshgrid(xs, ys)

    Z = np.full((len(ys), len(xs)), np.nan)

    x_idx = {x: i for i, x in enumerate(xs)}
    y_idx = {y: i for i, y in enumerate(ys)}

    for x, y, z in hmap:
        Z[y_idx[y], x_idx[x]] = z

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')

    plt.show()

if len(sys.argv) < 2:
	print("Script for plotting heightmaps in .npy files that are exported by the vision_analysis node.")
	print("Usage: python plot_heightmap.py <path_to_heightmap.npy>")
	sys.exit(1)
hmap = np.load(f'{sys.argv[1]}')
plot_heightmap(hmap)
