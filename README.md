1. Setup:
	- Create a venv in order to be able to run this codebase.
		- (all from within this directory...)
		- Create the venv: `python3 -m venv ./evolving_venv`
		- Activate the venv: `source evolving_venv/bin/activate`
		- Install necesary libraries via pip: 
			- `pip install midiutil`
			- `pip install flask`
2. Running the application (stand-alone):
	- Navigate to the folder above the one containing this README-SETUP.txt file; the one containing the 'evolving_venv' folder.
	- Activate the venv with the following command:
	```
	source evolving_venv/bin/activate
	```
	- Navigate to the folder containing the application.py file.
	- execute: `python3 application.py` 
3. Running the application (via website):
	- Navigate to the folder above the one containing this README-SETUP.txt file; the one containing the 'evolving_venv' folder.
	- Activate the venv with the following command:
	```
	source evolving_venv/bin/activate
	```
	- Navigate to the folder containg this README-SET.txt file
	- Execute the following to start the Flask Development server:
	```
	python app.py
	```
	- The website can be viewed at this URL: localhost:5000