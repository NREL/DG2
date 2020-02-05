from PyPVtoolkit.PyDSSlite.Components import SolveMode
from opendssdirect.utils import run_command
import opendssdirect as dss
import networkx as nx
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
        self.__dssInstance.utils.run_command('{}.{}.{} = {}'.format(Class, Name, Param, Value))
        print(Class, Name, Param, Value)
        rValue = self.Get_Parameter(Class, Name, Param)
        print(rValue)
        if str(Value).lower() == rValue.lower():
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
        if self.__dssInstance.Element.Name().lower() == Class.lower() + '.' + Name.lower():
            try:
                funct = getattr(self.__dssInstance.CktElement, Param)
                return funct()
            except:
                self.Logger.Log(3, 'Error reading circuit element property: {}.{}.{}'.format(Class, Name, Param))
                return None

    def Get_Parameter(self,Class, Name, Param):
        self.__dssInstance.Circuit.SetActiveElement(Class + '.' + Name)
        if self.__dssInstance.Element.Name() == (Class + '.' + Name):
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

