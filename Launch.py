import os
from flask import Flask,render_template,request
from bokeh.plotting import figure
from bokeh.io import output_file,show
from bokeh.embed import components
from bokeh.client import push_session, pull_session
from bokeh.embed import server_session
import PyPVtoolkit.Application
from bokeh.io import curdoc
import zipfile
import json
import time

doc = curdoc()
app = Flask(__name__, template_folder='templates')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("REPlan_layout.html")

@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT,'files/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        network = filename.split('.')[0]
        destination = "/".join([target,filename])
        print(destination)
        file.save(destination)

        zip_ref = zipfile.ZipFile(destination, 'r')
        zip_ref.extractall(target)
        zip_ref.close()
    time.sleep(5)
    session = pull_session(session_id=None, url='http://localhost:5006/DG2')
    time.sleep(5)
    script = server_session(session_id=session.id, url='http://localhost:5006/DG2')
    return render_template("REPlan_layout_after_upload.html", script=script, template="Flask")

if __name__ == "__main__":
    import subprocess
    BokehServer = subprocess.Popen(["bokeh", "serve", "DG2.py",
                                    "--allow-websocket-origin=localhost:5000",
                                    "--allow-websocket-origin=localhost:5006"], stdout=subprocess.PIPE)
    time.sleep(10)
    app.run(debug=True, host='localhost')

