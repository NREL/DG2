
def GetSolver(SimulationSettings ,dssInstance, Logger):
    SolverDict = {
        'Snapshot'    : __Shapshot,
        'Time series' : __TimeSeries,
    }
    try:
        Solver = SolverDict[SimulationSettings['Simulation Type']](dssInstance, SimulationSettings, Logger)
        return Solver
    except:
        Logger.Log(3, 'pyDSS solver object could not be created')
        return -1

class __TimeSeries:
    def __init__(self, dssInstance, SimulationSettings, Logger):
        Logger.Log(1, 'Created time series solver')
        self.MaxItrs = SimulationSettings['Max Control Iterations']
        self.Hour = int(SimulationSettings['Hour'])
        self.Sec = (SimulationSettings['Hour'] - self.Hour) * 60 * 60
        self.StartDay = SimulationSettings['Start Day']
        self.sStepRes = int(SimulationSettings['Step resolution (min)']*60)
        self.__dssInstance = dssInstance
        self.__dssSolution = dssInstance.Solution
        self.__dssSolution.Mode(2)
        self.__dssSolution.Hour(self.StartDay * 24 + self.Hour)
        self.__dssSolution.Seconds(self.Sec)
        self.__dssSolution.Number(1)
        self.__dssSolution.StepSize(0)
        self.__dssSolution.MaxControlIterations(self.MaxItrs)
        return

    def SolveAt2(self, Day, Hour):
        hr = int(Hour)
        sc = int((Hour - hr) * 60 * 60)
       #self.__dssInstance.utils.run_command('set mode=yearly number=1 MaxIter=30 MaxControlIteration=30')
        self.__dssInstance.utils.run_command('set time=({},{})'.format(Day * 24 + hr - 1, sc))
        print(self.__dssInstance.utils.run_command('solve'))

    def SolveAt(self, Day, Hour):
        hr = int(Hour)
        sc = int((Hour - hr) * 60 * 60)
        self.__dssSolution.Hour(Day * 24 + hr)
        self.__dssSolution.Seconds(sc)
        self.__dssSolution.Number(1)
        self.__dssSolution.StepSize(0)
        self.__dssSolution.Solve()
        return

    def IncStep(self):
        self.__dssSolution.StepSize(self.sStepRes)
        self.__dssSolution.Solve()

    def reSolve(self):
        self.__dssSolution.StepSize(0)
        self.__dssSolution.StepSizeMin(0)
        self.__dssSolution.SolveNoControl()

    def UpdateSettings(self):
        print("Updating settings")
        self.__dssInstance.utils.run_command('set mode = snap')
        self.__dssInstance.utils.run_command('set time=(0,0)')
        print(self.__dssInstance.utils.run_command('solve'))
        self.__dssInstance.utils.run_command('set mode = yearly')
        self.__dssInstance.utils.run_command('set demand = true')
        self.__dssInstance.utils.run_command('set number = 1')
        self.__dssInstance.utils.run_command('set DIVerbose = true')
        self.__dssInstance.utils.run_command('set ControlMode = Time')
        self.__dssInstance.utils.run_command('set MaxIter=30')
        self.__dssInstance.utils.run_command('set MaxControlIteration={}'.format(self.MaxItrs))
        #self.__dssInstance.utils.run_command('Set Year = 1 Number = 720')
        #self.__dssInstance.utils.run_command('solve')

    def Reset(self):
        self.UpdateSettings()
        self.SolveAt2(0,0)
        return

    def Mode(self):
        return self.__dssSolution.Mode()

class __Shapshot:
    def __init__(self, dssInstance, SimulationSettings, Logger):
        Logger.Log(1, 'Created snapshot solver')
        hr = int(SimulationSettings['Hour'])
        sc = int((SimulationSettings['Hour'] - hr) * 60 * 60)
        self.__dssInstance = dssInstance
        self.__dssSolution = dssInstance.Solution
        self.__StartDay = int(SimulationSettings['Start Day'])
        self.__sStepRes = int(SimulationSettings['Step resolution (min)'] * 60)
        self.__dssSolution.Mode(5)
        self.__dssSolution.Hour(self.__StartDay * 24 + hr)
        self.__dssSolution.Number(1)
        self.__dssSolution.StepSize(self.__sStepRes)
        self.__dssSolution.MaxControlIterations(SimulationSettings['Max Control Iterations'])
        return

    def solve(self, DayOfYear=None, Hour=None, stepSize=None):
        print(self.__dssSolution.SystemYChanged())
        hr = int(Hour)
        sc = int((Hour - hr) * 60 * 60)
        if DayOfYear and Hour:
            print('Day of year: ', DayOfYear)
            print('Hour of day: ', Hour)
            self.__dssSolution.Mode(0)
            self.__dssSolution.Hour(DayOfYear * 24 + hr)
            self.__dssSolution.StepSize(0)
            self.__dssSolution.StepSizeMin(0)
            self.__dssSolution.Solve()
        return





