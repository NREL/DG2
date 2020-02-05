from PyPVtoolkit.dashboard.Tab1.Components import SimulationSettings as SS
from PyPVtoolkit.dashboard.Tab1.Components import InverterSettings as IS
from PyPVtoolkit.dashboard.Tab1.Components import StorageSettings as SoS
from PyPVtoolkit.dashboard.Tab1.Components import Topology as TP
from PyPVtoolkit.dashboard.Tab1.Components import LogBox as LB
from bokeh.layouts import row, column
from bokeh.models.widgets import PreText, Panel, Tabs


class Create():
    def __init__(self, opendss_path):

        self.Settings = SS.Create(opendss_path)
        self.InvSettings = IS.Create()
        self.StorageSettings = SoS.Create()

        self.tab1 = Panel(child=self.InvSettings.layout(), title="Inverter settings")
        self.tab2 = Panel(child=self.StorageSettings.layout(), title="Storage settings")
        self.tabs = Tabs(tabs=[self.tab1, self.tab2])

        self.TopologyPlot = TP.Create(self.InvSettings, self.StorageSettings)
        self.LogTable = LB.Create()
        self.final_layout = row(column(self.Settings.layout(),
                                       self.TopologyPlot.layout(),
                                       self.LogTable.layout()),
                                self.tabs)
        return

    def layout(self):
        return self.final_layout

    def LoadDSSproject(self):
        return