from bokeh.models.widgets import Slider, DatePicker, Button, Select
from bokeh.layouts import row, column
from datetime import datetime
class Create():
    def __init__(self):
        dateNow = datetime.now()
        self.startDay = DatePicker(title="Start Date", min_date=datetime(2000, 1, 1),
                                   max_date=datetime(2030, 12, 31),
                                   value=datetime(dateNow.year, dateNow.month, dateNow.day))
        self.endDay = DatePicker(title="End Date", min_date=datetime(2000, 1, 1),
                                   max_date=datetime(2030, 12, 31),
                                   value=datetime(dateNow.year, dateNow.month, dateNow.day))
        # snapshot time hours minutes
        self.timeStep = Slider(title="Time step [min]", value=15.0, start=1.0, end=60.0, step=1.0)
        self.PVsystem = Select(title="Select PV system", value="", options=[])
        self.runSimulation = Button(label="Run simulation", button_type="success")
        r1 = row(self.startDay, self.endDay, self.timeStep, self.PVsystem, self.runSimulation)

        self.final_layout = r1
        return


    def getPVname(self):
        return self.PVsystem.value

    def layout(self):
        return self.final_layout



    def UpdatePlot(self):
        return