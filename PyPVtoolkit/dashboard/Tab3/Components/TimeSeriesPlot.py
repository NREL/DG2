from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

class Create():
    def __init__(self):
        self.PlotData = {
            'Pass1' : [0],
            'Pass2' : [0],
            'Pass3' : [0],
            'Time'  : [0]
        }
        self.Source = ColumnDataSource(self.PlotData)
        self.Plot = figure(plot_width=1700, plot_height=500, title="Time series plot")
        self.Plot.toolbar.logo = None
        self.Plot.xaxis.axis_label = 'Time [h]'
        self.Plot.yaxis.axis_label = ''
        self.Plot.line(x='Time', y='Pass1', source=self.Source, color='red', legend='Smart ctrl mode')
        self.Plot.line(x='Time', y='Pass2', source=self.Source, color='blue', legend='Unity PF')
        self.Plot.line(x='Time', y='Pass3', source=self.Source, color='green', legend='PV disabled')
        self.Plot.legend.location = "top_right"
        self.Plot.legend.click_policy = "hide"
        self.final_layout = self.Plot
        return

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data, xLabel, yLabel):
        self.Source.data = Data
        self.Plot.xaxis.axis_label = xLabel
        self.Plot.yaxis.axis_label = yLabel