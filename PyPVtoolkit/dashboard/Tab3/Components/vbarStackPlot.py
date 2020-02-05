from bokeh.models import ColumnDataSource, ranges
from bokeh.plotting import figure
import numpy as np
class Create():
    def __init__(self, W, H, YaxisLabel, L1, L2, ZeroBase = False):
        self.Source = ColumnDataSource(dict(x=['Smart', 'Unity', 'Disabled'], y=[0, 0, 0], z=[0, 0, 0]))

        self.Plot = figure(plot_width=W, plot_height=H, tools="save", x_range=self.Source.data["x"],
                           y_range=ranges.Range1d(start=0, end=max(self.Source.data["z"]) * 1.2))

        self.Plot.toolbar.logo = None
        # self.Plot.xaxis.axis_label = 'Time [h]'
        self.Plot.yaxis.axis_label = YaxisLabel
        if not ZeroBase:
            self.Plot.vbar(source=self.Source, x='x', top='y', bottom=0, width=0.6, color='blue', alpha=0.5 ,legend = L1)
            self.Plot.vbar(source=self.Source, x='x', top='z', bottom='y', width=0.6, color='red', alpha=0.5,legend = L2)
        else:
            self.Plot.vbar(source=self.Source, x='x', top='z', bottom=0, width=0.6, color='green', alpha=0.5, legend=L1)
            self.Plot.vbar(source=self.Source, x='x', top=0, bottom='y', width=0.6, color='red', alpha=0.5, legend=L2)
        self.final_layout = self.Plot

        return

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data, ZeroBase = False):
        if not ZeroBase:
            DataX = dict(x=['Smart', 'Unity', 'Disabled'], y=Data[0], z=np.add(Data[0], Data[1]))
        else:
            DataX = dict(x=['Smart', 'Unity', 'Disabled'], y=Data[0], z=Data[1])
        self.Source.data = DataX
        self.Plot.y_range.end= max(self.Source.data["z"]) * 1.3