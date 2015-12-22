import time, math, threading
import threading, os
import multiprocessing, Queue
import PoMoCoModule
# modifies how smoothly the servos move
#smoother means more processing power, and fills the serial line
#lower if movements start to slow down, or get weird
#Anything higher than 50 is pointless (maximum refresh of standard servos)
stepPerS = 3
floor = 60
import sys

sys.path.append('Moves')

# sys.path.append('Moves') # include the moves folder
# global function for running move files
# def move(moveName):
# print "Preforming move:",moveName
# moveName = moveName.replace(' ','')
# if moveName in sys.modules:
# reload(sys.modules[moveName])
# else:
# __import__(moveName)

class runMovement(threading.Thread):
    def __init__(self, function, *args):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.start()

    def run(self):
        self.function(*self.args)


class Servo():
    def __init__(self, parent, num, deg=0, joint="", active=False, offset=0):
        self.num = num
        self.deg = deg
        self.offset = offset
        self.active = active
        self.joint = joint
        self.parent = parent

    def SetDeg(self, deg):
        #print self.num,deg
        if deg == "sleep":
            self.SetActive(False)
        else:
            deg = float(deg)
            if deg > 90:
                self.deg = 90
            elif deg < -90:
                self.deg = -90
            else:
                self.deg = deg
            self.parent.writeAndSendNote("SetServoPos", "%d,%.1f" % (self.num, self.deg), "GUI")
            self.parent.writeAndSendNote("SetServoPos", "%d,%.1f" % (self.num, self.deg), "controller")


    def GetDeg(self):
        return self.deg

    def SetOffset(self, offset):
        self.offset = offset
        #print self.num,offset
        self.parent.writeAndSendNote("SetServoOffset", "%d,%.1f" % (self.num, self.offset), "GUI")
        self.parent.writeAndSendNote("SetServoOffset", "%d,%.1f" % (self.num, self.offset), "controller")


    def GetOffset(self):
        return self.offset

    def GetNum(self):
        return self.num

    def SetActive(self, active=True):
        if active:
            outState = "active"
        else:
            outState = "inactive"
        self.parent.writeAndSendNote("SetServoActive", str(self.num) + "," + outState, "GUI")
        self.parent.writeAndSendNote("SetServoActive", str(self.num) + "," + outState, "controller")


class robot(PoMoCoModule.Node):
    def __init__(self):
        super(robot, self).__init__()
        threading.Thread.__init__(self)

        self.moduleType = 'robot'
        self.outgoingNoteQueue = Queue.Queue()
        PoMoCoModule.Node.modules[self.moduleType] = self.inNoteQueue
        self.servos = []
        for i in range(32):
            self.servos.append(Servo(self, i))

        self.RF = leg(self, 'rightFront', self.servos[24], self.servos[25], self.servos[26])
        self.RM = leg(self, 'rightMid', self.servos[20], self.servos[21], self.servos[22])
        self.RB = leg(self, 'rightBack', self.servos[16], self.servos[17], self.servos[18])

        self.LF = leg(self, 'leftFront', self.servos[7], self.servos[6], self.servos[5])
        self.LM = leg(self, 'leftMid', self.servos[11], self.servos[10], self.servos[9])
        self.LB = leg(self, 'leftBack', self.servos[15], self.servos[14], self.servos[13])

        self.legs = [self.RF,
                     self.RM,
                     self.RB,
                     self.LF,
                     self.LM,
                     self.LB]

        self.neck = neck(self, self.servos[31])

        self.tripod1 = [self.RF, self.RB, self.LM]
        self.tripod2 = [self.LF, self.LB, self.RM]

        self.start()

    def writeAndSendNote(self, type, message, receiver):
        toSend = PoMoCoModule.Note()
        toSend.sender = "robot"
        toSend.type = type
        toSend.message = message
        toSend.receiver = receiver
        PoMoCoModule.Node.modules[toSend.receiver].put(toSend)


    def run(self):
        while True:
            try:
                message = self.inNoteQueue.get(block=False)
                self.processNote(message)
            except Queue.Empty:
                pass

            time.sleep(0)  # keeps infinite loop from hogging all the CPU

    def processNote(self, note):
        #print "Note:",note.sender,"->",note.receiver,"-",note.type,":",note.message
        if note.type == "RequestDisableAll":
            for servo in self.servos:
                servo.active = False
            self.writeAndSendNote("RequestDisableAll", "", "controller")

        if note.type == "RequestEnableAll":
            for servo in self.servos:
                servo.active = True
            self.writeAndSendNote("RequestEnableAll", "", "controller")

        if note.type == "RequestCenterAll":
            for servo in self.servos:
                servo.deg = 0
            self.writeAndSendNote("RequestCenterAll", "", "controller")

        if note.type == "SetServoPos":
            num, pos = note.message.split(',')
            num = int(num);
            pos = float(pos)
            self.servos[num].SetDeg(pos)

        if note.type == "SetServoOffset":
            num, offset = note.message.split(',')
            num = int(num);
            offset = float(offset)
            self.servos[num].SetOffset(offset)

        if note.type == "SetServoActive":
            num, inState = note.message.split(',')
            num = int(num);
            outState = False
            if inState == "active":
                outState = True
            if inState == "inactive":
                outState = False
            self.servos[num].SetActive(outState)

        if note.type == "RunMove":
            moveName = note.message[:]  # copy the move name locally
            print "running", moveName
            self.RunMove(moveName)

    def RunMove(self, moveName):
        moveName = moveName.replace(' ', '')
        if moveName in sys.modules:
            reload(sys.modules[moveName])
        else:
            __import__(moveName)


class neck():
    def __init__(self, parent, servo):
        self.servo = servo
        self.parent = parent

    def set(self, deg):
        self.servo.SetDeg(deg)


class leg():
    def __init__(self, parent, name, hipServo, kneeServo, ankleServo):
        self.parent = parent
        self.name = name
        self.hipServo = hipServo
        self.kneeServo = kneeServo
        self.ankleServo = ankleServo

    def hip(self, deg):
        self.hipServo.SetActive()
        self.hipServo.SetDeg(deg)

    def knee(self, deg):
        self.kneeServo.SetActive()
        self.kneeServo.SetDeg(deg)

    def ankle(self, deg):
        self.ankleServo.SetActive()
        self.ankleServo.SetDeg(deg)

    def setHipDeg(self, endHipAngle, stepTime=1):
        runMovement(self.setHipDeg_function, endHipAngle, stepTime)

    def setFootY(self, footY, stepTime=1):
        runMovement(self.setFootY_function, footY, stepTime)

    def replantFoot(self, endHipAngle, stepTime=1):
        runMovement(self.replantFoot_function, endHipAngle, stepTime)

    def setHipDeg_function(self, endHipAngle, stepTime):
        startHipAngle = self.hipServo.GetDeg()
        hipDiff = endHipAngle - startHipAngle
        self.hip(endHipAngle)
        
        steps = range(int(stepPerS*stepTime))
        for i, t in enumerate(steps):
            #move a small amount each step
            hipAngle = (hipDiff / len(steps)) * (i + 1)    
            self.hip(startHipAngle + hipAngle)
            
            #wait for next cycle
            time.sleep(float(stepTime) / float(stepPerS))

    def setFootY_function(self, footY, stepTime):
        # TODO: max steptime dependent
        # TODO: implement time-movements the servo commands sent for far fewer
        #       total servo commands

        if (footY < 75) and (footY > -75):
            kneeAngle = math.degrees(math.asin(float(footY) / 75.0))
            ankleAngle = 90 - kneeAngle

            self.knee(kneeAngle)
            self.ankle(-ankleAngle)

    def replantFoot_function(self, endHipAngle, stepTime):
        # Smoothly moves a foot from one position on the ground to another in time seconds
        # TODO: implement time-movements the servo commands sent for far fewer total servo
        #       commands

        currentHipAngle = self.hipServo.GetDeg()

        hipMaxDiff = endHipAngle - currentHipAngle

        steps = range(int(stepPerS))
        for i, t in enumerate(steps):
            

            hipAngle = (hipMaxDiff / len(steps)) * (i + 1)

            #calculate the absolute distance between the foot's highest and lowest point
            footMax = 0
            footMin = floor
            footRange = abs(footMax - footMin)

            #normalize the range of the hip movement to 180 deg
            try:
                anglNorm = hipAngle * (180 / (hipMaxDiff))
            except:  #dvide by zero error
                anglNorm = hipAngle * (180 / (1))  #divide by one instead

            #base footfall on a sin pattern from footfall to footfall with 0 as the midpoint
            footY = footMin - math.sin(math.radians(anglNorm)) * footRange

            #set foot height
            self.setFootY_function(footY, stepTime=0)
            hipAngle = currentHipAngle + hipAngle

            self.hip(hipAngle)

            #wait for next cycle
            time.sleep(float(stepTime) / float(stepPerS))


if __name__ == '__main__':
    hexy = robot()