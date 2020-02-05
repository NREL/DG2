from PyPVtoolkit.dashboard.Tab2.Components import VoltageDistance as VD
from PyPVtoolkit.dashboard.Tab2.Components import VoltageLoading as VL
from PyPVtoolkit.dashboard.Tab2.Components import NetworkAnalysis as NA
from PyPVtoolkit.dashboard.Tab2.Components import JointDistribution as JD
from PyPVtoolkit.dashboard.Tab2.Components import Settings as SS
from bokeh.layouts import row, column

class Create():
    def __init__(self):
        self.Settings = SS.Create()
        LineSliders = self.Settings.GetLineSliders()
        self.VDplot = VD.Create(LineSliders)
        self.VLplots = VL.Create(LineSliders)
        self.NAlayout = NA.Create(LineSliders)
        self.ProbLayout = JD.Create(LineSliders)
        C1 = column(self.Settings.layout(), self.VDplot.layout(), self.VLplots.layout())
        C2 = column(self.NAlayout.layout(), self.ProbLayout.layout())
        self.final_layout = row(C1, C2)
        return

    def layout(self):
        return self.final_layout

    def LoadDSSproject(self):
        return