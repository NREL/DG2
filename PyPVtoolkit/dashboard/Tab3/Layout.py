from PyPVtoolkit.dashboard.Tab3.Components import TimeSeriesPlot as TSP
from PyPVtoolkit.dashboard.Tab3.Components import Settings as SS
from PyPVtoolkit.dashboard.Tab3.Components import CurtailmentPlot as CP
from PyPVtoolkit.dashboard.Tab3.Components import EnergyPlot as EP
from PyPVtoolkit.dashboard.Tab3.Components import BoxPlot as BP
from PyPVtoolkit.dashboard.Tab3.Components import LossPlot as LP
from PyPVtoolkit.dashboard.Tab3.Components import vbarStackPlot as VP

from bokeh.models.widgets import Select, Slider
from bokeh.layouts import row, column

class Create():

    def __init__(self):

        self.Settings = SS.Create()
        self.TimePlot = TSP.Create()
        self.BoxPlot = BP.Create()
        r1 = row(self.TimePlot.layout())


        self.BarP1 = EP.Create(258,500)
        self.BarP2 = CP.Create(208,500)
        self.BarP3 = LP.Create(308,500, 'Total system losses [kWh]')
        self.BarP3p = VP.Create(308, 500, 'Active power flow [MWh]',
                               'Forward direction', 'Reverse direction', True)
        self.BarP3q = VP.Create(308, 500, 'Reactive power flow [Mvar]',
                               'Forward direction', 'Reverse direction', True)
        self.BarP4 = VP.Create(425,500, 'Voltage violations frequency (system wide)',
                               'LB voltage violations', 'UB voltage violations')
        self.BarP5 = VP.Create(425,500, 'Voltage violations duration [h] (system wide)',
                               'LB voltage violations', 'UB voltage violations')
        self.BarP6 = VP.Create(425,500, 'Voltage violations frequency (PV node)',
                               'LB voltage violations', 'UB voltage violations')
        self.BarP7 = VP.Create(425,500, 'Voltage violations duration [h] (PV node)',
                               'LB voltage violations', 'UB voltage violations')






        r2 = row(self.BoxPlot.layout(),
                 self.BarP3p.layout(),
                 self.BarP3q.layout(),
                 self.BarP1.layout(),
                 self.BarP2.layout(),
                 self.BarP3.layout())

        r3 = row(self.BarP4.layout(), self.BarP5.layout(), self.BarP6.layout(), self.BarP7.layout())
        c1 = column(self.Settings.layout(), r1, r2, r3)
        self.final_layout = c1
        return

    def layout(self):
        return self.final_layout

