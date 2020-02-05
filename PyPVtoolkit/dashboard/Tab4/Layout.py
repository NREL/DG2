from PyPVtoolkit.dashboard.Tab4.Components import Settings as SS
from PyPVtoolkit.dashboard.Tab4.Components import PVplot
from PyPVtoolkit.dashboard.Tab4.Components import QVplot
from PyPVtoolkit.dashboard.Tab4.Components import PQplot
from PyPVtoolkit.dashboard.Tab4.Components import PFplot
from PyPVtoolkit.dashboard.Tab4.Components import Pplot
from PyPVtoolkit.dashboard.Tab4.Components import Qplot
from PyPVtoolkit.dashboard.Tab4.Components import Vplot
from bokeh.layouts import row, column
class Create():
    def __init__(self):
        self.Settings = SS.Create()

        self.plotPF = PFplot.Create()
        self.plotP = Pplot.Create()
        self.plotQ = Qplot.Create()
        self.plotV = Vplot.Create()

        self.plotPV = PVplot.Create()
        self.plotQV = QVplot.Create()
        self.plotPQ = PQplot.Create()

        r0 = self.Settings.layout()
        r1 = row(self.plotP.layout(), self.plotQ.layout())
        r2 = row(self.plotV.layout(), self.plotPF.layout())
        r3 = row(self.plotPV.layout(), self.plotQV.layout(), self.plotPQ.layout())
        self.final_layout = column(r0, r1, r2, r3)
        return

    def layout(self):
        return self.final_layout

