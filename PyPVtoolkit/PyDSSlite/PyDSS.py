from PyPVtoolkit.PyDSSlite.Components import SolveMode
from opendssdirect.utils import run_command
import opendssdirect as dss
import networkx as nx
import numpy as np
import datetime
import os
class createInstance:
    def __init__(self, SimulationSettings, Logger):
        self.Logger = Logger
        self.Network_Modifications = []
        self.__SimulationOptions = SimulationSettings
        self.__dssInstance = dss
        Logger.Log(1, 'Compiling: ' + SimulationSettings['DSS File'])
        self.__dssInstance.Basic.ClearAll()
        self.__dssInstance.utils.run_command('Log=NO')
        run_command('Clear')
        print('creating PyDSS')
        hasComplied =  run_command('compile ' + SimulationSettings['DSS File'])
        print(hasComplied)
        if 'Not Found' in hasComplied:
            Logger.Log(3,'OpenDSS file not found.')
            self.hasComplied = False
            return
        else:
            self.hasComplied = True
            Logger.Log(1, 'Project compilation successful.')

        self.__dssCircuit = dss.Circuit
        self.__dssElement = dss.Element
        self.__dssBus = dss.Bus
        self.__dssClass = dss.ActiveClass
        self.__dssCommand = run_command
        self.__dssSolution = dss.Solution

        run_command('Solve')
        self.createGraph()

        self.dssSolver = SolveMode.GetSolver(self.__SimulationOptions, self.__dssInstance, Logger)
        Logger.Log(1, 'pyDSS instance created successfully.')
        return

    def ValidateModificationDSSExistance(self):
        f = open(self.__SimulationOptions['DSS File'])
        lines = f.readlines()
        f.close()
        i = 0
        hasModiferFile = False
        for i, line in enumerate(lines):
            if 'redirect modifications.dss' in line.lower():
                hasModiferFile = True
                break
            if 'New Energymeter'.lower() in line.lower():
                break
        if not hasModiferFile:
            lines.insert(i, 'redirect modifications.dss\n\n')
            f = open(self.__SimulationOptions['DSS File'], 'w')
            for line in lines:
                f.write("%s" % line)
            f.close()

        sPath = self.__SimulationOptions['DSS File']
        index =  dict(map(reversed, enumerate(sPath)))["/"]
        dssDir = sPath[:index]
        self.ModFile = os.path.join(dssDir, 'modifications.dss')
        modifierFileExists = os.path.isfile(self.ModFile)
        if not modifierFileExists:
            open(self.ModFile, 'a').close()


    def clear_Modifications(self):
        self.Logger.Log(1, 'Clearing all modifications')
        f = open(self.ModFile, 'w')
        f.close()


    def Save_Modifications(self):

        self.ValidateModificationDSSExistance()
        self.Logger.Log(1, 'Opening modification file')
        f = open(self.ModFile, 'a')
        f.write('\n')
        for Cmd in self.Network_Modifications:
            f.write(Cmd + '\n')
        f.close()
        self.__init__(self.__SimulationOptions, self.Logger)
        self.Logger.Log(1, 'Network modifications saved to Modification.dss')
        return

    def Add_Element(self, Class, Name, Properties):
        Cmd = 'New ' + Class + '.' + Name
        print(Cmd)
        for PptyName, PptyVal in Properties.items():
            if PptyVal is not None:
                tCMD = ' ' + str(PptyName) + '=' + str(PptyVal)
                Cmd += tCMD
        print(self.__dssCommand(Cmd))
        self.Logger.Log(1, 'Element added: {}.{}'.format(Class, Name))
        self.Network_Modifications.append(Cmd)
        return

    def GetElementList(self, Class):
        Names = []
        self.__dssInstance.Circuit.SetActiveClass(Class)
        try:
            Elm = self.__dssInstance.Circuit.FirstElement()
            while Elm:
                Names.append(self.__dssInstance.CktElement.Name().split('.')[1])
                Elm = self.__dssInstance.Circuit.NextElement()
        except:
            return ['']
        return Names


    def graph(self):
        return self.dssGraph

    def getInstance(self):
        return self.__dssInstance

    def runCommand(self, cmd):
        self.Logger.Log(1, 'Running command: {}'.format(cmd))
        return self.__dssInstance.run_command(cmd)

    def RunSimulation(self, RunNumber = None):
        TotalDays = self.__SimulationOptions['End Day'] - self.__SimulationOptions['Start Day']
        Steps = int(TotalDays * 24 * 60 / self.__SimulationOptions['Step resolution (min)'])
        for i in range(Steps):
            self.dssSolver.SolveAt(0,i)
            Voltages = self.__dssCircuit.AllBusMagPu()
            print(max(Voltages))
            #self.__UpdateResults()

    def createGraph(self):
        self.Logger.Log(0, 'Creating graph representation for the network')
        Data = self.getNetworkData()
        self.dssGraph = nx.DiGraph()
        self.updateGraphAttributes(Data)
        self.Logger.Log(0, 'Creating graph nodes')
        self.createNodes(Data)
        self.Logger.Log(0, 'Creating graph edges')
        self.createEdges()
        self.Logger.Log(0, 'Graph creation complete')

        self.Logger.Log(0, 'Number of nodes: ' + str(len(self.dssGraph.nodes())))
        self.Logger.Log(0, 'Number of edges: ' + str(len(self.dssGraph.edges())))
        return self.dssGraph

    def createNodes(self, Data):
        dssNodes, Voltages, Distances, Losses, LineLosses, Power, subLosses = Data
        for i, dssNode in enumerate(dssNodes):
            NodeData = dssNode.split('.')
            NodeName = NodeData[0]
            NodePhases = int(NodeData[1]) - 1
            self.__dssInstance.Circuit.SetActiveBus(NodeName)
            X = self.__dssInstance.Bus.X()
            Y = self.__dssInstance.Bus.Y()
            if NodeName not in self.dssGraph.node:
                BusData = {
                    'kVbase' : self.__dssInstance.Bus.kVBase(),
                    'Name'   : NodeName.lower(),
                    'Phs'    : [NodePhases],
                    'D'      : Distances[i],
                    'V'      : [Voltages[i]],
                    'X'      : X,
                    'Y'      : Y,
                    'PV'     : 'black',
                    'Storage': 'black',
                }

                self.dssGraph.add_node(NodeName.lower(), BusData)
            else:
                self.dssGraph.node[NodeName]['V'].append(Voltages[i])
                self.dssGraph.node[NodeName]['Phs'].append(NodePhases)

            PVsystem = self.__dssInstance.PVsystems.First()
            while PVsystem:
                busnames = self.__dssInstance.CktElement.BusNames()
                busname = busnames[0].split('.')[0]
                if busname.lower() == NodeName.lower():
                    self.dssGraph.node[busname.lower()]['PV'] = 'green'
                PVsystem = self.__dssInstance.PVsystems.Next()

            self.__dssInstance.Circuit.SetActiveClass('Storage')
            Storage = self.__dssInstance.Circuit.FirstElement()
            while Storage:
                busnames = self.__dssInstance.CktElement.BusNames()
                busname = busnames[0].split('.')[0]
                if busname.lower() == NodeName.lower():
                    self.dssGraph.node[busname.lower()]['PV'] = 'pink'
                Storage = self.__dssInstance.Circuit.NextElement()

        return

    def createEdges(self):
        PDElement = self.__dssInstance.Circuit.FirstPDElement()
        Term = self.__dssInstance.PDElements.FromTerminal()
        Phs = int(self.__dssInstance.CktElement.BusNames()[0].split('.')[1])
        isOpen = self.__dssInstance.CktElement.IsOpen(Term, Phs)
        Enabled =  self.__dssInstance.CktElement.Enabled(),
        if Enabled and not isOpen:
            Term = self.__dssInstance.PDElements.FromTerminal()
            PhsTo = self.__dssInstance.CktElement.BusNames()[1].split('.')[1:]
            PhsFrom = self.__dssInstance.CktElement.BusNames()[0].split('.')[1:]
            if PhsTo != PhsFrom:
                print(self.__dssInstance.CktElement.Name(), PhsFrom, PhsTo)
            while PDElement:
                I = self.__dssInstance.CktElement.CurrentsMagAng()
                I = sum(I[:int(len(I)/2)][::2])
                ElementData = {
                    'Name': self.__dssInstance.CktElement.Name().split('.')[1].lower(),
                    'Class': self.__dssInstance.CktElement.Name().split('.')[0].lower(),
                    'BusFrom': self.__dssInstance.CktElement.BusNames()[0].split('.')[0].lower(),
                    'BusTo': self.__dssInstance.CktElement.BusNames()[1].split('.')[0].lower(),
                    'I': I,
                    'Imax':self.__dssInstance.CktElement.NormalAmps(),
                }
                self.dssGraph.add_edge(ElementData['BusFrom'], ElementData['BusTo'], ElementData)
                PDElement = self.__dssInstance.Circuit.NextPDElement()
                if self.__dssInstance.CktElement.Name().split('.')[0].lower() == 'load':
                    print("Yo")
        return

    def getNetworkData(self):
        Nodes = self.__dssCircuit.AllNodeNames()
        Voltages = self.__dssCircuit.AllBusMagPu()
        Distances = self.__dssCircuit.AllNodeDistances()
        Losses = self.__dssCircuit.Losses()
        LineLosses = self.__dssCircuit.LineLosses()
        Power = self.__dssCircuit.TotalPower()
        subLosses = self.__dssCircuit.SubstationLosses()
        Data = [Nodes, Voltages, Distances, Losses, LineLosses, Power, subLosses]
        return Data

    def updateGraphAttributes(self, Data):
        Nodes, Voltages, Distances, Losses, LineLosses, Power, subLosses = Data
        P = sum(Power[0::2]) / 1000
        Q = sum(Power[1::2]) / 1000
        Pl = sum(Losses[0::2]) / 1000
        Ql = sum(Losses[1::2]) / 1000
        self.dssGraph.graph['nLoops'] = self.__dssInstance.Topology.NumLoops()
        self.dssGraph.graph['nIslands'] = self.__dssInstance.Topology.NumIsolatedBranches()
        self.dssGraph.graph['nBuses'] = self.__dssCircuit.NumBuses()
        self.dssGraph.graph['nLoads'] = self.__dssInstance.Loads.Count()
        self.dssGraph.graph['nPVsystems'] = self.__dssInstance.PVsystems.Count()
        #dssGraph.graph['nStorages'] = self.__dssInstance.PVsystems.Count() # TODO: Add code for storage here
        self.dssGraph.graph['Vmin'] = min([i for i in Voltages if i != 0])
        self.dssGraph.graph['Vmax'] = max(Voltages)
        self.dssGraph.graph['Ptotal'] = P
        self.dssGraph.graph['Qtotal'] = Q
        self.dssGraph.graph['Ploss'] = Pl
        self.dssGraph.graph['Qloss'] = Ql
        self.dssGraph.graph['PlossLine'] = sum(LineLosses[0::2])
        self.dssGraph.graph['QlossLine'] = sum(LineLosses[1::2])
        self.dssGraph.graph['Length'] = max(Distances)
        self.dssGraph.graph['% Loss'] = abs(Pl + 1j * Ql)/1000 / \
                                   abs(P + 1j * Q) * 100

    def Set_Parameter(self,Class, Name, Param, Value):
        self.__dssInstance.Circuit.SetActiveElement(Class + '.' + Name)
        print('Active element: ', self.__dssInstance.Element.Name())
        print('Class: ', Class)
        print('Element: ', Name)
        self.__dssInstance.utils.run_command('{}.{}.{} = {}'.format(Class, Name, Param, Value))
        rValue = self.Get_Parameter(Class, Name, Param)

        if Value == rValue:
            return True
        else:
            self.Logger.Log(3, 'Error with command: {}.{}.{} = {}'.format(Class, Name, Param, Value))
            return False

    def Get_Bus_Variable(self,BusName,  VarName):
        self.__dssInstance.Circuit.SetActiveBus(BusName)
        try:
            funct = getattr(self.__dssInstance.Bus, VarName)
            return funct()
        except:
            self.Logger.Log(3, 'Error reading bus property: {}.{}'.format(BusName, VarName))
            return None

    def Get_CktElm_Variable(self, Class, Name, Param):
        self.__dssInstance.Circuit.SetActiveElement(Class + '.' + Name)
        print('Active element: ', self.__dssInstance.Element.Name())
        if self.__dssInstance.Element.Name().lower() == Class.lower() + '.' + Name.lower():
            try:
                funct = getattr(self.__dssInstance.CktElement, Param)
                return funct()
            except:
                self.Logger.Log(3, 'Error reading circuit element property: {}.{}.{}'.format(Class, Name, Param))
                return None

    def Get_Parameter(self,Class, Name, Param):
        self.__dssInstance.Circuit.SetActiveElement(Class + '.' + Name)
        print('Active element: ', self.__dssInstance.Element.Name())
        print('Class: ', Class)
        print('Element: ', Name)
        if self.__dssInstance.Element.Name().lower() == Class.lower() + '.' + Name.lower():
            print('Updating parameter value')
            x = self.__dssInstance.Properties.Value(Param)
            print(x)
            try:
                return float(x)
            except:
                return x
        else:
            self.Logger.Log(3, 'Could not set ' + Class + '.' + Name + ' as active element.')
            return None

    def clear_network_data(self):
        EdgeData = {
            'Class': [],
            'Name': [],
            'Xs': [],
            'Ys': [],
            'Phases': [],
            'fromBus': [],
            'toBus': [],
            'X': [],
            'Y': [],
            'V': [],
            'D': [],
            'kVbase': [],
            'I': [],
            'Imax': [],
            'Vmax': [],
            'Vmin': [],
        }
        NodeData = {
            'X': [],
            'Y': [],
            'PV': [],
            'Storage': [],
        }
        return EdgeData, NodeData

    def CreateGlobalDataSource(self):
        self.Logger.Log(0, 'Creating global data souce.')
        EdgeData, NodeData = self.clear_network_data()
        for N1, N2 in self.dssGraph.edges():
            Xs = [self.dssGraph.node[N1]['X'], self.dssGraph.node[N2]['X']]
            Ys = [self.dssGraph.node[N1]['Y'], self.dssGraph.node[N2]['Y']]
            if 0 not in Xs and 0 not in Ys:
                V = ['%0.3f' % x for x in self.dssGraph.node[N2]['V']]
                VV = []
                VV.extend(self.dssGraph.node[N2]['V'])
                VV.extend(self.dssGraph.node[N1]['V'])
                VV = [x for x in VV if x != 0]
                EdgeData['Class'].append(self.dssGraph[N1][N2]['Class'])
                EdgeData['Name'].append(self.dssGraph[N1][N2]['Name'])
                EdgeData['Xs'].append(Xs)
                EdgeData['Ys'].append(Ys)
                EdgeData['Phases'].append(self.toPhases(self.dssGraph.node[N1]['Phs']))
                EdgeData['fromBus'].append(N1)
                EdgeData['toBus'].append(N2)
                EdgeData['X'].append(Xs[1])
                EdgeData['Y'].append(Ys[1])
                EdgeData['V'].append(V)
                EdgeData['Vmax'].append(max(VV))
                EdgeData['Vmin'].append(min(VV))
                EdgeData['I'].append(self.dssGraph[N1][N2]['I'])
                EdgeData['Imax'].append(self.dssGraph[N1][N2]['Imax'])
                EdgeData['D'].append(self.dssGraph.node[N2]['D'])
                EdgeData['kVbase'].append(self.dssGraph.node[N2]['kVbase'])

        for Node in self.dssGraph.nodes():
            NodeData['X'].append(self.dssGraph.node[Node]['X'])
            NodeData['Y'].append(self.dssGraph.node[Node]['Y'])
            NodeData['PV'].append(self.dssGraph.node[Node]['PV'])
            NodeData['Storage'].append(self.dssGraph.node[Node]['Storage'])

        return EdgeData, NodeData

    def toPhases(self, phList):
        phases = ''
        if 0 in phList:
            phases+='A'
        if 1 in phList:
            phases+='B'
        if 2 in phList:
            phases+='C'
        return phases

    def RunYearlySimulation(self, TimeStep, PVsystem, Pass, sD, eD):
        self.YearlySimulatonResults = {
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

        self.__dssInstance.Circuit.SetActiveClass('priceshape')
        Elem = self.__dssInstance.Circuit.FirstElement()
        Price = self.__dssInstance.Properties.Value('price')
        Price = Price.replace('[ ', '').replace(']', '').split(' ')
        Price = [float(x) for x in Price]

        for day in range(sD, eD):
            for hour in np.arange(0, 23, TimeStep):
                if Pass == 0:
                    self.dssSolver.SolveAt2(day, hour)
                else:
                    self.dssSolver.SolveAt(day, hour)
                hourOfYear = day * 24 + int(hour)
                self.UpdateResults(day, hour, PVsystem, Price[hourOfYear])
        return self.YearlySimulatonResults


    def UpdateResults(self, day, hour, PVsystem, Price):
        self.__dssInstance.Circuit.SetActiveElement(PVsystem)
        if self.__dssInstance.CktElement.Name().lower() == PVsystem.lower():
            Bus = self.__dssInstance.CktElement.BusNames()[0].split('.')[0]
            self.__dssInstance.Circuit.SetActiveBus(Bus)
            if self.__dssInstance.Bus.Name().lower() == Bus.lower():
                vBase = self.__dssInstance.Bus.kVBase() * 1000
                V = self.__dssInstance.CktElement.VoltagesMagAng()[0::2]
                puVoltages = self.__dssInstance.Circuit.AllBusMagPu()
                self.YearlySimulatonResults['Ptotal'].append(sum(self.__dssInstance.Circuit.TotalPower()[0::2]))
                self.YearlySimulatonResults['Qtotal'].append(sum(self.__dssInstance.Circuit.TotalPower()[1::2]))
                self.YearlySimulatonResults['Vmax'].append(max(puVoltages))
                self.YearlySimulatonResults['Vmin'].append(min([i for i in puVoltages if i != 0]))
                self.YearlySimulatonResults['PlTotal'].append(sum(self.__dssInstance.Circuit.Losses()[0::2]))
                self.YearlySimulatonResults['QlTotal'].append(sum(self.__dssInstance.Circuit.Losses()[1::2]))
                self.YearlySimulatonResults['Pelm'].append(sum(self.__dssInstance.CktElement.Powers()[0::2]))
                self.YearlySimulatonResults['Qelm'].append(sum(self.__dssInstance.CktElement.Powers()[1::2]))
                self.YearlySimulatonResults['VelmMax'].append(max(V) / vBase)
                self.YearlySimulatonResults['VelmMin'].append(min([i for i in V if i != 0]) / vBase)
                self.YearlySimulatonResults['Time'].append(day + hour / 24)
                self.YearlySimulatonResults['LMP'].append(Price)
                if 'pvsystem.' in PVsystem.lower():
                    self.YearlySimulatonResults['SOC'].append(0)
                else:
                    print(self.__dssInstance.Properties.Value('%stored'))
                    self.YearlySimulatonResults['SOC'].append(float(self.__dssInstance.Properties.Value('%stored')))
        return

    def YearlyRunPass(self, sDay,eDay, TimeStep ,ClassName, ElmName):
        FullName = '{}.{}'.format(ClassName, ElmName)
        if type(sDay) == datetime.datetime:
            sDate = sDay.date()
            eDate = eDay.date()
        else:
            sDate = sDay
            eDate = eDay

        sD = (sDate - datetime.date(sDate.year, 1, 1)).days
        eD = (eDate - datetime.date(eDate.year, 1, 1)).days
        self.Logger.Log(1, "Time series simulation starting at day {} and will and on day {}".format(sD, eD))

        # Base case yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 1")
        self.dssSolver.UpdateSettings()
        Base_case_results = self.RunYearlySimulation(TimeStep, FullName, 0, sD, eD)
        self.Logger.Log(1, "Complete")

        # Unity PF yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 2")
        if 'pvsystem.' in FullName.lower():
            print('PV enabled 1')
            self.PVinverterEnabled(ElmName, 'False')
            print('PV enabled 2')
            self.Set_Parameter('PVsystem', ElmName, 'pf', 1)
            print('PV enabled 3')
            self.dssSolver.UpdateSettings()
            print('PV enabled 4')
            legacy_results = self.RunYearlySimulation(TimeStep, FullName, 1, sD, eD)
            self.Logger.Log(1, "Complete")
        else:
            legacy_results = {
                'Ptotal': [0] * len(Base_case_results['Ptotal']),
                'Qtotal': [0] * len(Base_case_results['Ptotal']),
                'Vmax': [0] * len(Base_case_results['Ptotal']),
                'Vmin': [0] * len(Base_case_results['Ptotal']),
                'PlTotal': [0] * len(Base_case_results['Ptotal']),
                'QlTotal': [0] * len(Base_case_results['Ptotal']),
                'Pelm': [0] * len(Base_case_results['Ptotal']),
                'Qelm': [0] * len(Base_case_results['Ptotal']),
                'VelmMax': [0] * len(Base_case_results['Ptotal']),
                'VelmMin': [0] * len(Base_case_results['Ptotal']),
                'Time': [0] * len(Base_case_results['Ptotal']),
                'LMP': [0] * len(Base_case_results['Ptotal']),
                'SOC': [0] * len(Base_case_results['Ptotal']),
            }
            pass

        #Control yearly pass
        self.Logger.Log(1, "Running time series simulation: Pass 3")
        if 'pvsystem.' in FullName.lower():
            self.Set_Parameter('PVsystem', ElmName, 'Enabled', 'False')
            self.Logger.Log(1, "Nolo")
        else:
            self.Logger.Log(1, "Yolo")
            self.Set_Parameter('Storage', ElmName, 'Enabled', 'False')
        self.dssSolver.UpdateSettings()
        smart_ctrl_results = self.RunYearlySimulation(TimeStep, FullName, 2, sD, eD)
        self.Logger.Log(1, "Complete")

        # Reset Controls
        if 'pvsystem.' in FullName.lower():
            self.PVinverterEnabled(ElmName, 'True')
        else:
            self.Set_Parameter('Storage', ElmName, 'Enabled', 'True')

        self.dssSolver.UpdateSettings()
        #Update plots

        return Base_case_results, legacy_results, smart_ctrl_results

    def PVinverterEnabled(self, ElmName, State):
        self.__dssInstance.Circuit.SetActiveClass('InvControl')
        try:
            Element = self.__dssInstance.Circuit.FirstElement()
            while Element:
                ElementName = self.__dssInstance.CktElement.Name().split('.')
                ControlledPVs =  self.Get_Parameter(ElementName[0], ElementName[1], 'PVsystemList')
                Ctrls = ControlledPVs.strip('[').strip(']').split(' ')
                if ElmName.lower() in Ctrls:
                    self.__dssInstance.utils.run_command(
                        ElementName[0] + '.' + ElementName[1] + '.Enabled = {}'.format(State)
                    )
                    self.Logger.Log(1,"{}.{}'s state changed to: {}".format(ElementName[0],ElementName[1], State))
                Element = self.__dssInstance.Circuit.NextElement()
        except:
            self.Logger.Log(0, "No instance of type {} in the current model.".format('InvControl'))
        return

    def doYearlyCalculations(self , Ulb, Uub, EnergyCorrCoef, R_basecase, R_legacy, R_smart):
        #
        Pcomps = self.GetEnergyComponents([R_basecase['Ptotal'],
                                           R_legacy['Ptotal'],
                                           R_smart['Ptotal']],
                                          EnergyCorrCoef)

        Qcomps = self.GetEnergyComponents([R_basecase['Qtotal'],
                                           R_legacy['Qtotal'],
                                           R_smart['Qtotal']],
                                          EnergyCorrCoef)

        PVEnergyS = abs(sum(R_basecase['Pelm'])) * EnergyCorrCoef
        PVEnergyU = abs(sum(R_legacy['Pelm'])) * EnergyCorrCoef

        KWHlossS = abs(sum(R_basecase['PlTotal'])) / 1000 * EnergyCorrCoef
        KWHlossU = abs(sum(R_legacy['PlTotal'])) / 1000 * EnergyCorrCoef
        KWHlossD = abs(sum(R_smart['PlTotal'])) / 1000 * EnergyCorrCoef


        SysviolationsDataLB_S = self.GetVoltageViolationMetrics([R_basecase['Vmin'],
                                                                 R_legacy['Vmin'],
                                                                 R_smart['Vmin']],
                                                                Ulb, 'LB')
        SysviolationsDataUB_S = self.GetVoltageViolationMetrics([R_basecase['Vmax'],
                                                                 R_legacy['Vmax'],
                                                                 R_smart['Vmax']],
                                                                Uub, 'UB')
        PVviolationsDataLB_S = self.GetVoltageViolationMetrics([R_basecase['VelmMin'],
                                                                R_legacy['VelmMin'],
                                                                R_smart['VelmMin']],
                                                                Ulb, 'LB')
        PVviolationsDataUB_S = self.GetVoltageViolationMetrics([R_basecase['VelmMax'],
                                                                R_legacy['VelmMax'],
                                                                R_smart['VelmMax']],
                                                                Uub, 'UB')

        return [PVEnergyS, PVEnergyU], PVEnergyU - PVEnergyS, [KWHlossS, KWHlossU, KWHlossD], Pcomps, Qcomps,\
               [SysviolationsDataLB_S[1], SysviolationsDataUB_S[1]], [PVviolationsDataLB_S[1], SysviolationsDataUB_S[1]], \
               [PVviolationsDataLB_S[2], PVviolationsDataUB_S[2]]

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

if __name__ == "__main__":

    class Logger:
        def __init__(self):
            return
        def Log(self, X, Text):
            print(X, Text)
    Settings = {
        'Start Day'              : 20,
        'End Day'                : 22,
        'Hour'                   : 1,
        'Step resolution (min)'  : 60,
        'Max Control Iterations' : 200,
        'Simulation Type'        : 'Time series',
        'DSS File'               : r'C:\Users\alatif\Desktop\wm_opendss_files\ojo_caliente/ojo_caliente.dss'
        }
    x = Logger()
    PyDSS = createInstance(Settings, x)
    PyDSS.dssSolver.UpdateSettings()
    for i in range(24):
        PyDSS.dssSolver.SolveAt2(100,i)

        dss.Circuit.SetActiveClass('priceshape')
        Elem = dss.Circuit.FirstElement()
        Price = dss.Properties.Value('price')
        Price = Price.replace('[ ', '').replace(']', '').split(' ')
        print(Price)
        #Price = Price.replace('[', '').replace(']', '').split(' ')
        #Price = [float(x) for x in Price]

    # PVproperties = {
    #     'bus1'      : 'dln_2546328.3',
    #     'phases'    : '1',
    #     'kv'        : '0.12',
    #     'kVA'       : '10',
    #     'Pmpp'      : '10',
    #     'kvarLimit' : '4.4',
    #     '%Cutin'    : '0.1',
    #     '%Cutout'   : '0.1',
    #     'irradiance': '1',
    #     'Yearly'    : '2603482_pv_mult',
    # }
    # print(run_command('LoadShape.2611201_pv_mult.action=normalize'))
    # PyDSS.Add_Element('PVsystem', '2611201_pv_mult', PVproperties)
    # print(run_command('New PVsystem.2611201_pv_mult bus1=dln_2546328.3 KVA=10 kv=0.12 yearly=2603482_pv_mult'))
    # #PyDSS.Add_Element('PVsystem', 'test', PVproperties)
    # PyDSS.dssSolver.UpdateSettings()
    # for i in range(24):
    #     PyDSS.dssSolver.SolveAt(100,i)
    #     print(PyDSS.Get_Bus_Variable('dln_2546328', 'puVmagAngle'))

