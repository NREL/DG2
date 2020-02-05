from bokeh.models.widgets import Slider, DatePicker, Button, Select
from bokeh.layouts import row, column
from datetime import datetime
class Create():
    def __init__(self):
        dateNow = datetime.now()
        Results = ['Ptotal', 'Qtotal', 'LMP', 'Vmax', 'Vmin', 'PlTotal',
                   'QlTotal', 'Pelm', 'Qelm', 'VelmMax', 'VelmMin', 'SOC']
        self.startDay = DatePicker(title="Start Date", min_date=datetime(2000, 1, 1),
                                   max_date=datetime(2030, 12, 31),
                                   value=datetime(dateNow.year, 1, 2).date() )
        self.endDay = DatePicker(title="End Date", min_date=datetime(2000, 1, 1),
                                   max_date=datetime(2030, 12, 31),
                                   value=datetime(dateNow.year + 1, 1, 1).date())
        self.timeStep = Slider(title="Time step [min]", value=60.0, start=1.0, end=60.0, step=1.0)


        self.Vul = Slider(title="Voltage upper limit [p.u]", value=1.05, start=0.9, end=1.1, step=0.005)
        self.Vll = Slider(title="Voltage lower limit [p.u]", value=0.95, start=0.9, end=1.1, step=0.005)


        self.Class = Select(title="Select class", value="", options=['', 'PVsystem','Storage'])
        self.Element = Select(title="Select element", value="", options=[])
        self.PptyCombo = Select(title="Plot type", value='Ptotal', options=Results)
        self.runSimulation = Button(label="Run simulation", button_type="success")

        r1=row(self.startDay, self.endDay,self.timeStep, self.runSimulation)
        r2 = row(self.Class, self.Element, self.PptyCombo, self.Vll, self.Vul)
        C = column(r1, r2)
        self.final_layout = C
        return

    def getElementName(self):
        return self.Element.value

    def layout(self):
        return self.final_layout

    def UpdatePlot(self):
        return