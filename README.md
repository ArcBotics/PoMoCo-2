# PoMoCo-2
PoMoCo 2 - Position and Motion Controller

PoMoCo 2.0 runs on modules, and an asynchronous note-passing system between them.
Each module is a child of the Node class, which itself is a child of the thread class.
Each module runs as its own thread with its own incoming notes queue. 
Every node can talk to every other node by putting notes into its incoming queue.
When a Node starts, it puts a pointer to its own incoming queue into a dictionary shared 
between the nodes. 

Communications between modules
GUI -> robot: changes to servo positions, offsets, on/off, robot moves
GUI -> controller: request connection, request auto-connection, record arduino moves
robot -> controller: changes to servo positions, offsets, on/off
robot -> GUI: when the robot moves, the servo moves are sent back to the GUI
controller -> comms: request connection changes, raw message data
comms -> controller: updates about connection status, firmware version updates, raw message data
controller -> GUI: updates about connection status, firmware version updates, recorded arduino moves

Uses Python 2.7, PySerial and wxPython

Installation instructions:
Windows
Install Python 2.7
https://www.python.org/ftp/python/2.7.9/python-2.7.9.msi
Install pySerial
https://pypi.python.org/packages/any/p/pyserial/pyserial-2.7.win32.exe
Instal wxPython
http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe


OSX
-python 2.7 already installed-
in terminal, run: pip install pyserial
Then install:
http://downloads.sourceforge.net/project/wxpython/wxPython/3.0.2.0/wxPython3.0-osx-3.0.2.0-carbon-py2.7.dmg

make sure not to install wxPython Cocoa! Its outdated, and will result in weird glitches when dragging icons


Run the PoMoCo.py file to start