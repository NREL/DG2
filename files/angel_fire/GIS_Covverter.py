from bokeh.palettes import Viridis, Plasma
import pandas as pd
import numpy as np


def transform(X, Y):
    source_proj = pyproj.Proj("+init={}".format('EPSG:3857'))  # + )
    target_proj = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    meter_factor = 1#0.3048006096012192
    Xt = []
    Yt = []
    if isinstance(X, list) and isinstance(X, list):
        for x1, y1 in zip(X, Y):
            Ans = pyproj.transform(source_proj, target_proj, float(x1) * meter_factor,
                                   float(y1) * meter_factor)
            #print(x1, y1, ' - ', Ans[0], Ans[1])
            Xt.append(Ans[0])
            Yt.append(Ans[1])
    else:
        Xt, Yt= pyproj.transform(source_proj, target_proj, float(X) * meter_factor,
                                   float(Y) * meter_factor)

    return Xt, Yt



try:
    import pyproj
except ImportError:
    print('Package pyproj not installed. Cannot use GISplot')
    quit()


BusCoordinates = pd.read_csv('Bus_Coordinates.csv', index_col=0, header=None)
BusCoordinates.columns = ['X', 'Y']


BusCoordinates['X'], BusCoordinates['Y'] = transform(BusCoordinates['X'].tolist(),
                                                     BusCoordinates['Y'].tolist())

BusCoordinates.to_csv('Bus_Coordinates_new.csv', header=None)
print(BusCoordinates)
