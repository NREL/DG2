from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

class Create():
    def __init__(self, Sliders):
        self.Dmax = 0
        X1 = {
            'Element'  : [0],
            'Voltage'  : [[0, 0]],
            'distance' : [[0, 0]],
            'color' : ['red']
        }
        X2 = {
            'Element': [0],
            'Voltage': [[0, 0]],
            'distance': [[0, 0]],
            'color': ['green']
        }
        X3 = {
            'Element': [0],
            'Voltage': [[0, 0]],
            'distance': [[0, 0]],
            'color': ['blue']
        }
        self.LimitsData = {
            'V': [[0, 0], [0, 0]],
            'D': [[0, 0], [0, 0]],
            'C': ['grey', 'grey']
        }
        self.Vll, self.Vul, self.Lul = Sliders
        self.DataSourceA = ColumnDataSource(X1)
        self.DataSourceB = ColumnDataSource(X2)
        self.DataSourceC = ColumnDataSource(X3)
        self.LimitsSource = ColumnDataSource(self.LimitsData)


        self.VDplot = figure(plot_width=1160, plot_height=580, title="Network overview")
        self.VDplot.toolbar.logo = None
        self.VDplot.background_fill_color = "#fafafa"
        self.LineplotA = self.VDplot.multi_line(xs='distance', ys='Voltage', source=self.DataSourceA,
                                                 legend='Phase A', line_color="color")
        self.LineplotB = self.VDplot.multi_line(xs='distance', ys='Voltage', source=self.DataSourceB,
                                                legend='Phase B', line_color="color")
        self.LineplotC = self.VDplot.multi_line(xs='distance', ys='Voltage', source=self.DataSourceC,
                                                legend='Phase C', line_color="color")

        self.Limits = self.VDplot.multi_line(xs='D', ys='V', source=self.LimitsSource,
                                                legend='Voltage limits', line_color="C")


        self.VDplot.xaxis.axis_label = 'Distance [miles]'
        self.VDplot.yaxis.axis_label = 'Voltage [p.u]'
        self.VDplot.legend.location = "top_right"
        self.VDplot.legend.click_policy = "hide"
        self.final_layout = self.VDplot

        return

    def UpdateLimits(self):
        self.LimitsData = {
            'V': [[self.Vll.value, self.Vll.value], [self.Vul.value, self.Vul.value]],
            'D': [[0, self.Dmax], [0, self.Dmax]],
            'C': ['grey', 'grey']
        }
        self.LimitsSource.data = self.LimitsData
        return

    def layout(self):
        return self.final_layout

    def UpdatePlot(self, dssInstance, Graph):
        print('Updating VD plot')
        AllPhaseData= [
            {
                'Element': [],
                'Voltage': [],
                'distance': [],
                'color' : []
            },
            {
                'Element': [],
                'Voltage': [],
                'distance': [],
                'color': []
            },
            {
                'Element': [],
                'Voltage': [],
                'distance': [],
                'color': []
            }]
        Nodes = [[x.split('.')[0], int(x.split('.')[1])-1] for x in dssInstance.Circuit.AllNodeNames()]
        Voltages = dssInstance.Circuit.AllBusMagPu()
        Distances = dssInstance.Circuit.AllNodeDistances()
        self.Dmax = max(Distances)

        colors = {
            0: 'red',
            1: 'green',
            2: 'blue',
        }

        dNodes = {
            0 : {},
            1 : {},
            2 : {},
        }

        for N, V, D in zip(Nodes, Voltages, Distances):
            if V != 0 and isinstance(V, float):
                i = N[1]
                dNodes[i][N[0].lower()] = [V, D]

        for N1, N2 in Graph.edges():
            for Phs in range(3):
                if N1.lower() in dNodes[Phs] and N2.lower() in dNodes[Phs]:
                    AllPhaseData[Phs]['Element'].append(Graph[N1][N2]['Name'])
                    AllPhaseData[Phs]['Voltage'].append([dNodes[Phs][N1][0], dNodes[Phs][N2][0]])
                    AllPhaseData[Phs]['distance'].append([dNodes[Phs][N1][1], dNodes[Phs][N2][1]])
                    AllPhaseData[Phs]['color'].append(colors[Phs])

        self.DataSourceA.data = AllPhaseData[0]
        self.DataSourceB.data = AllPhaseData[1]
        self.DataSourceC.data = AllPhaseData[2]

        self.LineplotA.data_source.data = AllPhaseData[0]

        self.UpdateLimits()

        return  print('VD Update Complete')


