import GUI
import wx
import threading, os, sys, multiprocessing, Queue
import time
import PoMoCoModule

sys.path.append('Robots/Hexy V1/Moves')
sys.path.append('Robots/Hexy V1/')
sys.path.append('Comms')
sys.path.append('Controllers')

import robot
import SerialComms
import Servotor32

class GUIProcess(PoMoCoModule.Node):
    def __del__():
        if self.ser:
            if self.ser.isOpen():
                self.ser.close()
                
    def __exit__(self, type, value, traceback):
        if self.ser and self.ser.isOpen():
            self.ser.close()
         
    def __init__(self, GUI):
        super(GUIProcess, self).__init__()
        threading.Thread.__init__(self)
        self.GUI = GUI
        self.moduleType = 'GUI'
        PoMoCoModule.Node.modules[self.moduleType] = self.inNoteQueue
        self.start()

    def run(self):
        while True:
            try:
                message = self.inNoteQueue.get(block=False)
                self.processNote(message)
            except Queue.Empty:
                time.sleep(0) # keeps infinite loop from hogging all the CPU

    def processNote(self, note):
        #print self.moduleType,"Received Note:",note.sender,"->",note.receiver,"-",note.type,":",note.message
        if note.type == "SetServoPos":
            num, pos = note.message.split(',')
            wx.CallAfter(self.GUI.UpdateServoPos, int(num), float(pos))
            
        if note.type == "SetServoOffset":
            num, offset = note.message.split(',')
            wx.CallAfter(self.GUI.UpdateServoOffset, int(num), float(offset))
            
        if note.type == "SetServoActive":
            num, state = note.message.split(',')
            servoState = False
            if state == "active":
                servoState = True
            if state == "inactive":
                servoState = False
            wx.CallAfter(self.GUI.UpdateServoActive, int(num), servoState)
            
        if note.type == "SetConnectionState":
            connState = False
            if note.message == "active":
                connState = True
            if note.message == "inactive":
                connState = False
            self.connectionState = connState
            wx.CallAfter(self.GUI.UpdateConnectionState, connState)
            
        if note.type == "SetPortList":
            portList = note.message.split(',')[:]
            wx.CallAfter(self.GUI.UpdatePortList, portList)

        if note.type == "SetFirmwareV":
            firmwareVersion = note.message
            wx.CallAfter(self.GUI.UpdateFirmwareVersion, firmwareVersion)

        if note.type == "UpdateArduinoCode":
            arduinoCode = note.message
            wx.CallAfter(self.GUI.UpdateArduinoCode, arduinoCode)

if __name__ == '__main__':
    app = wx.App()
    comms = SerialComms.SerialLink()
    controller = Servotor32.Servotor32()
    robot = robot.robot()
    __builtins__.hexy = robot
    __builtins__.robot = robot
    __builtins__.move = robot.RunMove
    __builtins__.floor = 60
    GUI = GUI.MainGui()
    GUIProc = GUIProcess(GUI)
    GUI.LoadRobot("Robots/Hexy V1/")
    
    app.MainLoop() # main loop of GUI needs to be executed in main thread, or OSX crashes
    del GUI
    del robot
    del controller
    del comms
    os._exit(0)
    #start GUI
    #have GUI ask serial 

    