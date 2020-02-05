Load existing model
^^^^^^^^^^^^^^^^^^^^


	One the server is up and runnig, 
		To open the main dashboard, open address http://localhost:5006/DG2 and the following window should appear
	
.. figure::  _static/DG2_main_dashboard.png
   :align:   center
	

Click on the "Networks" combo box to select one of the preexisting networks. Once you choose a network, "OpenDSS files" combobox listings will refresh. Choose the master opendss file and click "Load project" to load the project.
The model will show on the  

.. figure::  _static/network.png
   :align:   center
	
	
To add PV and Storage elemets to an existing model, zoom into the network and click on a node. The selected node name will appear on the "Bus name" textbox. Choose all additional settings appropriately and cick "Add PV\Storage to this network". To verify that the elemnt has been added scroll down in log window. When set to debug mode, information on added element should appear. Added elements can be saved by clicking the "Save changes button at the top".