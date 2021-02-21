import pandas as pd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from matplotlib.cm import get_cmap
import json


def project(longitude, latitude):
    x_tile = (longitude + 180.0) / 360.0
    lat_rad = np.radians(latitude)
    y_tile = (1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0
    return x_tile, y_tile


def opacity(x, c=100, b=1):
    return np.clip(-1 / (c * x + 1) + b, 0, None)


def get_base_map(edges, zoom=12, dpi=600, t=None):
    tilemapbase.start_logging()
    tilemapbase.init(create=True)
    if not t:
        t = tilemapbase.tiles.Carto_Light_No_Labels
    extent = tilemapbase.Extent.from_lonlat(edges["west"], edges["east"], edges["south"], edges["north"])
    fig, ax = plt.subplots(dpi=dpi)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plotter = tilemapbase.Plotter(extent, t, zoom=zoom)
    plotter.plot(ax, t)
    return ax, extent


def load_json(filename, edges):
    with open(filename) as f:
        df = pd.DataFrame(json.load(f)["locations"])
    df = df[["latitudeE7", "longitudeE7"]]
    df["latitudeE7"] = df["latitudeE7"].astype(int) / 10 ** 7
    df["longitudeE7"] = df["longitudeE7"].astype(int) / 10 ** 7
    df = df[df["latitudeE7"] <= edges["north"]]
    df = df[df["latitudeE7"] >= edges["south"]]
    df = df[df["longitudeE7"] <= edges["east"]]
    df = df[df["longitudeE7"] >= edges["west"]]
    return df


def plot_heatmap(df, ax, extent, bins=3000, color="viridis", sigma=1, alpha=1):
    x, y = project(df["longitudeE7"], df["latitudeE7"])
    scale = (extent.ymax - extent.ymin) / (extent.xmax - extent.xmin)
    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=(bins, int(bins * scale)))
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    heatmap = gaussian_filter(np.log(heatmap + 1), sigma=sigma)
    heatmap[heatmap == 0] = np.nan
    cm = get_cmap(color) if isinstance(color, str) else get_cmap()
    im = cm(heatmap)
    if isinstance(color, tuple):
        im[heatmap != np.nan] = color
    elif not isinstance(color, str):
        raise Exception("Invalid color: {}".format(color))
    im[:, :, 3] = opacity(heatmap, b=alpha)
    ax.imshow(np.transpose(im, (1, 0, 2)), extent=extent, origin='lower')
