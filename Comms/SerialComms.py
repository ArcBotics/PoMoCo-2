import sys, os, time, serial, threading
import multiprocessing, Queue

# chose an implementation, depending on os
if os.name == 'nt': #sys.platform == 'win32':
    from serial.tools.list_ports_windows import *
elif os.name == 'posix':
    from serial.tools.list_ports_posix import *
else:
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))

import PoMoCoModule

class SerialLink(PoMoCoModule.Node):
    def __init__(self):
        super(SerialLink, self).__init__()
        threading.Thread.__init__(self)
        self.moduleType = "comms"
        self.baud_rate = 9600
        self.ports = None
        self.ser = None
        self.connected = False
        self.connectedPort = None
        self.timeout_period = 8
        self.serial_incoming = []
        self.last_received = ""
        self.buffer = ""
        self.debug = True
        self.autoConnStr = ""
        
        self.port_priority = ["VID:PID=2341:8036",
                         "USB",
                         "BT",
                         "",
                         ]
                    
        self.priority_desc = ["Servotor32 (VID/PID matched)",
                              "USB Serial device",
                              "Windows Bluetooth Serial device",
                              "Unknown Type Serial Port",
                              ]
                              
        self.moduleType = 'comms'
        PoMoCoModule.Node.modules[self.moduleType] = self.inNoteQueue

        self.start()

    def __del__(self):
        self.ser.close()
        
    def run(self):
    #main thread after init
        startTime = time.clock()
        while True:
            #every 1 second(s) poll the available serial ports
            if time.clock()-startTime >= 1.0:
                self.portRefresh()
                startTime = time.clock()
            try:
                note = self.inNoteQueue.get(block=False)
                self.processNote(note)
            except Queue.Empty: # nothing in the Queue
                #process the serial buffer
                self.readIncomingSerial()
                #process incoming serial messages
                self.processSerial()
            time.sleep(0) # keeps infinite loop from hogging all the CPU

    def portRefresh(self):
    #check the existing ports and see if any new ones have popped up
    #notify the GUI of any changes
        self.debug = False
        oldPorts = []
        if self.ports:
            oldPorts = self.ports[:]
        self.scanForPorts()
        if self.ports != oldPorts:
            if self.debug: print "difference!"
            portList = ""
            for port in self.ports:
                portList+=port['name']+","
            if len(portList) > 0:
                portList = portList[:-1] #remove that last comma
            self.writeAndSendNote("SetPortList", portList, "controller")
        
    def processNote(self, note):
    #process an incoming PoMoCo message
        #print self.moduleType,"Received Note:",note.sender,"->",note.receiver,"-",note.type,":",note.message
        if note.type == "RequestConnectPort":
            connectPort = note.message
            self.connect(connectPort)
            
        if note.type == "RequestAutoConnect":
            self.autoConnStr = note.message
            self.autoConnect()

        if note.type == "SendMessage":
            self.sendSerial(note.message)

        if note.type == "RequestPortList":
            print "comms got port list request"
            self.scanForPorts()
            portList = ""
            for port in self.ports:
                portList+=port['name']+","
            if len(portList) > 0:
                portList = portList[:-1] #remove that last comma
            print note.sender
            self.writeAndSendNote("SetPortList", portList, note.sender)

    def processSerial(self):
        # transfer the serial stack to the string
        while len(self.serial_incoming) > 0:
            print "From Controller:", self.serial_incoming.pop()
        # send the string stack to the controller for processing
            
    def readIncomingSerial(self):
    #process incoming serial messages
        if self.connected and self.ser:
            try:
                self.buffer = self.buffer + self.ser.read(self.ser.inWaiting())
            except IOError as detail:
                print "Serial connection unexpectedly terminated:",detail
                self.ser = None
                self.connected = False
                self.writeAndSendNote("SetFirmwareV","?","controller")
                self.writeAndSendNote("SetConnectionState","inactive","controller")                
            if '\n' in self.buffer:
                lines = self.buffer.split('\n') # Guaranteed to have at least 2 entries
                last_received = lines[-2]
                self.serial_incoming.append(last_received)
                #If the Arduino sends lots of empty lines, you'll lose the
                #last filled line, so you could make the above statement conditional
                #like so: if lines[-2]: last_received = lines[-2]
                self.buffer = lines[-1]  
                return True
        return False

    def sendSerial(self, toSend):
        if self.ser:
            #print "sending "+str(self.ser.name)+": '"+str(toSend.strip('\n'))+"'"
            pass
        else:
            #print "sending (not connected): '"+str(toSend.strip('\n'))+"'"
            pass
        if self.ser:
            if self.ser.writable:
                self.ser.write(str(toSend))
                return True
        return False
            
    def scanForPorts(self):
    #scans for and sorts ports
        unsorted_ports = []
        for portPath, desc, hwid in comports():
            portPath = portPath.replace("/dev/cu.","/dev/tty.",1)
            port = {"name":portPath, "desc":desc, "hwid":hwid}
            unsorted_ports.append(port)

        priority_val = 0
        sorted_ports = []
        while (len(unsorted_ports) > 0) and (priority_val < len(self.port_priority)):
            for port in unsorted_ports:
                # see if the string is part of the description
                if self.port_priority[priority_val] in port['hwid']:
                    #print self.port_priority[priority_val],"in", port['hwid']
                    if port not in sorted_ports:
                        sorted_ports.append(port)
                else:
                    pass
                    #print self.port_priority[priority_val],"not in", port['hwid']
            priority_val += 1

        if len(sorted_ports) > 0:
            self.ports = sorted_ports
            if self.debug: 
                print "Available Serial Ports:"
                print "-"*20
            for port in self.ports:
                if self.debug: 
                    print "Name:",port['name']
                    print "Description:",port['desc']
                    print "Hardware ID:",port['hwid']
                    print "-"*20
        else:
            if self.debug: 
                print "No serial ports available!"            
                print "Are the drivers installed?"
                print "Device powered/plugged in?"
                print "Bluetooth paired?" 
            self.ports = None
            
    def autoConnect(self):
    #automatically connect to the "best" available port
        if self.connected:
            print "Already connected"
            return True
        self.scanForPorts()
        if self.ports:
            for port in self.ports:
                print "trying", port['name']
                self.connect(port['name'])
                if self.connected:
                    return True
        return None

    def connect(self, portName):
    #connect to a specifically named port
        self.connected = False
        self.ser = None
        
        result = ""
        try:
            self.ser = serial.Serial(portName, baudrate=self.baud_rate, timeout=self.timeout_period, writeTimeout=self.timeout_period)
            if not self.ser.isOpen():
                print "Connection failed:",portName,"has already been opened by another process"
                self.ser = None
                return False
            self.ser.flush()
            time.sleep(0.1)
            self.sendSerial('V\n')
            time.sleep(1)
            result = self.ser.readline()
            if self.autoConnStr in result:
                print "Connected to",portName
                firmware = result.rstrip('\n\r')
                print "Firmware Version:",firmware
                self.writeAndSendNote("SetFirmwareV",firmware,"controller")
                self.ser.flush()
                self.connected = True
                self.writeAndSendNote("SetConnectionState","active","controller")
            else:
                self.ser = None
                print "Device not on",portName    
        except serial.serialutil.SerialException as detail:
            print "Serial Exception:",portName,",",sys.exc_info()
            self.ser = None
        except:
            print "Connection failed:",portName,",",sys.exc_info()
            self.ser = None
            

            
if __name__ == '__main__':
    serialObject = Serial()
    serialObject.autoConnect()
    serialObject.sendSerial('C\n')
    serialObject.sendSerial('K\n')
    serialObject.sendSerial('V\n')