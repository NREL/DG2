from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

class Create():
    def __init__(self):
        self.PlotData = {
            'P': [0],
            'Q': [0]
        }
        self.Source = ColumnDataSource(self.PlotData)
        self.Plot = figure(plot_width=566, plot_height=566, title="Active power / Reactive power plot")
        self.Plot.toolbar.logo = None
        self.Plot.xaxis.axis_label = 'Reactive power [kvar]'
        self.Plot.yaxis.axis_label = 'Active power [kW]'
        self.Plot.scatter(x='Q', y='P', source=self.Source, color='blue')
        self.final_layout = self.Plot
        return

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data):
        self.Source.data = Data