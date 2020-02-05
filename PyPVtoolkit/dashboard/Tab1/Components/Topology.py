from bokeh.models import ColumnDataSource, HoverTool, TapTool,  CustomJS, ZoomInTool, ZoomOutTool
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON
from itertools import chain, combinations

from bokeh.models import GeoJSONDataSource, GMapOptions, LinearColorMapper, ColorBar
from bokeh.plotting import figure, gmap
from bokeh.sampledata.sample_geojson import geojson

class Create():
    def __init__(self, InverterSettings, StorageSettings):

        self.InvSettings = InverterSettings
        self.StorageSettings = StorageSettings
        self.clearTopologyData()

        self.source = ColumnDataSource(self.TopologyData)
        self.sourceNode = ColumnDataSource(self.NodeData)

        callback = CustomJS(code="""console.info("hello TapTool")""")
        tt = TapTool(callback=callback)

        map_options = GMapOptions(lat=36, lng=-106, map_type='roadmap', zoom=8)

        self.TopologyPlot = gmap('AIzaSyCiQT0TLjv0G25HN03eRJjQVfk6xRsMITo', map_options, plot_width=1200,
                                 plot_height=1000)

        self.TopologyPlot.toolbar.logo = None
        self.TPmulti_lines = self.TopologyPlot.multi_line(xs='Xs', ys='Ys', source=self.source, line_width=1,
                                                    line_alpha=1.0,line_color="darkblue", legend='Edges')

        self.TPcircles = self.TopologyPlot.circle(x='X', y='Y', source=self.sourceNode, legend='Nodes',
                                                  color='PV', radius=20, hover_color="red")

        self.TopologyPlot.toolbar.active_tap = 'auto'
        self.TopologyPlot.xaxis.axis_label = 'Longitude'
        self.TopologyPlot.yaxis.axis_label = 'Latitude'
        self.TopologyPlot.legend.location = "top_right"
        self.TopologyPlot.legend.click_policy = "hide"
        
        hoverBus = HoverTool(show_arrow=False, line_policy='next', tooltips=[
            ("Element", "@Name"),
            ("Class", "@Class"),
            ("Phases", "@Phases"),
            ("Distance", "@D")
        ])
        self.TopologyPlot.tools.append(hoverBus)
        self.TopologyPlot.tools.append(TapTool())
        self.TopologyPlot.tools.append(ZoomInTool())
        self.TopologyPlot.tools.append(ZoomOutTool())
        self.final_layout = self.TopologyPlot

        self.TPcircles.data_source.on_change('selected', self.test)

        #taptool = self.TopologyPlot.select(type=TapTool)
        #taptool.callback = callback

        return

    def clearTopologyData(self):
        self.TopologyData = {
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
        }

        self.NodeData = {
            'X': [],
            'Y': [],
            'PV': [],
            'Storage': [],
        }

        self.SelectedNode = self.TopologyData.copy()
        return

    def layout(self):
        return self.final_layout

    def createPlot(self, DataSource, NodeSource):
        self.TopologyData = DataSource.data
        self.NodeData = NodeSource.data
        self.source.data = self.TopologyData
        self.sourceNode.data = self.NodeData
    def test(self,attr,old,new):
        idx = self.source.selected['1d']['indices']

        if len(idx) == 1:
            i = idx[0]
            self.SelectedNode = {}
            for key in self.TopologyData:
                self.SelectedNode[key] = self.TopologyData[key][i]

            self.InvSettings.PVnameTextbox.value= 'pv_' + self.SelectedNode['toBus']
            self.InvSettings.BusNameTextbox.value = self.SelectedNode['toBus']

            self.StorageSettings.StoragenameTextbox.value = 'storage_' + self.SelectedNode['toBus']
            self.StorageSettings.BusNameTextbox.value = self.SelectedNode['toBus']

            #self.InvSettings.PVprofileTextbox.value = self.InvSettings.PVnameTextbox.value + '.csv'
            phases = self.getAllSubsets(self.SelectedNode['Phases'])
            self.InvSettings.Dropwown_phases.options = phases
            self.InvSettings.Dropwown_phases.value =  phases[0]

            self.StorageSettings.Dropdown_phases.options = phases
            self.StorageSettings.Dropdown_phases.value =  phases[0]

    def getAllSubsets(self, iterable):
        xs = list(iterable)
        sets = chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1))
        lists = [''.join(list(x)) for x in sets][1:]
        return lists

    def toPhases(self, phList):
        phases = ''
        if 0 in phList:
            phases+='A'
        if 1 in phList:
            phases+='B'
        if 2 in phList:
            phases+='C'
        return phases
