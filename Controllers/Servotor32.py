import threading, os, time
import multiprocessing, Queue
import PoMoCoModule

class Servotor32(PoMoCoModule.Node):
    def __init__(self):
        super(Servotor32, self).__init__()
        threading.Thread.__init__(self)
        self.servo_offset = {}
        self.servo_pos = {}
        self.servo_active = {}
        self.servo_min_uS = 500
        self.servo_max_uS = 2500
        self.firmwareV = ""
        self.portList = []
        self.connectionState = False
        self.recording = False

        self.recording_servo_move_time = []
        self.recording_servo_move_deg = []
        self.recording_servo_move_num = []
        
        for i in range(32):
            self.servo_offset[i] = 0
            self.servo_pos[i] = 1500
            self.servo_active[i] = False
        
        self.moduleType = 'controller'
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
        if note.type == "StartRecording":
            self.recording = True
            self.recordingName = note.message
            #clean up recording name

        if note.type == "StopRecording":
            if not self.recording:
                return False
            self.recording = False
            moveSteps = len(self.recording_servo_move_time)           

            times = self.recording_servo_move_time
            poses = self.recording_servo_move_deg
            servos = self.recording_servo_move_num

            name = self.recordingName.replace(' ', '_')
    
            rc = ""
            rc+= "#include <avr/pgmspace.h>"+"\n"
            rc+= "#define MOVE_"+name.upper()+"_SIZE "+str(moveSteps)+"\n\n"
            rc+= "const PROGMEM uint16_t move_"+name+"_time[MOVE_"+name.upper()+"_SIZE] = {"+"\n"
            for i,time in enumerate(times):
                rc+= str(int((time-times[0])*1000))
                if(i < moveSteps-1):
                    rc+= ", "
            rc+= "};"+"\n\n"

            rc+= "const PROGMEM uint8_t move_"+name+"_servo[MOVE_"+name.upper()+"_SIZE] = {"+"\n"
            for i,servo in enumerate(servos):
                rc+= str(servo)
                if(i < moveSteps-1):
                    rc+= ", "
            rc+= "};"+"\n\n"

            rc+= "const PROGMEM uint8_t move_"+name+"_pos[MOVE_"+name.upper()+"_SIZE] = {"+"\n"
            for i,pos in enumerate(poses):

                rc+= str(int(pos)/10)+" "
                if(i < moveSteps-1):
                    rc+= ", "
            rc+=  "};"+"\n\n"
            rc+=  ""+"\n"
            rc+=  "void move_"+name+"(){"+"\n"
            rc+=  "  int startTime = hexy.millis_new();"+"\n"
            rc+=  "  int currentTime = 0;"+"\n"
            rc+=  "  int last_update = 0;"+"\n"
            rc+=  "  for(int i=0; i<MOVE_"+name.upper()+"_SIZE; i++){" +"\n"
            rc+=  "    delayMicroseconds(10);"+"\n"
            rc+=  "    currentTime = hexy.millis_new() - startTime;"+"\n"
            rc+=  "    uint16_t move_time = pgm_read_word_near(move_"+name+"_time + i);"+"\n"
            rc+=  "    while(currentTime < move_time){"+"\n"
            rc+=  "      delayMicroseconds(10);"+"\n"
            rc+=  "      currentTime = hexy.millis_new() - startTime;"+"\n"
            rc+=  "    }"+"\n"
            rc+=  "    uint8_t servo_time = pgm_read_byte_near(move_"+name+"_servo + i);"+"\n"
            rc+=  "    uint8_t servo_pos  = pgm_read_byte_near(move_"+name+"_pos + i);"+"\n"
            rc+=  "    hexy.changeServo(servo_time, servo_pos*10);"+"\n"
            rc+=  "    last_update = currentTime;"+"\n"
            rc+=  "  }"+"\n"
            rc+=  "}"+"\n"
            rc+=  "//Move Size is "+str(moveSteps*4)+" bytes"+"\n"
            rc+=  "//Run this move by using:"+"\n"
            rc+=  "// move_"+name+"()"
            
            self.writeAndSendNote("UpdateArduinoCode",rc,"GUI")
            self.recording_servo_move_time = []
            self.recording_servo_move_deg = []
            self.recording_servo_move_num = []             

        if note.type == "RequestDisableAll":
            for i in range(32):
                self.servo_active[i] = False
            self.writeAndSendNote("SendMessage","K\n","comms")

        if note.type == "RequestEnableAll":
            for i in range(32):
                self.servo_active[i] = True
                self.SendServoState(i)

        if note.type == "RequestCenterAll":
            for i in range(32):
                self.servo_pos[i] = 1500
            self.writeAndSendNote("SendMessage","C\n","comms")

        if note.type == "RequestConnectPort":
            self.port = note.message
            self.writeAndSendNote("RequestConnectPort",note.message,"comms")
            
        if note.type == "RequestAutoConnect":
            self.writeAndSendNote("RequestAutoConnect","SERVOTOR","comms")

        if note.type == "RequestPortList":
            self.writeAndSendNote("RequestPortList","","comms")

        if note.type == "SetPortList":
            portList = note.message.split(',')[:]
            self.portList = portList
            self.writeAndSendNote("SetPortList",note.message,"GUI")
            
        if note.type == "SetServoPos":
            num, pos = note.message.split(',')
            num = int(num); pos = float(pos)
            self.servo_pos[num] = pos
            self.SendServoState(num)
            
        if note.type == "SetFirmwareV":
            self.firmwareV = note.message
            self.writeAndSendNote("SetFirmwareV",note.message,"GUI")
            
        if note.type == "SetServoOffset":
            num, offset = note.message.split(',')
            num = int(num); offset = float(offset) 
            self.servo_offset[num] = offset
            self.SendServoState(num)
 
        if note.type == "SetConnectionState":
            connState = False
            if note.message == "active":
                connState = True
            if note.message == "inactive":
                connState = False
            self.connectionState = connState
            self.writeAndSendNote("SetConnectionState",note.message,"GUI")
 
        if note.type == "SetServoActive":
            num, inState = note.message.split(',')
            num = int(num); 
            outState = False
            if "active" in inState:
                outState = True
            if "inactive" in inState:
                outState = False
            self.servo_active[num] = outState
            self.SendServoState(num)

    def SendServoState(self, num):
        #send raw command to comms
        outPos = self.servo_pos[num]
        outPos += self.servo_offset[num] #add offset
        outPos = outPos*(1000.0/90.0)+1500 #convert servo deg to uS pulse length

        #keep within pulse min/max
        if outPos > self.servo_max_uS:
            outPos = self.servo_max_uS
        if outPos < self.servo_min_uS:
            outPos = self.servo_min_uS

        if self.recording:
            if self.servo_active[num]:
                self.recording_servo_move_time.append(time.clock())
                outPos = self.servo_pos[num]
                outPos += self.servo_offset[num] #add offset
                outPos = outPos*(1000.0/90.0)+1500 #convert servo deg to uS pulse length 
                self.recording_servo_move_deg.append(outPos)
                self.recording_servo_move_num.append(num)

        if self.servo_active[num]:
            self.writeAndSendNote("SendMessage","#%02dP%04d\n"%(num,outPos),"comms")   
        else:
            self.writeAndSendNote("SendMessage","#%02dL\n"%(num),"comms") 
        
        
             
        
