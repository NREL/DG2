from PyPVtoolkit.dashboard import mainDashboard
from PyPVtoolkit.PyDSSlite import PyDSS
from bokeh.models import ColumnDataSource
from tkinter import filedialog
from tkinter import Tk
import numpy as np
import datetime
import os
class createApplication():
    def __init__(self, doc, opendss_path):
        self.opendss_path = opendss_path
        self.Dash = mainDashboard.Create(doc, opendss_path)
        self.Dash.layout1.Settings.LogCombo.on_change('value', self.SetLoggerDebugLevel)
        self.Logger = self.Dash.layout1.LogTable
        self.Logger.Log(1, 'Creating pyPVtoolkit instance')
        self.Dash.layout1.Settings.Button_loadDSSproject.on_click(self.createPyDSSinstance)
        self.Dash.layout1.Settings.Allocate_load.on_click(self.runLoadAllocation)
        self.Dash.layout1.Settings.saveChangesBtn.on_click(self.saveChanges)
        self.Dash.layout1.Settings.clearChangesBtn.on_click(self.clearChanges)
        self.Dash.layout1.InvSettings.addPVbutton.on_click(self.addPVsystem)
        self.Dash.layout1.Settings.Textbox_dssPath.on_change('value', self.updateOpenDSSfiles)
        self.Dash.layout1.StorageSettings.addStoragebutton.on_click(self.addStorageSystem)
        for w in [self.Dash.layout2.Settings.startDay, self.Dash.layout2.Settings.Hour]:
            w.on_change('value', self.RunStaticFL)
        for w in self.Dash.layout2.Settings.GetLineSliders():
            w.on_change('value', self.TableBindings)
        for w in [self.Dash.layout3.Settings.Vll, self.Dash.layout3.Settings.Vul]:
            w.on_change('value', self.UpdateYearlyPlots)
        # self.Dash.layout4.Settings.runSimulation.on_click(self.RunTSsimulation)
        self.Dash.layout3.Settings.runSimulation.on_click(self.YearlyRunPass)
        self.Dash.layout3.Settings.PptyCombo.on_change('value', self.Layout3Update)
        self.Dash.layout3.Settings.Class.on_change('value', self.Layout3ElmComboUpdate)
        return

    def updateOpenDSSfiles(self, attr, old, new):
        activeProject = self.Dash.layout1.Settings.Textbox_dssPath.value
        files_path = os.path.join(self.opendss_path, activeProject)
        files = list(filter(lambda x: '.dss' in x, os.listdir(files_path)))
        self.Dash.layout1.Settings.Opendssfilepath.value = files[0]
        self.Dash.layout1.Settings.Opendssfilepath.options = files
        return

    def GetLayout(self):
        return self.Dash.Layout()

    def clearChanges(self):
        self.Logger.Log(1, 'Clearing all modifications to the network')
        self.pyDSS.clear_Modifications()
        return

    def saveChanges(self):
        self.Logger.Log(1, 'Saving modified network')
        self.Dash.layout1.Settings.clearChangesBtn.disabled = False
        self.pyDSS.Save_Modifications()
        self.Logger.Log(1, 'File saved successfully')
        return

    def runLoadAllocation(self):
        root = Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        root.filename = filedialog.askopenfilename(initialdir=r"C:/Users/alatif/Desktop/A201202",
                                                   title="Select OpenDSS master file",
                                                   filetypes=(("OpenDSS files", "*.dss"),))
        self.Dash.layout1.Settings.load_Path.value = root.filename
        if root.filename:
            self.Logger.Log(1, 'Running load allocation')

            #self.pyDSS = PyDSS.createInstance(Settings, self.Logger)
            #self.dssGraph = self.pyDSS.graph()
            #self.CreateGlobalDataSource()
            #self.Dash.layout1.TopologyPlot.createPlot(self.source)
            #self.GetListofLines()
            #self.updatePVcombo()

            root.quit()
        return

    def UpdateYearlyPlots(self, attr, old, new):
        self.doYearlyCalculations()

    def GetListofLines(self):
        self.Logger.Log(1, 'Creating node list...')
        self.dssInstance = self.pyDSS.getInstance()
        LineList = self.dssInstance.Lines.AllNames()
        LineList.insert(0, '')
        self.Dash.layout1.StorageSettings.Node_dropdown.options = LineList
        self.Dash.layout1.StorageSettings.Node_dropdown.value = LineList[0]
        self.Logger.Log(1, 'Complete')

    def SetLoggerDebugLevel(self, attr, old, new):
        if self.Dash.layout1.Settings.LogCombo.value == 'debug':
            self.Logger.SetLoggingLevel(0)
        elif self.Dash.layout1.Settings.LogCombo.value == 'info':
            self.Logger.SetLoggingLevel(1)
        elif self.Dash.layout1.Settings.LogCombo.value == 'warning':
            self.Logger.SetLoggingLevel(2)
        elif self.Dash.layout1.Settings.LogCombo.value == 'error':
            self.Logger.SetLoggingLevel(3)

    def Layout3Update(self, attr, old, new):
        Property  = self.Dash.layout3.Settings.PptyCombo.value
        self.updateYearlyPlots(Property)
        return

    def Layout3ElmComboUpdate(self, attr, old, new):
        Class = self.Dash.layout3.Settings.Class.value
        self.dssInstance = self.pyDSS.getInstance()
        if Class == 'PVsystem':
            ElementNames = self.dssInstance.PVsystems.AllNames()
            self.Dash.layout3.Settings.Element.options = ElementNames
            self.Dash.layout3.Settings.Element.value = ElementNames[0]
        elif Class == 'Storage':
            ElementNames = self.pyDSS.GetElementList('Storage')
            self.Dash.layout3.Settings.Element.options = ElementNames
            self.Dash.layout3.Settings.Element.value = ElementNames[0]
        return

    def RunTSsimulation(self):
        if hasattr(self, 'dssInstance'):
            PVname =  'pvsystem.' + self.Dash.layout4.Settings.PVsystem.value
            self.dssInstance.Circuit.SetActiveElement(PVname)
            if self.dssInstance.CktElement.Name().lower() == PVname.lower():
                Bus = self.dssInstance.CktElement.BusNames()[0].split('.')[0]
                self.dssInstance.Circuit.SetActiveBus(Bus)
                if self.dssInstance.Bus.Name().lower() == Bus.lower():
                    StartDay = self.Dash.layout4.Settings.startDay.value
                    if type(StartDay) == datetime.datetime:
                        sDate = StartDay.date()
                        sDayOfYear = (sDate - datetime.date(sDate.year, 1, 1)).days
                    else:
                        sDate = StartDay
                        sDayOfYear = (sDate - datetime.date(sDate.year, 1, 1)).days + 1
                    EndDay = self.Dash.layout4.Settings.endDay.value
                    if type(EndDay) == datetime.datetime:
                        eDate = EndDay.date()
                        eDayOfYear = (eDate - datetime.date(eDate.year, 1, 1)).days
                    else:
                        eDate = EndDay
                        eDayOfYear = (eDate - datetime.date(eDate.year, 1, 1)).days + 1

                    TimeStep = self.Dash.layout4.Settings.timeStep.value / 60
                    PVdata = {
                        'P'  : [],
                        'Q'  : [],
                        'V'  : [],
                        'T'  : [],
                        'PF' : [],
                    }

                    if eDayOfYear >= sDayOfYear:
                        for day in range(sDayOfYear, eDayOfYear+1):
                            for hour in np.arange(0, 23, TimeStep):
                                self.pyDSS.dssSolver.SolveAt2(day, hour)
                                vBase = self.dssInstance.Bus.kVBase() * 1000
                                V = max(self.dssInstance.CktElement.VoltagesMagAng()[0::2])
                                P = sum(self.dssInstance.CktElement.Powers()[0::2])
                                Q = sum(self.dssInstance.CktElement.Powers()[1::2])
                                S = np.sqrt(P ** 2 + Q ** 2)
                                if sum([P, Q, S]) == 0:
                                    PF = 1
                                else:
                                    PF = P/S
                                PVdata['P'].append(P)
                                PVdata['Q'].append(Q)
                                PVdata['V'].append(V/vBase)
                                PVdata['T'].append(day * 24 +  hour)
                                PVdata['PF'].append(PF)
                                self.UpdatePVplots(PVdata)
        else:
            self.Logger.Log(2, 'Load a valid OpenDSS project first.')
        return

    def YearlyRunPass(self):
        sDay = self.Dash.layout3.Settings.startDay.value
        eDay = self.Dash.layout3.Settings.endDay.value
        if type(sDay) == datetime.datetime:
            sDate = sDay.date()
            eDate = eDay.date()
        else:
            sDate = sDay
            eDate = eDay

        print(sDate, eDate)

        sD = (sDate - datetime.date(sDate.year, 1, 1)).days
        eD = (eDate - datetime.date(eDate.year, 1, 1)).days
        self.Logger.Log(1, "Time series simulation starting at day {} and will and on day {}".format(sD, eD))

        ClassName = self.Dash.layout3.Settings.Class.value
        ElmName = self.Dash.layout3.Settings.Element.value
        FullName = '{}.{}'.format(ClassName, ElmName)
        TimeStep = self.Dash.layout3.Settings.timeStep.value / 60

        # Base case yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 1")
        self.pyDSS.dssSolver.UpdateSettings()
        self.YearlyResults1 = self.RunYearlySimulation(TimeStep, FullName, 0, sD, eD)
        self.Logger.Log(1, "Complete")

        # Unity PF yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 2")
        if 'pvsystem.' in FullName.lower():
            print('FullName: ', FullName)
            print('PV enabled 1')
            self.PVinverterEnabled(ElmName, 'False')
            print(ElmName)
            print('PV enabled 2')
            self.pyDSS.Set_Parameter('PVsystem', ElmName, 'pf', 1)
            print('PV enabled 3')
            self.pyDSS.dssSolver.UpdateSettings()
            print('PV enabled 4')
            self.YearlyResults2 = self.RunYearlySimulation(TimeStep, FullName, 1, sD, eD)
            self.Logger.Log(1, "Complete")
        else:
            self.YearlyResults2 = {
                'Ptotal': [0] * len(self.YearlyResults1['Ptotal']),
                'Qtotal': [0] * len(self.YearlyResults1['Ptotal']),
                'Vmax': [0] * len(self.YearlyResults1['Ptotal']),
                'Vmin': [0] * len(self.YearlyResults1['Ptotal']),
                'PlTotal': [0] * len(self.YearlyResults1['Ptotal']),
                'QlTotal': [0] * len(self.YearlyResults1['Ptotal']),
                'Pelm': [0] * len(self.YearlyResults1['Ptotal']),
                'Qelm': [0] * len(self.YearlyResults1['Ptotal']),
                'VelmMax': [0] * len(self.YearlyResults1['Ptotal']),
                'VelmMin': [0] * len(self.YearlyResults1['Ptotal']),
                'Time': [0] * len(self.YearlyResults1['Ptotal']),
                'LMP': [0] * len(self.YearlyResults1['Ptotal']),
                'SOC': [0] * len(self.YearlyResults1['Ptotal']),
            }
            pass

        #Control yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 3")
        if 'pvsystem.' in FullName.lower():
            self.pyDSS.Set_Parameter('PVsystem', ElmName, 'Enabled', 'False')
            self.Logger.Log(1, "Nolo")
        else:
            self.Logger.Log(1, "Yolo")
            self.pyDSS.Set_Parameter('Storage', ElmName, 'Enabled', 'False')
        self.pyDSS.dssSolver.UpdateSettings()
        self.YearlyResults3 = self.RunYearlySimulation(TimeStep, FullName, 2, sD, eD)
        self.Logger.Log(1, "Complete")

        import pandas as pd
        print(pd.DataFrame(self.YearlyResults1))
        print(pd.DataFrame(self.YearlyResults2))
        print(pd.DataFrame(self.YearlyResults3))


        # Reset Controls
        if 'pvsystem.' in FullName.lower():
            self.PVinverterEnabled(ElmName, 'True')
        else:
            self.pyDSS.Set_Parameter('Storage', ElmName, 'Enabled', 'True')

        self.pyDSS.dssSolver.UpdateSettings()
        #Update plots
        self.Logger.Log(1, "Calculating and updating results")
        Ppty = self.Dash.layout3.Settings.PptyCombo.value
        self.doYearlyCalculations()
        self.updateYearlyPlots(Ppty)
        return

    def GetVoltageViolationMetrics(self, Profiles, Limit, LimitType):
        MaxV = []
        nVio = []
        Vdur = []
        for Profile in Profiles:
            if LimitType == 'UB':
                ViolationDuration = sum(np.greater(Profile, Limit))
                nViolations = sum([((Profile[i] < Limit) and (Profile[i + 1] > Limit)) for i in range(len(Profile) - 1)])
                MaxViolation = max(np.subtract(Profile, Limit)) if max(np.subtract(Profile, Limit)) > 0 else 0
            else:
                ViolationDuration = sum(np.less(Profile, Limit))
                nViolations = sum([((Profile[i] > Limit) and (Profile[i + 1] < Limit)) for i in range(len(Profile) - 1)])
                MaxViolation = max(np.subtract(Limit, Profile)) if max(np.subtract(Limit, Profile)) > 0 else 0
            MaxV.append(MaxViolation)
            nVio.append(nViolations)
            Vdur.append(ViolationDuration)
        return MaxV, nVio, Vdur

    def GetEnergyComponents(self, Profiles,  EnergyCorrCoef):
        pSums = []
        nSums = []
        for profile in Profiles:
            profile = np.multiply(np.array(profile), EnergyCorrCoef)
            pSums.append(-profile[profile > 0].sum()/1000)
            nSums.append(-profile[profile < 0].sum()/1000)
        return pSums, nSums

    def doYearlyCalculations(self):
        Ulb = self.Dash.layout3.Settings.Vll.value
        Uub = self.Dash.layout3.Settings.Vul.value
        EnergyCorrCoef = self.Dash.layout3.Settings.timeStep.value / 60

        Data = [self.YearlyResults1, self.YearlyResults2, self.YearlyResults3]

        Pcomps = self.GetEnergyComponents([self.YearlyResults1['Ptotal'],
                                           self.YearlyResults2['Ptotal'],
                                           self.YearlyResults3['Ptotal']],
                                          EnergyCorrCoef)

        Qcomps = self.GetEnergyComponents([self.YearlyResults1['Qtotal'],
                                           self.YearlyResults2['Qtotal'],
                                           self.YearlyResults3['Qtotal']],
                                          EnergyCorrCoef)

        PVEnergyS = abs(sum(self.YearlyResults1['Pelm'])) * EnergyCorrCoef
        PVEnergyU = abs(sum(self.YearlyResults2['Pelm'])) * EnergyCorrCoef

        KWHlossS = abs(sum(self.YearlyResults1['PlTotal'])) / 1000 * EnergyCorrCoef
        KWHlossU = abs(sum(self.YearlyResults2['PlTotal'])) / 1000 * EnergyCorrCoef
        KWHlossD = abs(sum(self.YearlyResults3['PlTotal'])) / 1000 * EnergyCorrCoef


        SysviolationsDataLB_S = self.GetVoltageViolationMetrics([self.YearlyResults1['Vmin'],
                                                                 self.YearlyResults2['Vmin'],
                                                                 self.YearlyResults3['Vmin']],
                                                                Ulb, 'LB')
        SysviolationsDataUB_S = self.GetVoltageViolationMetrics([self.YearlyResults1['Vmax'],
                                                                 self.YearlyResults2['Vmax'],
                                                                 self.YearlyResults3['Vmax']],
                                                                Uub, 'UB')
        PVviolationsDataLB_S = self.GetVoltageViolationMetrics([self.YearlyResults1['VelmMin'],
                                                                 self.YearlyResults2['VelmMin'],
                                                                 self.YearlyResults3['VelmMin']],
                                                                Ulb, 'LB')
        PVviolationsDataUB_S = self.GetVoltageViolationMetrics([self.YearlyResults1['VelmMax'],
                                                                 self.YearlyResults2['VelmMax'],
                                                                 self.YearlyResults3['VelmMax']],
                                                                Uub, 'UB')

        self.Dash.layout3.BarP1.updatePlot([PVEnergyS, PVEnergyU])
        self.Dash.layout3.BarP2.updatePlot(PVEnergyU - PVEnergyS)
        self.Dash.layout3.BarP3.updatePlot([KWHlossS, KWHlossU, KWHlossD])
        self.Dash.layout3.BarP3p.updatePlot(Pcomps)
        self.Dash.layout3.BarP3q.updatePlot(Qcomps)
        self.Dash.layout3.BarP4.updatePlot([SysviolationsDataLB_S[1], SysviolationsDataUB_S[1]])
        self.Dash.layout3.BarP5.updatePlot([SysviolationsDataLB_S[2], SysviolationsDataUB_S[2]])
        self.Dash.layout3.BarP6.updatePlot([PVviolationsDataLB_S[1], SysviolationsDataUB_S[1]])
        self.Dash.layout3.BarP7.updatePlot([PVviolationsDataLB_S[2], PVviolationsDataUB_S[2]])

        return

    def PVinverterEnabled(self, ElmName, State):
        self.dssInstance.Circuit.SetActiveClass('InvControl')
        try:
            Element = self.dssInstance.Circuit.FirstElement()
            while Element:
                ElementName = self.dssInstance.CktElement.Name().split('.')
                ControlledPVs =  self.pyDSS.Get_Parameter(ElementName[0], ElementName[1], 'PVsystemList')
                Ctrls = ControlledPVs.strip('[').strip(']').split(' ')
                if ElmName.lower() in Ctrls:
                    self.dssInstance.utils.run_command(
                        ElementName[0] + '.' + ElementName[1] + '.Enabled = {}'.format(State)
                    )
                    self.Logger.Log(1,"{}.{}'s state changed to: {}".format(ElementName[0],ElementName[1], State))
                Element = self.dssInstance.Circuit.NextElement()
        except:
            self.Logger.Log(0, "No instance of type {} in the current model.".format('InvControl'))
        return

    def updateYearlyPlots(self, Ppty):
        import pandas as pd

        PlotData = {
            'Pass1': self.YearlyResults1[Ppty],
            'Pass2': self.YearlyResults2[Ppty],
            'Pass3': self.YearlyResults3[Ppty],
        }
        self.Dash.layout3.BoxPlot.updatePlot(PlotData, '')
        PlotData['Time']=self.YearlyResults1['Time']
        self.Dash.layout3.TimePlot.updatePlot(PlotData, '', '')

    def RunYearlySimulation(self, TimeStep, PVsystem, Pass, sD, eD):
        self.dssInstance = self.pyDSS.getInstance()
        self.Results = {
            'Ptotal'   : [],
            'Qtotal'   : [],
            'Vmax'     : [],
            'Vmin'     : [],
            'PlTotal'  : [],
            'QlTotal'  : [],
            'Pelm'     : [],
            'Qelm'     : [],
            'VelmMax'  : [],
            'VelmMin'  : [],
            'Time'     : [],
            'LMP'      : [],
            'SOC'      : [],
        }

        self.dssInstance.Circuit.SetActiveClass('priceshape')
        Elem = self.dssInstance.Circuit.FirstElement()
        Price = self.dssInstance.Properties.Value('price')
        Price = Price.replace('[ ', '').replace(']', '').split(' ')
        Price = [float(x) for x in Price]
        print(sD, eD, TimeStep)
        for day in range(sD, eD):
            for hour in np.arange(0, 23, TimeStep):
                print(day, hour)
                #if Pass == 0:
                self.pyDSS.dssSolver.SolveAt2(day, hour)
                #else:
                #    self.pyDSS.dssSolver.SolveAt(day, hour)
                hourOfYear = day * 24 + int(hour)
                self.UpdateResults(day, hour, PVsystem, Price[hourOfYear])
        return self.Results

    def UpdateResults(self, day, hour, PVsystem, Price):
        self.dssInstance.Circuit.SetActiveElement(PVsystem)
        if self.dssInstance.CktElement.Name().lower() == PVsystem.lower():
            Bus = self.dssInstance.CktElement.BusNames()[0].split('.')[0]
            self.dssInstance.Circuit.SetActiveBus(Bus)
            if self.dssInstance.Bus.Name().lower() == Bus.lower():
                vBase = self.dssInstance.Bus.kVBase() * 1000
                V = self.dssInstance.CktElement.VoltagesMagAng()[0::2]
                puVoltages = self.dssInstance.Circuit.AllBusMagPu()
                self.Results['Ptotal'].append(sum(self.dssInstance.Circuit.TotalPower()[0::2]))
                self.Results['Qtotal'].append(sum(self.dssInstance.Circuit.TotalPower()[1::2]))
                self.Results['Vmax'].append(max(puVoltages))
                self.Results['Vmin'].append(min([i for i in puVoltages if i != 0]))
                self.Results['PlTotal'].append(sum(self.dssInstance.Circuit.Losses()[0::2]))
                self.Results['QlTotal'].append(sum(self.dssInstance.Circuit.Losses()[1::2]))
                self.Results['Pelm'].append(sum(self.dssInstance.CktElement.Powers()[0::2]))
                self.Results['Qelm'].append(sum(self.dssInstance.CktElement.Powers()[1::2]))
                self.Results['VelmMax'].append(max(V) / vBase)
                self.Results['VelmMin'].append(min([i for i in V if i != 0]) / vBase)
                self.Results['Time'].append(day + hour / 24)
                self.Results['LMP'].append(Price)
                if 'pvsystem.' in PVsystem.lower():
                    self.Results['SOC'].append(0)
                else:
                    print(self.dssInstance.Properties.Value('%stored'))
                    self.Results['SOC'].append(float(self.dssInstance.Properties.Value('%stored')))
        return

    def UpdatePVplots(self, Data):
        self.Dash.layout4.plotP.updatePlot(Data)
        self.Dash.layout4.plotQ.updatePlot(Data)
        self.Dash.layout4.plotV.updatePlot(Data)
        self.Dash.layout4.plotPF.updatePlot(Data)
        self.Dash.layout4.plotPV.updatePlot(Data)
        self.Dash.layout4.plotQV.updatePlot(Data)
        self.Dash.layout4.plotPQ.updatePlot(Data)
        return

    def TableBindings(self, attr, old, new):
        self.UpdateTables()
        return

    def RunStaticFL(self, attr, old, new):
        nDay = self.Dash.layout2.Settings.startDay.value
        if type(nDay) == datetime.datetime:
            Date = nDay.date()
        else:
            Date = nDay
        DayOfYear = (Date - datetime.date(Date.year,1,1)).days + 1
        Hour = self.Dash.layout2.Settings.Hour.value
        self.pyDSS.dssSolver.Reset()
        self.Logger.Log(1, 'Running load flow for day {} at time {} hours.'.format(DayOfYear, Hour))
        self.pyDSS.dssSolver.SolveAt2(DayOfYear, Hour)
        self.dssGraph = self.pyDSS.createGraph()
        self.CreateGlobalDataSource()
        self.UpdateTables()
        self.Dash.layout1.TopologyPlot.createPlot(self.source, self.sourceNode)
        self.Dash.layout2.VDplot.UpdatePlot(self.pyDSS.getInstance(), self.dssGraph)
        self.Dash.layout2.VLplots.UpdatePlot(self.source.data)
        VLdata = self.Dash.layout2.VLplots.GetPlotData()
        self.Dash.layout2.ProbLayout.UpdatePlot(VLdata)
        return

    def UpdateTables(self):
        self.Logger.Log(0, 'Updating snapshot tab tables')
        self.Dash.layout2.NAlayout.UpdateOverviewTable(self.dssGraph)
        self.Dash.layout2.NAlayout.UpdateVoltageViolationTable(self.source.data)
        self.Dash.layout2.NAlayout.UpdateLoadingViolationTable(self.source.data)
        self.Dash.layout2.VDplot.UpdateLimits()
        self.Dash.layout2.VLplots.UpdateLimits()
        return

    def addStorageSystem(self):
        LoadShapeName = self.Dash.layout1.StorageSettings.LoadshapesCombo.value
        NodeData = self.Dash.layout1.TopologyPlot.SelectedNode
        if hasattr(self, 'pyDSS') and len(NodeData['Class']) and len(self.Dash.layout1.StorageSettings.StoragenameTextbox.value):
            self.Dash.layout1.StorageSettings.CreateStorage(self.pyDSS, NodeData, LoadShapeName)
            self.pyDSS.dssSolver.Reset()
            #self.updatePVcombo()
            self.Dash.layout1.Settings.saveChangesBtn.disabled = False
        else:
            self.Logger.Log(2, 'Select a node from the topology plot first.')

        return

    def addPVsystem(self):
        if self.Dash.layout1.InvSettings.LoadshapesCombo.value == '':
            root = Tk()
            root.attributes("-topmost", True)
            root.withdraw()
            root.filename = filedialog.askopenfilename(initialdir=r"C:\Users\alatif\Desktop\wm_opendss_files\ojo_caliente",
                                                       title="Select Load / PV profile",
                                                       filetypes=(("Load / PV profile", "*.csv"), ))
            LoadShapeName = root.filename
        else:
            LoadShapeName = self.Dash.layout1.InvSettings.LoadshapesCombo.value

        NodeData = self.Dash.layout1.TopologyPlot.SelectedNode
        if hasattr(self, 'pyDSS') and len(NodeData['Class']) and len(self.Dash.layout1.InvSettings.PVnameTextbox.value):
            self.Dash.layout1.InvSettings.addPVsystem(self.pyDSS, NodeData, LoadShapeName)
            self.pyDSS.dssSolver.Reset()
            self.updatePVcombo()
            self.Dash.layout1.Settings.saveChangesBtn.disabled=False
        else:
            self.Logger.Log(2, 'Select a node from the topology plot first.')
        try:
            root.quit()
        except:
            pass
        return

    def createPyDSSinstance(self):
        project = self.Dash.layout1.Settings.Textbox_dssPath.value
        dssfile = self.Dash.layout1.Settings.Opendssfilepath.value
        dssPath = os.path.join(self.opendss_path, project, dssfile)

        if dssfile:
            Settings = {
                'Start Day'              : 1,
                'End Day'                : 365,
                'Hour'                   : 1,
                'Step resolution (min)'  : 1,
                'Max Control Iterations' : 50,
                'Simulation Type'        : 'Time series',
                'DSS File'               : dssPath,
            }
            self.Logger.Log(1, 'Creating OpenDSS instance')

            self.pyDSS= PyDSS.createInstance(Settings, self.Logger)
            self.dssGraph = self.pyDSS.graph()
            if self.dssGraph:
                self.Logger.Log(0, 'Network representation created sucessfully')

            self.Logger.Log(1, 'Creating OpenDSS instance')
            self.Logger.Log(0, 'Creating global data source...')
            self.CreateGlobalDataSource()
            self.Logger.Log(0, 'Complete')
            self.Logger.Log(0, 'Creating topology plot...')
            self.Dash.layout1.TopologyPlot.createPlot(self.source, self.sourceNode)
            self.Logger.Log(0, 'Complete')
            self.Logger.Log(0, 'Updating dropdown menues...')
            self.GetListofLines()
            self.updatePVcombo()
            self.Logger.Log(0, 'Complete')
        return

    def updatePVcombo(self):
        self.Logger.Log(0, 'Updating combo boxes')
        self.dssInstance = self.pyDSS.getInstance()
        LoadShapes = self.dssInstance.LoadShape.AllNames()
        LoadShapes.insert(0, '')
        self.Dash.layout1.InvSettings.LoadshapesCombo.options = LoadShapes
        self.Dash.layout1.InvSettings.LoadshapesCombo.value = LoadShapes[0]
        PVsystems = self.dssInstance.PVsystems.AllNames()
        #self.Dash.layout4.Settings.PVsystem.options = PVsystems
        #self.Dash.layout4.Settings.PVsystem.value = PVsystems[0]

        #self.Dash.layout3.Settings.PVsystem.options = PVsystems
        #self.Dash.layout3.Settings.PVsystem.value = PVsystems[0]
        return

    def CreateGlobalDataSource(self):
        self.Logger.Log(0, 'Creating global data souce.')
        self.clearData()
        for N1, N2 in self.dssGraph.edges():
            Xs = [self.dssGraph.node[N1]['X'], self.dssGraph.node[N2]['X']]
            Ys = [self.dssGraph.node[N1]['Y'], self.dssGraph.node[N2]['Y']]
            if 0 not in Xs and 0 not in Ys:
                V = ['%0.3f' % x for x in self.dssGraph.node[N2]['V']]
                VV = []
                VV.extend(self.dssGraph.node[N2]['V'])
                VV.extend(self.dssGraph.node[N1]['V'])
                VV = [x for x in VV if x != 0]
                self.Data['Class'].append(self.dssGraph[N1][N2]['Class'])
                self.Data['Name'].append(self.dssGraph[N1][N2]['Name'])
                self.Data['Xs'].append(Xs)
                self.Data['Ys'].append(Ys)
                self.Data['Phases'].append(self.toPhases(self.dssGraph.node[N1]['Phs']))
                self.Data['fromBus'].append(N1)
                self.Data['toBus'].append(N2)
                self.Data['X'].append(Xs[1])
                self.Data['Y'].append(Ys[1])
                self.Data['V'].append(V)
                self.Data['Vmax'].append(max(VV) if len(VV) > 0 else 0)
                self.Data['Vmin'].append(min(VV) if len(VV) > 0 else 0)
                self.Data['I'].append(self.dssGraph[N1][N2]['I'])
                self.Data['Imax'].append(self.dssGraph[N1][N2]['Imax'])
                self.Data['D'].append(self.dssGraph.node[N2]['D'])
                self.Data['kVbase'].append(self.dssGraph.node[N2]['kVbase'])
        # import pandas as pd
        # print(pd.DataFrame(self.Data))
        self.source.data = self.Data
        for Node in self.dssGraph.nodes():
            self.NodeData['X'].append(self.dssGraph.node[Node]['X'])
            self.NodeData['Y'].append(self.dssGraph.node[Node]['Y'])
            self.NodeData['PV'].append(self.dssGraph.node[Node]['PV'])
            self.NodeData['Storage'].append(self.dssGraph.node[Node]['Storage'])

        # import pandas as pd
        # print(pd.DataFrame(self.NodeData))
        self.sourceNode.data = self.NodeData

        return

    def clearData(self):
        self.Data = {
            'Class'   : [],
            'Name'    : [],
            'Xs'      : [],
            'Ys'      : [],
            'Phases'  : [],
            'fromBus' : [],
            'toBus'   : [],
            'X'       : [],
            'Y'       : [],
            'V'       : [],
            'D'       : [],
            'kVbase'  : [],
            'I'       : [],
            'Imax'    : [],
            'Vmax'    : [],
            'Vmin'    : [],
        }
        self.source = ColumnDataSource(self.Data)

        self.NodeData = {
            'X': [],
            'Y': [],
            'PV': [],
            'Storage': [],
        }
        self.sourceNode = ColumnDataSource(self.NodeData)
        self.SelectedNode = self.Data.copy()
        return

    def toPhases(self, phList):
        phases = ''
        if 0 in phList:
            phases+='A'
        if 1 in phList:
            phases+='B'
        if 2 in phList:
            phases+='C'
        return phases



