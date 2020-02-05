
import PyPVtoolkit.Application
from bokeh.io import curdoc
import os

doc = curdoc()
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
opendss_path = os.path.join(APP_ROOT, 'files')
instance = PyPVtoolkit.Application.createApplication(doc, opendss_path)


