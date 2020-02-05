from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, ColorBar
import numpy as np
class Create():
    def __init__(self, Sliders):
        self.PDFdata = {
            'height' : [0],
            'width': [0],
            'xValue' : [0],
            'yValue' : [0],
            'Prob'   : [1]
        }
        self.PDFdatasource = ColumnDataSource(self.PDFdata)


        self.color_mapper = LinearColorMapper(palette="Viridis256", low=0, high=1)

        self.PDFplot = figure(plot_width=550, plot_height=450, min_border=10, min_border_left=50,
                             toolbar_location="above", title="Joint PDF")
        self.PDFplot.toolbar.logo = None
        self.PDFplot.xaxis.axis_label = 'Loading [%]'
        self.PDFplot.yaxis.axis_label = 'Voltage [p.u]'

        self.RecPlot = self.PDFplot.rect(x='xValue', y='yValue', width='width', height='height',
                          source=self.PDFdatasource,
                          color={'field': 'Prob', 'transform':  self.color_mapper},
                          line_color=None,
                          hover_line_color='black',
                          hover_color={'field': 'Prob', 'transform':  self.color_mapper})

        self.color_bar = ColorBar(color_mapper= self.color_mapper,
                            label_standoff=12, border_line_color=None, location=(0, 0))
        self.PDFplot.add_layout(self.color_bar, 'right')
        self.final_layout = self.PDFplot
        return

    def layout(self):
        return self.final_layout

    def UpdatePlot(self, Data):
        nBins = 20
        V = Data['Vmax']
        L = Data['Loading']


        H, xedges, yedges = np.histogram2d(np.array(L), np.array(V), bins=nBins)
        H = H.T
        self.color_bar.color_mapper.low = H.min()
        self.color_bar.color_mapper.high =  H.max()
        X, Y = np.meshgrid(xedges, yedges)
        xcenters = (xedges[:-1] + xedges[1:]) / 2
        ycenters = (yedges[:-1] + yedges[1:]) / 2

        X = [0 for x in range(nBins * nBins)]
        Y = [0 for x in range(nBins * nBins)]
        for i, xy in enumerate(zip(xcenters, ycenters)):
            x,y = xy
            for j in range(nBins):
                X[i + j * nBins] = x
                Y[i * nBins + j] = y

        self.PDFdata = {
            'xValue': X,
            'yValue': Y,
            'height': [(max(V) - min(V)) /  nBins] * len(Y),
            'width' : [(max(L) - min(L)) /  nBins] * len(Y),
            'Prob': H.flatten(),
        }
        self.PDFdatasource.data =  self.PDFdata


        return