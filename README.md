# sim-eye
A project for producing low-cost, easily-assembled simulation eyes for use in ophthalmology training.

Note: the underlying model, the algorithm and the provided implementation are all being actively developed and have yet to be peer reviewed. They are provided here purely for information.

## Interactive examples
A simple interface to produce gores from example images or by uploading image files
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stuwilmur/sim-eye/HEAD?urlpath=voila%2Frender%2FInterface.ipynb)

A Jupyter Notebook to produce gores and try out the code yourself
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stuwilmur/sim-eye/HEAD?filepath=Interface.ipynb)

A Jupyter Notebook that explains some of the functions used
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stuwilmur/sim-eye/HEAD?filepath=Example.ipynb)
## Environment setup
Use of a virtual environment is recommended. Instructions are given for Anaconda, but use your preferred environment manager.

With Anaconda, in the top-level folder, create the environment (called appenv here: you can replace this with your preferred name for the environment):
```
conda create --name appenv python=3.7.11
```
Activate the environment
```
conda activate appenv
```
Finally, set up the environment by running environment.py:
```
python environment.py
```
Finally, once finished, deactivate the environment:
```
conda deactivate
```
## Run the application
Activate the environment (if not already active):
```
conda activate appenv
```
Navigate to the qt/ directory, then Run the application:
```
python app.py
```
To enable debug output, run using the debug flag `-d`:
```
python app.py -d
```
## Build environment setup
The requirements to build the application are slightly different to those above (cx_freeze is required, matplotlib is not).

With Anaconda, in the qt/ folder, create the environment (called installerenv here: you can replace this with your preferred name for the environment):
```
conda create --name installerenv python=3.7.11
```
Activate the environment
```
conda activate installerenv
```
Finally, set up the environment by running environment.py:
```
python environment.py
```
If desired, deactivate the environment:
```
conda deactivate
```
## Build the application
Build instructions are given for Windows and Mac OS. Before attempting any build, activate the installer environment:
```
conda activate installerenv
```
### Build executable
Build the application as an executable together with its dependencies; the command is common to either platform and will create the appropriate Windows/Mac executable:
```
python setup.py build
```
### Build Mac distribution
Create a .app bundle that may be distributed:
```
python setup.py bdist_mac
```
### Build Mac disk image
Build a Mac installer .dmg file (when opened this includes the Applications folder, allowing for easy drag and drop installation):
```
python setup.py bdist_dmg
```
### Build a Windows MSI (Microsoft Installer)
There is a Windows batch script app/build.bat which will perform the build. 
