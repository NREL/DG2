from bokeh.models.widgets import Paragraph, DataTable, Button, TableColumn
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
import datetime

from tkinter import filedialog
from tkinter import Tk

import pandas as pd

class Create():
    LogLevel = 1
    DebugLevelTable = {
        0: 'Debug',
        1: 'Info',
        2: 'Warning',
        3: 'Error',
    }

    def __init__(self):
        textHeaderTable1 = Paragraph(text='Log information')
        self.LogTable = self.createLogTable()
        self.saveLogTable = Button(label="Export data", button_type="danger")
        self.final_layout = column(textHeaderTable1, self.LogTable, self.saveLogTable)
        self.saveLogTable.on_click(self.ExportTableToCSV)
        return

    def createLogTable(self):
        self.VCdata = {
            'Time'         : [],
            'Level'       : [],
            'Information' : [],
        }
        self.LogSource = ColumnDataSource(self.VCdata)
        cols = []
        Widths = [150,80,800]
        for i, key in enumerate(self.VCdata):
            cols.append(TableColumn(field=key, title=key, width=Widths[i]))
        VCTable = DataTable(source=self.LogSource, columns=cols, width=1125, height=200)

        return VCTable

    def SetLoggingLevel(self, Level):
        self.LogLevel = Level
        return

    def Log(self, DebugLevel, LogText):
        if DebugLevel >=self.LogLevel:
            self.VCdata['Time'].append(str(datetime.datetime.now()))
            self.VCdata['Level'].append(self.DebugLevelTable[DebugLevel])
            self.VCdata['Information'].append(LogText)
            self.LogSource.data =  self.VCdata
        return

    def layout(self):
        return self.final_layout


    def ExportTableToCSV(self):
        root = Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        root.filename = filedialog.asksaveasfilename(initialdir=r"C:/Users/alatif/Desktop/A201202",
                                                   title="Save data table",
                                                   filetypes=(("Text file", "*.txt"),))
        if root.filename:
            Data = self.LogTable.source.data
            Data = pd.DataFrame(Data)
            print(Data)
            Data = Data[['Time', 'Level', 'Information']]
            print(Data)
            Data.to_csv(root.filename, sep=' ', header=False, index=False)
        root.quit()


