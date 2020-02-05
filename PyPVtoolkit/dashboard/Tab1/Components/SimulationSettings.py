import PyPVtoolkit
from bokeh.layouts import row, column
from bokeh.models.widgets import TextInput,Button, Select
import os

class Create():
    def __init__(self, opendss_path):
        projects = os.listdir(opendss_path)
        projects = [x for x in projects if '.' not in x]
        if len(projects) > 0:
            files_path = os.path.join(opendss_path, projects[0])
            files = list(filter(lambda x: '.dss' in x, os.listdir(files_path)))
        else:
            projects = ['']
            files = ['']

        self.Textbox_dssPath = Select(title="Networks", value=projects[0], options=projects)
        # self.Textbox_dssPath = TextInput(placeholder="OpenDSS project path",
        #                                  value='')
        self.Textbox_dssPath.width = 400

        self.Opendssfilepath = Select(title="OpenDSS files", value=files[0], options=files)
        # self.Textbox_dssPath = TextInput(placeholder="OpenDSS project path",
        #                                  value='')
        self.Opendssfilepath.width = 400

        self.load_Path = TextInput(placeholder="Load allocation file path",
                                         value='', )
        self.load_Path.disabled = True
        self.load_Path.width = 400


        self.LogCombo = Select(title="Logging level", value="debug", options=['debug', 'info', 'warning', 'error'])

        self.Button_loadDSSproject = Button(label="Load project", button_type="success")
        self.Button_loadDSSproject.on_click(self.LoadDSSproject)

        self.saveChangesBtn = Button(label="Save changes", button_type="success")
        self.clearChangesBtn = Button(label="Clear changes", button_type="success")
        self.Allocate_load = Button(label="Reallocate Load", button_type="success")

        self.saveChangesBtn.disabled = True
        self.clearChangesBtn.disabled = True
        Opts= row(self.Textbox_dssPath, self.Opendssfilepath,self.load_Path)
        buttons = row(self.Button_loadDSSproject, self.Allocate_load, self.saveChangesBtn, self.clearChangesBtn)
        updatemodel = row(self.LogCombo)
        self.final_layout = column(Opts, buttons, updatemodel)

        return

    def layout(self):
        return self.final_layout

    def LoadDSSproject(self):
        return