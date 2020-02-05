from bokeh.models import ColumnDataSource, ranges
from bokeh.plotting import figure
import pandas as pd
class Create():
    def __init__(self):
        self.PlotData = {
            'Pass1' : [0,2,6,4],
            'Pass2' : [0,14,79,1],
            'Pass3' : [0,54,5,46],
        }

        Quarts = self.calculateQuarts(self.PlotData)
        self.Source = ColumnDataSource(Quarts)
        Range = max(self.Source.data["max"]) - min(self.Source.data["min"])
        Ymax = max(self.Source.data["max"]) + 0.1 * Range
        Ymin = min(self.Source.data["min"]) - 0.1 * Range
        self.Plot = figure(plot_width=300, plot_height=500, title="Box plot", x_range=self.Source.data["Columns"],
                           y_range=ranges.Range1d(start= Ymin,  end  = Ymax))

        self.Plot.vbar(source = self.Source, x = 'Columns', top = 'Q1', bottom = 'Q2',width=0.6,
                       fill_color='c', fill_alpha=0.5, line_color='black')
        self.Plot.vbar(source = self.Source, x = 'Columns', top = 'Q2', bottom = 'Q3',width=0.6,
                       fill_color='c', fill_alpha=0.5, line_color='black')
        self.Plot.vbar(source=self.Source, x='Columns', top='max', bottom='Q3', width=0.01,
                       line_color='black')
        self.Plot.vbar(source=self.Source, x='Columns', top='Q1', bottom='min', width=0.01,
                       line_color='black')
        self.Plot.vbar(source=self.Source, x='Columns', top='max', bottom='max', width=0.3,
                       line_color='black')
        self.Plot.vbar(source=self.Source, x='Columns', top='min', bottom='min', width=0.3,
                       line_color='black')

        self.Plot.toolbar.logo = None
        self.Plot.xaxis.axis_label = 'Scenario'
        self.Plot.yaxis.axis_label = ''

        self.Plot.legend.location = "top_right"
        self.Plot.legend.click_policy = "hide"
        self.final_layout = self.Plot
        return


    def calculateQuarts(self, Data):
        data = pd.DataFrame(Data)
        q75 = data.quantile(q=0.75)
        q50 = data.quantile(q=0.50)
        q25 = data.quantile(q=0.25)
        Quarts = {
            'Columns': ['Smart', 'Unity', 'Disabled'],
            'Q1': q25,
            'Q2': q50,
            'Q3': q75,
            'max': data.max(),
            'min': data.min(),
            'Range': [data.min().min(), 0, data.max().max()],
            'c': ['red', 'blue', 'green']
        }
        return Quarts

    def layout(self):
        return self.final_layout

    def updatePlot(self, Data, yLabel):
        Quarts = self.calculateQuarts(Data)
        self.Source.data = Quarts
        Range = max(self.Source.data["max"]) - min(self.Source.data["min"])
        Ymax = max(self.Source.data["max"]) + 0.1 * Range
        Ymin = min(self.Source.data["min"]) - 0.1 * Range
        self.Plot.y_range.start = Ymin
        self.Plot.y_range.end = Ymax
        self.Plot.yaxis.axis_label = yLabel