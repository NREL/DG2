import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource,VeeHead, Arrow, Range1d
from bokeh.models.widgets import Slider, TextInput, Button, Select

class Create():
    def __init__(self):
        self.StrCapabilityPlot = figure(plot_width=580, plot_height=595,
                                     tools='', title="Storage capability curve")

        self.StrCapabilityPlot.xaxis.axis_label = 'Q [p.u]'
        self.StrCapabilityPlot.yaxis.axis_label = 'P [p.u]'
        self.StrCapabilityPlot.toolbar.logo = None
        self.StrCapabilityPlot.toolbar_location = None
        self.StrCapabilityPlot.y_range = Range1d(*(-1.15, 1.15))
        self.StrCapabilityPlot.x_range = Range1d(*(-1.15, 1.15))
        self.StrCapabilityPlot.circle(x=[0], y=[0], radius=1.00, line_color ="navy", fill_color=None, size= 1)
        self.StrCapabilityPlot.add_layout(Arrow(end=VeeHead(size=10), line_color="black",
                                                x_start=0.0, y_start=-1.1, x_end=0, y_end=1.1))
        self.StrCapabilityPlot.add_layout(Arrow(end=VeeHead(size=10), line_color="black",
                                                x_start=-1.1, y_start=0, x_end=1.1, y_end=0))

        self.StoragecurveDatasource  = ColumnDataSource(data=dict(x0=[], x1=[], x2=[], y0=[], y1=[], y2=[]))

        self.StrCapabilityPlot.line('x0', 'y0', source=self.StoragecurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.StrCapabilityPlot.line('x1', 'y1', source=self.StoragecurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.StrCapabilityPlot.line('x2', 'y2', source=self.StoragecurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")

        Storagewidgetbox = self.createStoragewidgetbox()

        PVsettingsLayout = column(self.StrCapabilityPlot, Storagewidgetbox, width=800)
        self.final_layout = PVsettingsLayout

        for w in [self.kWratingSlider, self.PFslider]:
            w.on_change('value', self.updateStoragecurves)

        return

    def CreateStorage(self, pyDSS, NodeData, ProfilePath):
        print(NodeData)
        # Create corresponding PV system
        nPhases = len(self.Dropdown_phases.value)

        switch = {
            'bus1':NodeData['toBus'] + self.toPhase(self.Dropdown_phases.value),
            'bus2': NodeData['toBus'] + '_dummy' + self.toPhase(self.Dropdown_phases.value),
            'switch': 'y',
            'length': '1',
            'units': 'ft',
            'enabled': 'true',
            'phases': nPhases,
        }
        pyDSS.Add_Element('line', self.StoragenameTextbox.value + '_sw', switch)

        Storageproperties = {
            'bus1'           : NodeData['toBus'] + '_dummy' + self.toPhase(self.Dropdown_phases.value),
            'phases'         : nPhases,
            'kv'             : NodeData['kVbase'] if nPhases == 1 else NodeData['kVbase'] * 1.732,
            'kVA'            : float(self.StorageCapacityTextbox.value),
            'kWhrated'       : float(self.StorageCapacityTextbox.value) * float(self.PFslider.value),
            'kWrated'        : float(self.kWratingSlider.value) * float(self.StorageRatingTextbox.value),
            'kWhstored'      : float(self.StorageCapacityTextbox.value) * 0.50,
            '%EffCharge'     : float(self.CeffSlider.value),
            '%EffDischarge'  : float(self.DeffSlider.value),
            '%IdlingkW'      : (100 - self.IdleSlider.value),
            '%reserve'       : float(self.ReserveSlider.value),
            'State'          : 'IDLING',
            'pf'             : float(self.PFslider.value),
            'TimeChargeTrig' : '-1',
            '%Charge'        : float(self.RateChgSlider.value),
            '%Discharge'     : float(self.RateDchgSlider.value),

        }
        StorageController = None
        if self.StorageModeDropdown.value == 'Load following':
            Storageproperties['DispMode'] = 'FOLLOW'
            Storageproperties['ChargeTrigger'] = float(self.PSvalue.value)
            Storageproperties['DischargeTrigger'] = float(self.BLvalue.value)
            self.CreateLoadShape(pyDSS, ProfilePath, 'LoadShape')
            Storageproperties['Yearly'] = self.StoragenameTextbox.value

        elif self.StorageModeDropdown.value == 'Time triggered':
            Storageproperties['DispMode'] = 'EXTERNAL'
            Storageproperties['ChargeTrigger'] = '0.0'
            Storageproperties['DischargeTrigger'] = '0.0'
            StorageController = self.CreateStorageController()

        elif self.StorageModeDropdown.value == 'Peak shaving':
            Storageproperties['DispMode'] = 'EXTERNAL'
            Storageproperties['ChargeTrigger'] = '0.0'
            Storageproperties['DischargeTrigger'] = '0.0'
            StorageController = self.CreateStorageController()

        elif self.StorageModeDropdown.value == 'Support':
            Storageproperties['DispMode'] = 'EXTERNAL'
            Storageproperties['ChargeTrigger'] = '0.0'
            Storageproperties['DischargeTrigger'] = '0.0'
            StorageController = self.CreateStorageController()

        elif self.StorageModeDropdown.value == 'Price triggered':
            Storageproperties['DispMode'] = 'PRICE'
            Storageproperties['ChargeTrigger'] = float(self.PSvalue.value)
            Storageproperties['DischargeTrigger'] = float(self.BLvalue.value)
            self.CreateLoadShape(pyDSS, ProfilePath, 'PriceShape')
            pyDSS.runCommand('Set PriceCurve={}'.format(self.StoragenameTextbox.value))

        pyDSS.Add_Element('Storage', self.StoragenameTextbox.value, Storageproperties)
        if Storageproperties['DispMode'] == 'EXTERNAL':
            print('Creating storage controller')
            pyDSS.Add_Element('StorageController', self.StoragenameTextbox.value, StorageController)

        pyDSS.runCommand('Calcv')
        return

    def CreateLoadShape(self, pyDSS, ProfilePath, Type):
        Loadshape = {
            'npts': self.Textbox_nDatapoints.value,
        }
        if Type == 'PriceShape':
            Loadshape['mInterval'] = '60'
            Loadshape['price'] = '(file=' + ProfilePath + ')'
        else:
            Loadshape['mInterval'] = self.Slider_stepsize.value
            Loadshape['mult'] = '(file=' + ProfilePath + ')'
        pyDSS.Add_Element(Type, self.StoragenameTextbox.value, Loadshape)
        return

    def CreateStorageController(self):
        # Create corresponding Inverter controller
        StorageController = {
            'element'              : 'line.' + self.StoragenameTextbox.value + '_sw',
            'ElementList'          : self.StoragenameTextbox.value,
            'terminal'             : 1,
            '%kWBand'              : self.BandwidthSlider.value,
            '%RateCharge'          : self.RateChgSlider.value,
            '%RateKw'              : self.RateDchgSlider.value,
            '%Reserve'             : self.ReserveSlider.value,
            'Enabled'              : 'True',
            'TimeChargeTrigger'    : self.ChgTrSLider.value,
            'TimeDischargeTrigger' : self.DchgTrSLider.value,
        }

        if self.Node_dropdown.value == '':
            StorageController['element'] = 'line.' + self.StoragenameTextbox.value + '_sw'
        else:
            StorageController['element'] = 'line.' + self.Node_dropdown.value

        if self.StorageModeDropdown.value == 'Time triggered':
            StorageController['ModeCharge'] = 'Time'
            StorageController['ModeDischarge'] = 'Time'

        elif self.StorageModeDropdown.value == 'Peak shaving':
            StorageController['ModeCharge'] = 'Time'
            StorageController['ModeDischarge'] = 'PeakShave'
            StorageController['kWTarget'] = float(self.PeakShaveValue.value)

        elif self.StorageModeDropdown.value == 'Support':
            StorageController['ModeCharge'] = 'Time'
            StorageController['ModeDischarge'] = 'Support'
            StorageController['kWTarget'] = float(self.BaseLoadValue.value)

        return StorageController

    def toPhase(self, sPhases):
        sPhases = sPhases.replace('A', '.1')
        sPhases = sPhases.replace('B', '.2')
        sPhases = sPhases.replace('C', '.3')
        return sPhases

    def layout(self):
        return self.final_layout

    def createStoragewidgetbox(self):
        self.StoragenameTextbox=TextInput(title="Storage name (unique; no spaces or dots)", value='')
        self.BusNameTextbox = TextInput(title="Bus name", value='')
        self.BusNameTextbox.disabled = True
        PVname = row(self.StoragenameTextbox, self.BusNameTextbox)


        self.StorageRatingTextbox = TextInput(title="Storage rating [kVA]", value='1.0')
        self.StorageCapacityTextbox = TextInput(title="Storage capacity [kVAh]", value='1.0')
        PVratings = row(self.StorageRatingTextbox, self.StorageCapacityTextbox)

        self.kWratingSlider = Slider(title="Storage kW rating [p.u]", value=1.0, start=0.0, end=1.0, step=0.01)
        self.PFslider = Slider(title="Storage power factor", value=1, start=-1.0, end=1.0, step=0.01)
        StorageRatings = row(self.kWratingSlider, self.PFslider)

        self.StorageModeDropdown = Select(title="Storage control mode", value='Time triggered',
                                      options=['Load following', 'Price triggered', 'Time triggered', 'Peak shaving', 'Support'])
        self.Dropdown_phases = Select(title="Phases", value="", options=[])
        #self.Textbox_SelectedNode.disabled = True
        self.Node_dropdown = Select(title="Remote measurement node", value="", options=[])
        self.IdleSlider = Slider(title="Efficiency idling [%]", value=95.0, start=0, end=100, step=0.1)
        FPFsettings = row(self.Node_dropdown, self.IdleSlider)

        self.CeffSlider = Slider(title="Efficiency charging [%]", value=95.0, start=0, end=100, step=0.1)
        self.DeffSlider = Slider(title="Efficiency discharging [%]", value=95.0, start=0, end=100, step=0.1)
        EfficiencySettings = row(self.CeffSlider, self.DeffSlider)

        self.BandwidthSlider = Slider(title="Bandwidth [% of target KW]", value=2.0, start=0, end=100, step=0.1)
        self.ReserveSlider = Slider(title="Contingency reserve [%]", value=0.0, start=0, end=100, step=0.1)
        ControlSetings = row(self.BandwidthSlider, self.ReserveSlider)
        StorageAdditionalSettings = column(EfficiencySettings, ControlSetings)

        XX = row( self.StorageModeDropdown, self.Dropdown_phases)
        PVsettings = column(PVname, PVratings, StorageRatings,FPFsettings, StorageAdditionalSettings, XX)

        self.RateChgSlider = Slider(title="Charging power [%]", value=50, start=0, end=100, step=1)
            #Select(title="Remote measurement node", value="",
                       #               options=[''])
        self.RateDchgSlider = Slider(title="Discharging power [%]", value=50, start=0, end=100, step=1)
        voltageDBlimitsVW = row(self.RateChgSlider, self.RateDchgSlider)
        self.PSvalue  = Slider(title="LMP charge threshold [$/MWh]", value=20, start=0, end=150, step=1)
        self.BLvalue  = Slider(title="LMP discharge threshold [$/MWh]", value=30, start=0, end=150, step=1)
        voltageVW = row(self.PSvalue, self.BLvalue)

        self.PeakShaveValue = TextInput(title="Peak shaving limit [kW]", value='0.0')
        self.BaseLoadValue = TextInput(title="Base loading limit [kW]", value='0.0')
        PSBLBox = row(self.PeakShaveValue, self.BaseLoadValue)

        VoltWattBox = column(voltageDBlimitsVW, voltageVW)
        self.ChgTrSLider = Slider(title="Trigger charging [h]", value=0.0, start=0.0, end=24.0, step=0.05)
        self.DchgTrSLider = Slider(title="Trigger discharging [h]", value=0.0, start=0.0, end=24.0, step=0.05)
        Timetriggers = row(self.ChgTrSLider, self.DchgTrSLider)
        self.Textbox_nDatapoints = TextInput(title="Number of data points", value='525600')
        self.Slider_stepsize = Slider(title="profile resolution [m]", value=1, start=1, end=60, step=1)
        self.LoadshapesCombo = Select(title="Exsisting profiles", value='', options=[''])
        self.ProfileRes = Slider(title="Profile resolution [m]", value=15, start=1, end=60, step=1)
        self.addStoragebutton = Button(label="Add storage to the network", button_type="danger")
        PVxy = row(self.LoadshapesCombo, self.Textbox_nDatapoints)
        XX = row(self.Slider_stepsize, self.addStoragebutton)
        return column(PVsettings, VoltWattBox, Timetriggers,PSBLBox, PVxy,  XX)

    def updateStoragecurves(self, attrname, old, new):
        # Get the current slider values
        kWlim = self.kWratingSlider.value
        powerfactor = self.PFslider.value

        P = powerfactor
        Q = np.sin(np.arccos(P))

        self.StoragecurveDatasource.data = {'x0' : [-1, 1],
                                       'y0' : [kWlim, kWlim],
                                       'x1' : [-1, 1],
                                       'y1' : [-kWlim, -kWlim],
                                       'x2' : [-Q, Q],
                                       'y2' : [-P, P],
                                       }
