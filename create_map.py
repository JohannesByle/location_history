from basic_functions import *
import pandas as pd
from matplotlib.cm import get_cmap
import os
from tqdm import tqdm

os.chdir(os.path.dirname(__file__))
if not os.path.exists("maps"):
    os.mkdir("maps")


def create_map_from_filenames(filenames, colors, edges, zoom=12, dpi=600, t=None, bins=3000, sigma=1, alpha=1):
    """
    :param filenames: List of filenames, either list of strings or list of list of strings
    :param colors: Colors for each heatmap, either a list of matplotlib colormap strings, a list of tuples, a tuple, or
    a matplotlib colormap string. A list of colormap options can be found here
    https://matplotlib.org/stable/gallery/color/colormap_reference.html
    :param edges: Edges of map, must have form {"north": float, "south": float,"east": float,"west": float}
    :param zoom: Zoom level of map, default 12
    :param dpi: Dots-per-inch, default 6000
    :param t: Type of basemap from tilemapbase.tiles, either from Carto or Stamen, default Carto_Light_No_Labels
    :param bins: Number of bins in heatmap, i.e. how detailed the heatmap is, default 3000
    :param sigma: How much smoothing is applied to the heatmap, default is 1
    :param alpha: Transparency of each heatmap layer, default 1
    """
    if isinstance(colors, list):
        assert len(colors) == len(filenames)
    assert all([isinstance(n, type(filenames[0])) for n in filenames])
    ax, extent = get_base_map(edges, zoom=zoom, dpi=dpi, t=t)
    dfs = []
    for filename in tqdm(filenames, desc="Loading data"):
        if isinstance(filename, str):
            dfs.append(load_json(filename, edges))
        elif isinstance(filename, list):
            dfs.append(pd.concat([load_json(n, edges) for n in filename]))
        else:
            raise Exception("Unknown filename: {}".format(filename))
    for n in tqdm(range(len(dfs)), desc="Generating map"):
        if isinstance(colors, list):
            color = colors[n]
        elif isinstance(colors, tuple):
            color = colors
        elif isinstance(colors, str):
            cm = get_cmap(colors)
            color = cm(n / (len(dfs) - 1 if len(dfs) > 1 else 1))
        else:
            raise Exception("Unknown colors: {}".format(colors))
        plot_heatmap(dfs[n], ax, extent, bins=bins, sigma=sigma, color=color, alpha=alpha)
    saved = False
    n = 0
    while not saved:
        save_filename = "maps/map_{}.png".format(n)
        if not os.path.exists(save_filename):
            plt.savefig(save_filename)
            saved = True
        n += 1
