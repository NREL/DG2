Documentation for (DG)²
**************************
.. toctree::
   :maxdepth: 2
   :caption: Contents:

About (DG)²
===========
(DG)² is an impact analysis tool... 


Installation
===================

(DG)² can be installed by typing the following command on the command prompt:

clone the repository using the following command

.. code-block:: python

	Git clone asdasd
	

Alternately, you can choose to download the repository directly from https://github.com/nrel/DG2. Once the repository has been cloned, go to the folder containing setup.py file. In the command prompt enter the followiing command. 


.. code-block:: python
	
	conda create -n DG2 python=3.7
	conda activate DG2
	pip install -e.
	

Once the installation ios complete, the (DG)²server can be launched by running the following command.

.. code-block:: python
	
	python launch.py
	
if installed correctly you should be able to see the lines appear on the console.

.. code-block:: python

	Starting REPlan Server

	(dg2) C:\Users\alatif\Desktop\(DG)2\replan-master>python launch.py
	2020-01-31 12:04:38,940 Starting Bokeh server version 0.12.7 (running on Tornado 4.4.2)
	2020-01-31 12:04:38,944 Bokeh app running at: http://localhost:5006/DG2
	2020-01-31 12:04:38,945 Starting Bokeh server with process id: 26380
	 * Serving Flask app "launch" (lazy loading)
	 * Environment: production
	   WARNING: This is a development server. Do not use it in a production deployment.
	   Use a production WSGI server instead.
	 * Debug mode: on
	 * Restarting with stat
	2020-01-31 12:04:50,590 Starting Bokeh server version 0.12.7 (running on Tornado 4.4.2)
	2020-01-31 12:04:50,592 Cannot start Bokeh server, port 5006 is already in use
	 * Debugger is active!
	 * Debugger PIN: 290-557-408
	 * Running on http://localhost:5000/ (Press CTRL+C to quit)



	
Running simulatons
===================
.. toctree::
   :maxdepth: 1

   Load existing model
   Uploading models
   Running simulations
   
   
License
=======

BSD 3-Clause License

Copyright (c) 2018, Alliance for Sustainable Energy LLC, All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Contact
=======
Questions? Please send an email to aadil.latif@nrel.gov or aadil.latif@gmail.com
