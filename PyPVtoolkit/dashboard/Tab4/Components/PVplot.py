from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

class Create():
    def __init__(self):
        self.PlotData = {
            'P': [0],
            'V': [0]
        }
        self.Source = ColumnDataSource(self.PlotData)
        self.Plot = figure(plot_width=566, plot_height=566, title="Active power / Voltage plot")
        self.Plot.toolbar.logo = None
        self.Plot.xaxis.axis_label = 'Voltage [p.u]'
        self.Plot.yaxis.axis_label = 'Active power [kW]'
        self.Plot.scatter(x='V', y='P', source=self.Source, color='blue')
        self.final_layout = self.Plot
        return

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data):
        self.Source.data = Data