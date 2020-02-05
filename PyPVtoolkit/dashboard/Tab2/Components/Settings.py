from bokeh.models.widgets import Slider, DatePicker, Button
from bokeh.layouts import row, column
from datetime import datetime
class Create():
    def __init__(self):
        dateNow = datetime.now()
        self.startDay = DatePicker(title="Start Date", min_date=datetime(2000, 1, 1),
                                   max_date=datetime(2030, 12, 31),
                                   value=datetime(dateNow.year, dateNow.month, dateNow.day))

        # snapshot time hours minutes
        self.Hour = Slider(title="Time of day [h]", value=1.0, start=1.0, end=24.0, step=0.25)
        self.timeStep = Slider(title="Time step [min]", value=15.0, start=1.0, end=60.0, step=1.0)
        self.timeStep.on_change('value', self.updateHourSlider)

        r1 = row(self.startDay, self.Hour, self.timeStep)

        self.Vul = Slider(title="Voltage upper limit [p.u]", value=1.05, start=0.9, end=1.1, step=0.005)
        self.Vll = Slider(title="Voltage lower limit [p.u]", value=0.95, start=0.9, end=1.1, step=0.005)
        self.Lul = Slider(title="Loading upper limit [%]", value=90, start=0, end=120, step=1)

        r2 = row(self.Vll, self.Vul, self.Lul)
        self.final_layout = column(r1, r2)
        return

    def GetLineSliders(self):
        return self.Vll, self.Vul, self.Lul

    def layout(self):
        return self.final_layout

    def updateHourSlider(self, attr, old, new):
        self.Hour.step = self.timeStep.value / 60
        return

    def UpdatePlot(self):
        return