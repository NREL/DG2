import numpy as np
def fix_load_buses(Loadfile, newLoadfile, Voltages, Coordinates):
	Coordinates = np.genfromtxt(Coordinates, delimiter=',', dtype=str)
	Vdata = np.genfromtxt(Voltages, delimiter=',', dtype=str)
	Vdata[:,0]= np.array([x.lower().strip('"') for x in Vdata[:, 0]])
	r, c = Vdata.shape
	SecondaryNodes = {}
	for i in range(1, r):
		Bus = Vdata[i, 0].strip(' ')
		BaseKV = float(Vdata[i, 1].strip(' '))
		if BaseKV < 1:
			IndicesTR = np.where(Coordinates[:,0] == Bus)
			IndexTR = list(IndicesTR[0])[0]
			SecondaryNodes[Bus] = {
				"X"   : float(Coordinates[IndexTR,1].strip(' ')),
				"Y"   : float(Coordinates[IndexTR,2].strip(' ')),
				"KV"  : BaseKV,
			}

	wfile = open(newLoadfile, 'w')
	file = open(Loadfile, 'r')
	Loads_LV = 0
	Loads_MV = 0
	Loads = 0
	for line in file:
		Loads += 1
		LineStr = line.split(' ')
		Node1 = LineStr[2].replace('bus1=', '')
		Bus1 = Node1.split('.')[0]
		Phases = '.'.join(Node1.split('.')[1:])
		nPhases = len(Node1.split('.')[1:])
		CoordinateIndex = list(np.where(Coordinates[:, 0] == Bus1))[0]
		Coordainates = Coordinates[CoordinateIndex, :][0]
		X = float(Coordainates[1].strip(' '))
		Y = float(Coordainates[2].strip(' '))
		Distance = []
		for newBus, Coords in SecondaryNodes.items():
			X1 = Coords['X']
			Y1 = Coords['Y']
			D = np.sqrt((X - X1)**2 + (Y - Y1)**2)
			Distance.append([newBus, D, Coords['KV']])

		DistArray = np.array(Distance)
		DistList = [float(x) for x in DistArray[:,1]]
		MimimunDistance = min(DistList)
		Index = DistList.index(MimimunDistance)
		selectedBus = DistArray[Index,0]
		KVbase = float(DistArray[Index,2])
		SelectedNode = '{}.{}'.format(selectedBus, Phases)
		LineStr[2] = 'bus1={}'.format(SelectedNode)
		if nPhases == 1:
			LineStr[5] = 'kv={}'.format(KVbase/1.732)
		else:
			LineStr[5] = 'kv={}'.format(KVbase)

		LoadStr = ' '.join(LineStr)
		wfile.write(LoadStr)
		print(LoadStr)



	print('Total loads: ', Loads)
	print('Total MV loads: ', Loads_MV)
	print('Total LV loads: ', Loads_LV)

fix_load_buses('Loads.dss', 'newLoads.dss', 'ojo_caliente_EXP_VOLTAGES.CSV', 'Bus_Coordinates.csv')