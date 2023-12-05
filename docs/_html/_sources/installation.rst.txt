Installation
==============================================

1. Prerequisites
-----------------

Python and R are needed. It has been tested with python 3.8, 3.9, 3.10, 3.11 and R 4.3


2. Why R is needed ?
---------------------

DroneMD uses geoflow in some parts such as:

* ISO19115 XML generation

* (optional since Friday 13th of October 2023) upload to Zenodo : implemented in Python with contact file with relevant informations (display name, orcid, organisation)

3. Installation
----------------

Easy way : 
(Optionnal: create a python venv, please watch python documentation)

.. code-block:: console

	git clone https://github.com/IRDG2OI/DroneMD.git
	cd DroneMD
	pip install -r requirements


4. Configuration
----------------

4.1 OpenDroneMap server and credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Copy settings_sample.py to settings.py

* Fill required information such as server endpoint, username, password


4.2 Zenodo token
^^^^^^^^^^^^^^^^

4.2.1 Use settings.py from 4.1

4.2.2 Use a dotenv file inside geoflow folder


5. Usage
--------

Please follow python notebook's
