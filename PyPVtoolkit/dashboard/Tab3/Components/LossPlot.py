from bokeh.models import ColumnDataSource, ranges
from bokeh.plotting import figure

class Create():
    def __init__(self , W, H, YaxisLabel):
        Curtailment = 1
        self.source = ColumnDataSource(dict(x=['Smart', 'Unity', 'Disabled'], y=[0,0, 0], c =['red', 'blue', 'green']))

        self.Plot = figure(plot_width=W, plot_height=H, tools="save", x_range=self.source.data["x"],
                           y_range=ranges.Range1d(start=0, end=max(self.source.data["y"]) * 1.2))

        self.Plot.toolbar.logo = None
        # self.Plot.xaxis.axis_label = 'Time [h]'
        self.Plot.yaxis.axis_label = YaxisLabel

        self.Plot.vbar(source=self.source, x='x', top='y', bottom=0, width=0.6, color='c', alpha=0.5)
        self.final_layout = self.Plot
        return

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data):
        DataX = dict(x=['Smart', 'Unity', 'Disabled'], y=Data, c=['red', 'blue', 'green'])
        self.source.data = DataX
        self.Plot.y_range.end = max(self.source.data["y"]) * 1.2
