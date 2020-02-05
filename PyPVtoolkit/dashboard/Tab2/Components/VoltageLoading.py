from bokeh.models import ColumnDataSource, Range1d
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import Spacer
import numpy as np
class Create():
    def __init__(self, Sliders):
        self.Vll, self.Vul, self.Lul = Sliders
        self.LimitsData = {
            'top'     : [],
            'bottom'  : [],
            'left'    : [],
            'right'   : [],
        }

        self.LimitsData2 = {
            'maxV' : [[0, 0]],
            'maxH' : [[0, 0]],
            'Vul'  : [[0, 0]],
            'Vll'  : [[0, 0]],
            'Lul'  : [[0, 0]],
        }

        self.LimitsSource = ColumnDataSource(self.LimitsData)
        self.LimitsSource2 = ColumnDataSource(self.LimitsData2)
        self.plotData = {
            'Name'    : [''],
            'I'       : [0],
            'Imax'    : [0],
            'Vmax'    : [0],
            'Vmin'    : [0],
            'Loading' : [0],
        }
        self.DataSource = ColumnDataSource(self.plotData)
        self.VLplot = figure(plot_width=900, plot_height=900, min_border=10, min_border_left=50,
                             toolbar_location="above", title="Voltage / loading plots",
                             )
        self.VLplot.toolbar.logo = None
        a = self.VLplot.quad(top='top', bottom='bottom', left='left',right='right', fill_alpha=0.4,
                         source=self.LimitsSource, color="white", line_color="#3A5785", line_alpha=0.4)

        self.VI1 =  self.VLplot.circle(x='Loading', y='Vmax', source=self.DataSource,
                                                legend='Maximum voltage', color="red")
        self.VI2 = self.VLplot.circle(x='Loading', y='Vmin', source=self.DataSource,
                                     legend='Minimum voltage', color="pink")

        self.VLplot.legend.location = "top_right"
        self.VLplot.legend.click_policy = "hide"
        self.VLplot.xaxis.axis_label = 'Loading [%]'
        self.VLplot.yaxis.axis_label = 'Voltage [p.u]'

        self.VLplot.background_fill_color = "#fafafa"
        # create the horizontal histogram
        x = self.plotData['Loading']
        hhist, hedges = np.histogram(x, bins=20)
        self.maxHhist = max(hhist) * 1.1

        LINE_ARGS = dict(color="#3A5785", line_color=None)

        self.ph = figure(toolbar_location=None, plot_width=self.VLplot.plot_width, plot_height=260,
                         x_range=self.VLplot.x_range, y_range=(0, self.maxHhist), min_border=10,
                         min_border_left=50, y_axis_location="right")
        self.ph.xgrid.grid_line_color = None
        self.ph.yaxis.major_label_orientation = np.pi / 4
        self.ph.background_fill_color = "#fafafa"

        self.hh0 = self.ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hhist, color="white", line_color="#3A5785")
        Line1 =  self.ph.multi_line(xs='Lul', ys='maxH', source=self.LimitsSource2, color="grey")
       # self.hh1 = self.ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.5, **LINE_ARGS)
       # self.hh2 = self.ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.1, **LINE_ARGS)

        # create the vertical histogram
        y = self.plotData['Vmax']
        vhist, vedges = np.histogram(y, bins=20)
        self.maxVhist = max(vhist) * 1.1

        self.pv = figure(toolbar_location=None, plot_width=260, plot_height=self.VLplot.plot_height,
                         x_range=(0, self.maxVhist), y_range=self.VLplot.y_range,
                         min_border=10, y_axis_location="right")
        self.pv.ygrid.grid_line_color = None
        self.pv.xaxis.major_label_orientation = np.pi / 4
        self.pv.background_fill_color = "#fafafa"

        self.vh0 = self.pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist, color="white", line_color="#3A5785")
        Line1 = self.pv.multi_line(xs='maxV', ys='Vul', source=self.LimitsSource2, color="grey")
        Line1 = self.pv.multi_line(xs='maxV', ys='Vll', source=self.LimitsSource2, color="grey")
        #self.vh1 = self.pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
        #self.vh2 = self.pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

        self.final_layout = column(row(self.VLplot, self.pv), row(self.ph, Spacer(width=260, height=260)))

        return

    def GetPlotData(self):
        return self.plotData

    def UpdateLimits(self):

        self.LimitsData = {
            'top'     : [self.Vul.value],
            'bottom'  : [self.Vll.value],
            'left'    : [0],
            'right'   : [self.Lul.value],
        }

        self.LimitsData2 = {
            'maxV': [[0, self.maxVhist]],
            'maxH': [[0, self.maxHhist]],
            'Vul': [[self.Vul.value, self.Vul.value]],
            'Vll': [[self.Vll.value, self.Vll.value]],
            'Lul': [[self.Lul.value, self.Lul.value]],
        }
        self.LimitsSource.data = self.LimitsData
        self.LimitsSource2.data = self.LimitsData2
        return

    def layout(self):
        return self.final_layout

    def UpdatePlot(self, Data):
        self.plotData = Data
        Data['Loading'] = np.multiply(np.divide(Data['I'],Data['Imax']), 100)
        self.DataSource.data = Data

        x = Data['Loading']
        hhist, hedges = np.histogram(x, bins=20)
        hzeros = np.zeros(len(hedges) - 1)
        self.maxHhist = max(hhist) * 1.1

        self.hh0.data_source.data["left"]  = hedges[:-1]
        self.hh0.data_source.data["right"] = hedges[1:]
        self.hh0.data_source.data["top"]   = hhist

        y = Data['Vmax']
        vhist, vedges = np.histogram(y, bins=20)
        vzeros = np.zeros(len(vedges) - 1)
        self.maxVhist= max(vhist) * 1.1

        self.vh0.data_source.data["bottom"]= vedges[:-1]
        self.vh0.data_source.data["top"]= vedges[1:]
        self.vh0.data_source.data["right"]= vhist

        self.ph.x_range = self.VLplot.x_range
        self.ph.y_range.start  = 0
        self.ph.y_range.start = self.maxHhist

        self.pv.y_range = self.VLplot.y_range
        self.pv.x_range.start = 0
        self.pv.x_range.end = self.maxVhist

        #self.DataSource.data = self.DataSource.data
        self.UpdateLimits()
        return