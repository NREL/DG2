from PyPVtoolkit.dashboard.Tab1 import Layout as LayoutTab1
from PyPVtoolkit.dashboard.Tab2 import Layout as LayoutTab2
from PyPVtoolkit.dashboard.Tab3 import Layout as LayoutTab3
from PyPVtoolkit.dashboard.Tab4 import Layout as LayoutTab4
from bokeh.models.widgets import Panel, Tabs, Button
from bokeh.layouts import column, row
from bokeh.plotting import figure

class Create():
    def __init__(self, doc, opendss_path):
        self.layout1 = LayoutTab1.Create(opendss_path)
        self.tab1 = Panel(child=self.layout1.layout(), title="Network settings")
        self.layout2 = LayoutTab2.Create()
        self.tab2 = Panel(child=self.layout2.layout(), title="Snapshot analysis")
        self.layout3 = LayoutTab3.Create()
        self.tab3 = Panel(child=self.layout3.layout(), title="Time-series analysis")
        # self.layout4 = LayoutTab4.Create()
        # self.tab4 = Panel(child=self.layout4.layout(), title="PV System analysis")

        # Push to server
        tabs = Tabs(tabs=[self.tab1, self.tab2, self.tab3])#, , self.tab4])
        tabs.width = 1700
        self.layout = tabs
        doc.add_root(self.layout)
        doc.title = "Distributed Generation for Distribution Grids - (DG)²"
        return



    def Layout(self):
        return self.layout