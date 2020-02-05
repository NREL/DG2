from bokeh.models.widgets import DataTable, TableColumn, Paragraph, Button
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
import pandas as pd
import numpy as np
from tkinter import filedialog
from tkinter import Tk
class Create():
    def __init__(self, Sliders):
        self.Vll, self.Vul, self.Lul = Sliders

        textHeaderTable1 = Paragraph(text='Network Overview')
        self.OverviewTable = self.createOverviewTable()
        self.saveOverview = Button(label="Export data", button_type="danger")
        textHeaderTable2 = Paragraph(text='Voltage Constraint Elements')
        self.VCTable = self.createVCTable()
        self.saveVCTable = Button(label="Export data", button_type="danger")
        textHeaderTable3 = Paragraph(text='Current Constraint Elements')
        self.CCTable = self.createCCTable()
        self.saveCCTable = Button(label="Export data", button_type="danger")
        L1 = column(textHeaderTable1, self.OverviewTable, self.saveOverview)
        L2 = column(textHeaderTable2, self.VCTable, self.saveVCTable)
        L3 = column(textHeaderTable3, self.CCTable, self.saveCCTable)

        self.saveOverview.on_click(self.ExportOverview)
        self.saveVCTable.on_click(self.ExportVCTable)
        self.saveCCTable.on_click(self.ExportCCTable)

        self.final_layout = column(L1, L2, L3)
        return

    def ExportOverview(self):
        self.ExportTabletoCSV(self.OverviewTable)

    def ExportVCTable(self):
        self.ExportTabletoCSV(self.VCTable)

    def ExportCCTable(self):
        self.ExportTabletoCSV(self.CCTable)

    def ExportTabletoCSV(self, Table):
        root = Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        root.filename = filedialog.asksaveasfilename(initialdir=r"C:/Users/alatif/Desktop/A201202",
                                                   title="Save data table",
                                                   filetypes=(("CSV file (comma seperated)", "*.csv"),))
        if root.filename:
            Data = Table.source.data
            Data = pd.DataFrame(Data)
            Data.to_csv(root.filename, sep=',')
        root.quit()

    def createVCTable(self):
        self.VCdata = {
            'Class'         : [],
            'Element'       : [],
            'Voltage [p.u]' : [],
        }
        self.CVsource = ColumnDataSource(self.VCdata)
        cols = []
        for key in self.VCdata:
            cols.append(TableColumn(field=key, title=key))
        VCTable = DataTable(source=self.CVsource, columns=cols, width=500, height=310)

        return VCTable

    def createCCTable(self):
        self.CCdata = {
            'Class'       : [],
            'Element'     : [],
            'Loading [%]' : [],
        }
        self.CCsource = ColumnDataSource(self.CCdata)
        cols = []
        for key in self.CCdata:
            cols.append(TableColumn(field=key, title=key))
        CCTable = DataTable(source=self.CCsource, columns=cols, width=500, height=310)
        return CCTable

    def createOverviewTable(self):
        self.Overview = {
            '' : [
            'Number of loads',
            'Number of PV systems',
            'Number of Buses',
            'Number of Islands',
            'Number of Loops',
            'Feeder length',
            'Minimum voltage',
            'Maximum voltage',
            'Total active power',
            'Total reactive power',
            'Total losses (active)',
            'Total losses (reactive)',
            'Percentage losses',
            'Line losses (active)',
            'Line loses (reactive)',
            ],
            'Value' : [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
            'Units' : ['','','','','', 'mi','p.u','p.u','MW','Mvar','kW','kvar','%','kW','kvar'],
        }
        self.OVsource = ColumnDataSource(self.Overview)
        cols = []
        for key in self.Overview:
            cols.append(TableColumn(field=key, title=key))
        OverviewTable = DataTable(source=self.OVsource, columns=cols, width=500, height=400)
        return OverviewTable

    def UpdateOverviewTable(self, dssGraph):
        g = dssGraph.graph

        self.Overview['Value'] = [
            g['nLoads'],
            g['nPVsystems'],
            g['nBuses'],
            g['nIslands'],
            g['nLoops'],
            g['Length'],
            g['Vmin'],
            g['Vmax'],
            g['Ptotal'],
            g['Qtotal'],
            g['Ploss'],
            g['Qloss'],
            g['% Loss'],
            g['PlossLine'],
            g['QlossLine'],
            ]
        self.OVsource.data['Value'] = self.Overview['Value']
        return

    def UpdateVoltageViolationTable(self, Data):
        rData = pd.DataFrame(Data)
        rData = rData[['Class' ,'Name' ,'Vmax', 'Vmin', 'I', 'Imax']]
        rData = rData[(rData['Vmax'] > self.Vul.value) |
                      (rData['Vmin'] < self.Vll.value)]

        self.VCdata['Class'] = list(rData['Class'])
        self.VCdata['Element'] = list(rData['Name'])
        self.VCdata['Voltage [p.u]'] = list(
            np.where(rData['Vmax'] > self.Vul.value, rData['Vmax'],
                     np.where(rData['Vmin'] < self.Vll.value, rData['Vmin'], 0)))
        self.CVsource.data = self.VCdata
        return

    def UpdateLoadingViolationTable(self, Data):
        rData = pd.DataFrame(Data)
        rData = rData[['Class', 'Name', 'Vmax', 'Vmin', 'I', 'Imax']]
        rData['loading'] = rData['I'] / rData['Imax'] * 100
        rData = rData[(rData['loading'] > self.Lul.value)]

        self.CCdata['Class'] = list(rData['Class'])
        self.CCdata['Element'] = list(rData['Name'])
        self.CCdata['Loading [%]'] = list(rData['loading'])
        self.CCsource.data = self.CCdata
        return

    def layout(self):
        return self.final_layout
