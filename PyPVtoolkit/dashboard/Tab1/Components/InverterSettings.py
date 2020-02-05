import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource,VeeHead, Arrow, Range1d
from bokeh.models.widgets import Slider, TextInput, Button, Select

class Create():
    def __init__(self):
        self.InvCapabilityPlot = figure(plot_width=580, plot_height=350,
                                     tools='', title="Inverter capability curve")
        self.PVSettingsPlot = figure(plot_width=580, plot_height=350,
                                tools='', title="PV settings")
        self.VoltVarDatasource = ColumnDataSource(data=dict(x=[], y=[]))
        self.PVSettingsPlot.line('x', 'y', source=self.VoltVarDatasource, line_width=2, line_alpha=0.6,
                                 legend='volt/var', line_color="blue")
        self.VoltWattDatasource = ColumnDataSource(data=dict(x=[], y=[]))
        self.PVSettingsPlot.line('x', 'y', source=self.VoltWattDatasource, line_width=2, line_alpha=0.6,
                                 legend='volt/watt', line_color="red")


        self.InvCapabilityPlot.xaxis.axis_label = 'Q [p.u]'
        self.InvCapabilityPlot.yaxis.axis_label = 'P [p.u]'
        self.InvCapabilityPlot.toolbar.logo = None
        self.InvCapabilityPlot.toolbar_location = None
        self.InvCapabilityPlot.y_range = Range1d(*(-0.05,1.15))
        self.InvCapabilityPlot.x_range = Range1d(*(-1.15, 1.15))

        self.InvCapabilityPlot.circle(x=[0], y=[0], radius=0.001,
                 color=["black"])
        self.InvCapabilityPlot.add_layout(Arrow(end=VeeHead(size=10), line_color="black",
                                            x_start=0.0, y_start=0, x_end=0, y_end=1.1))
        self.InvCapabilityPlot.add_layout(Arrow(end=VeeHead(size=10), line_color="black",
                                            x_start=-1.1, y_start=0, x_end=1.1, y_end=0))
        self.InvCapabilityPlot.arc(x=[0], y=[0], radius=1, start_angle=0, end_angle=3.142, color="navy")

        self.PVcurveDatasource = ColumnDataSource(data=dict(x0=[], x1=[], x2=[], x3=[], x4=[], x5=[], x6=[],
                                                            y0=[], y1=[], y2=[], y3=[], y4=[], y5=[], y6=[]))
        self.InvCapabilityPlot.line('x0', 'y0', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                 line_color="red")
        self.InvCapabilityPlot.line('x1', 'y1', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                 line_color="red")
        self.InvCapabilityPlot.line('x2', 'y2', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                 line_color="red")
        self.InvCapabilityPlot.line('x3', 'y3', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.InvCapabilityPlot.line('x4', 'y4', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.InvCapabilityPlot.line('x5', 'y5', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.InvCapabilityPlot.line('x6', 'y6', source=self.PVcurveDatasource, line_width=1, line_alpha=1.0,
                                    line_color="red")
        self.PVSettingsPlot.xaxis.axis_label = 'Voltage [p.u]'
        self.PVSettingsPlot.yaxis.axis_label = 'P,Q [p.u]'
        self.PVSettingsPlot.toolbar.logo = None
        self.PVSettingsPlot.toolbar_location = None
        self.PVSettingsPlot.legend.location = "bottom_left"
        self.PVSettingsPlot.legend.click_policy = "hide"
        self.PVSettingsPlot.x_range = Range1d(*(0.9, 1.2))
        self.PVSettingsPlot.y_range = Range1d(*(-1.15, 1.15))
        self.PVSettingsPlot.circle(x=[1], y=[0], radius=0.001,color=["black"])
        self.ArrowHead1 = Arrow(end=VeeHead(size=10), line_color="black",
                                x_start=1.0, y_start=-1.1, x_end=1 , y_end=1.1)
        self.ArrowHead2 = Arrow(end=VeeHead(size=10), line_color="black",
                                x_start=0.9, y_start=0, x_end=1.2, y_end=0)
        self.PVSettingsPlot.add_layout(self.ArrowHead1)
        self.PVSettingsPlot.add_layout(self.ArrowHead2)

        PVwidgetbox = self.createPVwidgetbox()
        PVsettingsLayout = column(self.InvCapabilityPlot, self.PVSettingsPlot, PVwidgetbox, width=800)
        self.final_layout = PVsettingsLayout

        for w in [self.PVvar, self.Vlb, self.Vub, self.Vdblb, self.Vdbub,
                  self.VWlb , self.VWub, self.VWPmin, self.VWumin,
                  self.PVRatingTB, self.PVcutinTB, self.PVcutoutTB, self.PVpf]:
            w.on_change('value', self.updatePVcurves)

        self.updatePVcurves(None, None, None)
        return

    def addPVsystem(self, pyDSS, NodeData, ProfilePath):
        # Create corresponding PV system
        nPhases = len(self.Dropwown_phases.value)
        PVproperties = {
            'bus1'      : NodeData['toBus'] + self.toPhase(self.Dropwown_phases.value),
            'phases'    : nPhases,
            'kv'        : NodeData['kVbase'] if nPhases == 1 else NodeData['kVbase'] * 1.732,
            'kVA'       : self.InverterRatingTextbox.value,
            'Pmpp'      : float(self.InverterRatingTextbox.value) * self.PVRatingTB.value,
            'kvarLimit' : float(self.InverterRatingTextbox.value) * self.PVvar.value,
            '%Cutin'    : self.PVcutinTB.value * 100,
            '%Cutout'   : self.PVcutoutTB.value * 100,
            'Enabled'   : 'True'
        }
        if self.InverterModeDropwown.value == 'Fix power factor':
            if self.PFsign.value == "Lagging":
                PVproperties['pf'] = -self.PVpf.value
            else:
                PVproperties['pf'] = self.PVpf.value
        else:
            VVcurve = self.CreateVVCurve(pyDSS)
            VWcurve = self.CreateVWCurve(pyDSS)
            self.InvProperties = self.CreateInverter(VVcurve, VWcurve)
        if '.csv' in ProfilePath.lower():
            PVproperties['yearly'] = self.PVnameTextbox.value
            # Create corresponding load shape
            self.CreateLoadShape(pyDSS, ProfilePath)
        else:
            PVproperties['yearly'] = ProfilePath
        pyDSS.Add_Element('PVsystem', self.PVnameTextbox.value, PVproperties)
        if self.InverterModeDropwown.value != 'Fix power factor':
            pyDSS.Add_Element('InvControl', self.PVnameTextbox.value, self.InvProperties)
        return

    def CreateLoadShape(self, pyDSS, ProfilePath):
        Loadshape = {
            'npts': self.Textbox_nDatapoints.value,
            'mInterval': self.Slider_stepsize.value,
            'mult': '(file=' + ProfilePath + ')',
        }
        pyDSS.Add_Element('loadshape', self.PVnameTextbox.value, Loadshape)
        return

    def CreateInverter(self,VVcurve, VWcurve):
        # Create corresponding Inverter controller
        WVmode = self.Select_Cur_control.value
        VVpriority = self.Select_priority.value
        InvProperties = {
            # 'DeltaP_factor'       : '',
            # 'DeltaQ_factor'       : '',
            'PVSystemList'        : '[' + self.PVnameTextbox.value + ']',
            'vvc_curve1'          : VVcurve,
            'Voltwatt_curve'      : VWcurve,
            'VoltwattYAxis'       : 'PMPPPU' if WVmode == "Rated power" else 'PAVAILABLEPU',
            'VV_RefReactivePower' : 'VARMAX_VARS' if VVpriority == 'Var' else 'VARMAX_WATTS',
            'Enabled'             : 'True'
        }
        if self.InverterModeDropwown.value == 'Volt var':
            InvProperties['Mode'] = 'VOLTVAR'
        elif self.InverterModeDropwown.value == 'Volt watt':
            InvProperties['Mode'] = 'VOLTWATT'
        elif self.InverterModeDropwown.value == 'Volt var / volt watt':
            InvProperties['CombiMode'] = 'VV_VW'

        return InvProperties

    def CreateVVCurve(self, pyDSS):
        name = 'VV_' + self.PVnameTextbox.value
        Y = [0, self.Vlb.value, self.Vdblb.value, self.Vdbub.value, self.Vub.value, self.VWumin.value]
        X = [1, 1, 0.01, 0.01, -1, -1]
        npts = len(X)
        XYcurve = {
            'npts'   : npts,
            'Xarray' : str(Y).replace('[', '(').replace(']', ')'),
            'Yarray' : str(X).replace('[', '(').replace(']', ')'),
        }
        pyDSS.Add_Element('XYcurve', name, XYcurve)
        return name

    def CreateVWCurve(self, pyDSS):
        name = 'VW_' + self.PVnameTextbox.value
        Y = [0, self.VWlb.value, self.VWub.value, self.VWumin.value, self.VWumin.value + 0.01]
        X = [1, 1, self.VWPmin.value, self.VWPmin.value, 0.01]
        npts = len(X)
        XYcurve = {
            'npts'   : npts,
            'Xarray' : str(Y).replace('[', '(').replace(']', ')'),
            'Yarray' : str(X).replace('[', '(').replace(']', ')'),
        }
        pyDSS.Add_Element('XYcurve', name, XYcurve)
        return name

    def toPhase(self, sPhases):
        sPhases = sPhases.replace('A', '.1')
        sPhases = sPhases.replace('B', '.2')
        sPhases = sPhases.replace('C', '.3')
        return sPhases

    def layout(self):
        return self.final_layout

    def createPVwidgetbox(self):
        self.PVnameTextbox=TextInput(title="PV name (unique; no spaces or dots)", value='')
        self.BusNameTextbox = TextInput(title="Bus name", value='')
        self.BusNameTextbox.disabled = True
        PVname = row(self.PVnameTextbox, self.BusNameTextbox)


        self.InverterRatingTextbox = TextInput(title="Inverter rating [KVA]", value='1.0')
        self.PVRatingTB = Slider(title="PV module rating [p.u]", value=1.0, start=0.0, end=1.0, step=0.01)
        PVratings = row(self.InverterRatingTextbox, self.PVRatingTB)

        self.PVvar = Slider(title="Inverter kvar limit [p.u]", value=0.44, start=0.0, end=1.0, step=0.01)
        self.PVpf = Slider(title="Inverter pf limit", value=0.95, start=0.0, end=1.0, step=0.01)
        PVpfq = row(self.PVvar, self.PVpf)

        self.PVcutinTB = Slider(title="PV cutin (active power) [p.u]", value=0.1, start=0.0, end=1.0, step=0.01)
        self.PVcutoutTB = Slider(title="PV cutout (active power) [p.u]", value=0.1, start=0.0, end=1.0, step=0.01)
        PVgensets = row(self.PVcutinTB, self.PVcutoutTB)

        self.InverterModeDropwown = Select(title="Inverter control mode", value="Fix power factor",
                                      options=["Fix power factor", "Volt var", "Volt watt", "Volt var / volt watt"])
        self.Dropwown_phases = Select(title="Phases", value="", options=[])
        #self.Textbox_SelectedNode.disabled = True
        XX = row( self.InverterModeDropwown, self.Dropwown_phases)

        PVsettings = column(PVname, PVratings, PVpfq, PVgensets, XX)

        self.PFslider = Slider(title="FPF: Power factor", value=0.95, start=0.0, end=1.0, step=0.01)
        self.PFsign = Select(title="Mode", value="Lagging", options=["Lagging", "Leading"])
        FPFsettings = row(self.PFslider, self.PFsign)

        self.Vlb = Slider(title="VV: min voltage [p.u]", value=0.95, start=0.9, end=1.1, step=0.001)
        self.Vub = Slider(title="VV: max voltage [p.u]", value=1.06, start=0.9, end=1.1, step=0.001)
        voltageLimits = row(self.Vlb, self.Vub)

        self.Vdblb = Slider(title="VVdb: min voltage [p.u]", value=0.97, start=0.9, end=1.1, step=0.001)
        self.Vdbub = Slider(title="VVdb: max voltage [p.u]", value=1.03, start=0.9, end=1.1, step=0.001)
        voltageDBlimits = row(self.Vdblb, self.Vdbub)

        VoltVarBox = column(voltageLimits,voltageDBlimits)

        self.VWlb = Slider(title="VW: min voltage [p.u]", value=1.06, start=0.9, end=1.1, step=0.001)
        self.VWub = Slider(title="VW: max voltage [p.u]", value=1.10, start=0.9, end=1.2, step=0.001)
        voltageDBlimitsVW = row(self.VWlb, self.VWub)
        self.VWPmin = Slider(title="VW: Minimum active power output [p.u]", value=0.5, start=0.0, end=1.0, step=0.01)
        self.VWumin = Slider(title="VW: Disconnect voltage [p.u]", value=1.15, start=1.0, end=1.2, step=0.001)
        voltageVW = row(self.VWPmin, self.VWumin)
        VoltWattBox = column(voltageDBlimitsVW, voltageVW)



        self.Select_priority = Select(title="Inverter priority mode", value="Var", options=["Var", "Watt"])
        self.Select_Cur_control = Select(title="Curtailment mode", value="Rated power",
                                      options=["Rated power", "Available power"])
        PVpri= row(self.Select_priority, self.Select_Cur_control)

        self.Textbox_nDatapoints = TextInput(title="Number of data points", value='525600')
        self.Slider_stepsize = Slider(title="profile resolution [m]", value=1, start=1, end=60, step=1)


        self.LoadshapesCombo = Select(title="Exsisting profiles", value='', options=[''])
        self.ProfileRes = Slider(title="Profile resolution [m]", value=15, start=1, end=60, step=1)
        self.addPVbutton = Button(label="Add PV to the network", button_type="danger")
        PVxy = row(self.LoadshapesCombo, self.Textbox_nDatapoints)
        XX = row(self.Slider_stepsize, self.addPVbutton)
        return column(PVsettings, FPFsettings, VoltVarBox, VoltWattBox, PVpri, PVxy,  XX)

    def updatePVcurves(self, attrname, old, new):
        # Get the current slider values
        Qlim = self.PVvar.value
        Vmin = self.Vlb.value
        Vmax = self.Vub.value
        Vdbmin = self.Vdblb.value

        Vdbmax = self.Vdbub.value

        self.Vlb.start = 0.9
        self.Vlb.end = Vdbmin

        self.Vdblb.start = Vmin
        self.Vdblb.end = Vdbmax

        self.Vdbub.start = Vdbmin
        self.Vdbub.end = Vmax

        self.Vub.start = Vdbmax
        self.Vub.end = 1.1

        VminVW = self.VWlb.value
        VmaxVW = self.VWub.value
        Pmin = self.VWPmin.value
        Vcutoff = self.VWumin.value

        self.VWlb.start = Vmin
        self.VWlb.end = VmaxVW

        self.VWub.start = VminVW
        self.VWub.end = Vcutoff

        self.VWumin.start = VmaxVW
        self.VWumin.end = 1.2

        self.VoltVarDatasource.data = dict(x=[Vmin, Vdbmin, Vdbmax, Vmax, Vcutoff],
                                           y=[Qlim, 0 , 0, -Qlim, -Qlim])

        self.VoltWattDatasource.data = dict(x=[Vmin,VminVW, VmaxVW, Vcutoff, Vcutoff],
                                            y= [1   ,  1    , Pmin , Pmin   , 0])

        PVrating = self.PVRatingTB.value
        Vcutout = self.PVcutoutTB.value
        Vcutin = self.PVcutinTB.value
        pf = self.PVpf.value
        P = pf
        Q = np.sin(np.arccos(P))


        self.PVcurveDatasource.data = {'x0' : [-1, 1],
                                       'y0' : [PVrating, PVrating],
                                       'x1' : [-1, 1],
                                       'y1' : [Vcutout, Vcutout],
                                       'x2' : [-1, 1],
                                       'y2' : [Vcutin, Vcutin],
                                       'x3' : [0, Q],
                                       'y3' : [0, P],
                                       'x4' : [0, -Q],
                                       'y4' : [0, P],
                                       'x5' : [Qlim, Qlim],
                                       'y5' : [0, 1],
                                       'x6' : [-Qlim, -Qlim],
                                       'y6' : [0, 1]
                                       }
