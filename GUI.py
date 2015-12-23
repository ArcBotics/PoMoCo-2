import math, ConfigParser, ast, os, re, time, sys
import wx
import PoMoCoModule
import webbrowser
import wx.lib.agw.hyperlink as hl

if os.name == 'nt': #sys.platform == 'win32':
    from serial.tools.list_ports_windows import *
elif os.name == 'posix':
    from serial.tools.list_ports_posix import *
else:
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))
#naughty magic constants
ROBOTS_FOLDER_PATH = "Robots/"
ROBOT_FOLDER_PATH = "Robots/Hexy V1/"
#----------------------------------------------------------------------

def sendNote(note):
    PoMoCoModule.Node.modules[note.receiver].put(note)

def writeAndSendNote(type, message, receiver):
    toSend = PoMoCoModule.Note()
    toSend.sender = "GUI"
    toSend.type = type
    toSend.message = message
    toSend.receiver = receiver
    sendNote(toSend)

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        wx.CallAfter(self.out.WriteText, string)

class MainGui(wx.Frame):
    def __init__(self):
        
        super(MainGui, self).__init__(None, title="PoMoCo 2.0 - Position and Motion Controller", size=(730, 750))        
        self.initUI()
        #self.LoadRobot(ROBOT_FOLDER_PATH)
        self.Show()
        
    def initUI(self):
        self.topPanel =  wx.Panel(self)
        if os.name == 'nt':
                self.topPanel.SetFont(wx.Font(8,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="Helvetica"))
                self.SetBackgroundColour('LIGHT_GREY')
        elif os.name == 'posix':
            self.topPanel.SetFont(wx.Font(12,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="Helvetica"))
            self.SetBackgroundColour('LIGHT GREY')
        
        # robot select
        robotPanel  = wx.Panel(self.topPanel, size=(100,30))
        self.robots = RobotSelect(robotPanel)
        
        # side button for executing Moves
        movePanel = wx.Panel(self.topPanel, size=(100, 1000))
        self.moveButtons = MoveControls(movePanel)

        # controller control panel
        controllerPanel = wx.Panel(self.topPanel)
        controller = ControllerPanel(controllerPanel)
        controller.SetFirmwareV("?")
        self.controller = controller
        
        # Servo control and visualization area
        servoPanel  = wx.Panel(self.topPanel, size=(600, 521))
        self.servos = ServoWidget(servoPanel, 600, 521)

        # Servo show/hide toggle panel
        togglePanel = wx.Panel(self.topPanel)
        self.toggle = ServoToggle(togglePanel)
        for button in self.toggle.toggleButtons:
            button.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleServo)
        self.toggle.disableAllBtn.Bind(wx.EVT_BUTTON, self.OnDisableAll)
        self.toggle.centerAllBtn.Bind(wx.EVT_BUTTON, self.OnCenterAll)
        self.toggle.enableAllBtn.Bind(wx.EVT_BUTTON, self.OnEnableAll)
        self.toggle.offsetsEditBtn.Bind(wx.EVT_BUTTON, self.OnEditOffsets)

        #console panel
        self.consoleBox = wx.TextCtrl(self.topPanel, size=(380, 230), pos=(5,5), style=wx.TE_MULTILINE) 
        sys.stdout = RedirectText(self.consoleBox)       

        ### Main GUI Layout
        #Left Panel
        leftBox = wx.BoxSizer(wx.VERTICAL)
        leftBox.Add(robotPanel, proportion=0, border=5)
        leftBox.Add(movePanel, proportion=0, border=5)
        
        #Middle Panel
        middleBox = wx.BoxSizer(wx.VERTICAL)
        middleBox.Add(controllerPanel, proportion=0, border=5,flag=wx.CENTER)
        middleBox.Add(servoPanel, proportion=1, border=5,flag=wx.CENTER)
        middleBox.Add(togglePanel, proportion=0, border=5,flag=wx.CENTER)
        middleBox.AddSpacer(5, proportion=0)
        middleBox.Add(self.consoleBox, proportion=2, border=5, flag=wx.EXPAND|wx.CENTER)
        middleBox.AddSpacer(5, proportion=0)

        #Right Panel
        rightBox = wx.BoxSizer(wx.VERTICAL)
        rightBox.AddSpacer(5, proportion=0)
        
        #Top Panel
        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.Add(leftBox, proportion=0, flag=wx.EXPAND)
        topBox.Add(middleBox, proportion=1, flag=wx.EXPAND|wx.CENTER)
        topBox.Add(rightBox, proportion=0, flag=wx.EXPAND|wx.CENTER)
        

        self.topPanel.SetSizerAndFit(topBox)
        
        ### menu bar
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)
        
        fileMenu = wx.Menu()
        menubar.Append(fileMenu, '&File')
        saveServosMenuItem = fileMenu.Append(wx.NewId(), "Save Servos", "Save the state of the servos in a file")
        self.Bind(wx.EVT_MENU, self.OnSaveServos, saveServosMenuItem)
        loadServosMenuItem = fileMenu.Append(wx.NewId(), "Load Servos", "Load the state of the servos from a file")
        self.Bind(wx.EVT_MENU, self.OnLoadServos, loadServosMenuItem)
        exitMenuItem = fileMenu.Append(wx.NewId(), "Exit", "Exit the application")
        self.Bind(wx.EVT_MENU, self.OnExit, exitMenuItem)

        helpMenu = wx.Menu()
        menubar.Append(helpMenu, '&Help')
        servoCalibrationWizard = helpMenu.Append(wx.NewId(), "Calibrate Servo Wizard", "Calibrate the Robot's Servos")
        self.Bind(wx.EVT_MENU, self.LaunchServoCalibrationWizard, servoCalibrationWizard)
        usingPoMoCo = helpMenu.Append(wx.NewId(), "How to use PoMoCo", "Help on how to use PoMoCo")
        self.Bind(wx.EVT_MENU, self.UsingPoMoCo, usingPoMoCo)
        aboutPoMoCo = helpMenu.Append(wx.NewId(), "About PoMoCo", "Information about PoMoCo")
        self.Bind(wx.EVT_MENU, self.LaunchAboutPage, aboutPoMoCo)

    def UpdateServoPos(self, num, pos):
        for servo in self.servos.servos:
            if servo.num == num:
                servo.SetDeg(pos)
                servo.Refresh()

    def UpdateServoOffset(self, num, offset):
        for servo in self.servos.servos:
            if servo.num == num:
                servo.SetOffset(offset)
                servo.Refresh()

    def UpdateServoActive(self, num, state):
        for servo in self.servos.servos:
            if servo.num == num:
                servo.SetActive(state)
                servo.Refresh()

    def UpdateConnectionState(self, state):
        self.controller.SetConnectionStatus(state)

    def UpdatePortList(self, portList):
        self.controller.SetPortList(portList)

    def UpdateFirmwareVersion(self, version):
        self.controller.SetFirmwareV(str(version))
    
    def UpdateArduinoCode(self, code):
        self.moveButtons.updateCodeBox(code)

    def ServoCalibrationWizard(self, evt):
            pass

    def UsingPoMoCo(self, evt):
            webbrowser.open_new_tab("http://arcbotics.com/products/pomoco/how-to-use-pomoco/")

    def LaunchAboutPage(self, evt):
        self.aboutPageItem = AboutPage(self.topPanel, 1)

    def LaunchServoCalibrationWizard(self, evt):
        self.ServoCalibrationWizard = ServoCalibrationWizard(self.topPanel, 1)

    def LoadRobot(self, folderPath):
        Config = ConfigParser.ConfigParser()
        Config.read(folderPath+"robot.inf")
        
        self.robotName          = Config.get('robot', 'name')
        self.robotVersion       = Config.get('robot', 'version')
        self.controllerName     = Config.get('robot', 'controller')
        robotMovesFolder        = Config.get('robot', 'movesfolder')
        mainFileName            = Config.get('robot', 'mainfile')
        servoFileName           = Config.get('robot', 'servofile')
        imageFileName           = Config.get('robot', 'imagefile')
        
        self.moveButtons.SetMovesFolder(folderPath+robotMovesFolder)
        self.LoadServoConfig(folderPath + servoFileName)
        bmp = wx.Bitmap(folderPath+imageFileName)
        self.servos.SetBackgroundImage(bmp)
        
        self.Refresh()
        
    def OnExit(self, evt):
        self.Close()
        pass
        
    def OnSaveServos(self, evt):
        saveFileDialog = wx.FileDialog(self, "Save servo file", "", "", "inf files (*.inf)|*.inf", wx.FD_SAVE)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...               
        with open(saveFileDialog.GetPath(), 'w') as cfgFile:
            Config = ConfigParser.ConfigParser()
            for servo in self.servos.servos:
                numStr = "servo_%.2d"%int(servo.num)
                Config.add_section(numStr)
                Config.set(numStr,'num',servo.num)
                Config.set(numStr,'active',servo.active)
                Config.set(numStr,'deg',servo.deg)
                Config.set(numStr,'offset',servo.offset)
                Config.set(numStr,'visible',servo.visible)
                Config.set(numStr,'posX',servo.pos[0])
                Config.set(numStr,'posY',servo.pos[1])
                Config.set(numStr,'joint',servo.joint)
            Config.write(cfgFile)
            cfgFile.close()
        
    def OnLoadServos(self, evt):
        openFileDialog = wx.FileDialog(self, "Open servo file", "", "", "inf files (*.inf)|*.inf", wx.FD_OPEN)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...      
        self.LoadServoConfig(openFileDialog.GetPath())

    def LoadServoConfig(self, filePath):
        Config = ConfigParser.ConfigParser()
        Config.read(filePath)
        self.servos.servos = []
        for servo in Config.sections():
            num = int(Config.get(servo, 'num'))
            posX = int(Config.get(servo, 'posX'))
            posY = int(Config.get(servo, 'posY'))
            pos = (posX, posY)
            deg = float(Config.get(servo, 'deg'))
            offset = float(Config.get(servo, 'offset'))
            visible = ast.literal_eval(Config.get(servo, 'visible'))
            active = ast.literal_eval(Config.get(servo, 'active'))
            joint = str(Config.get(servo, 'joint'))
            self.servos.AddServo(num, pos, deg, offset, visible, active, joint)
            button = self.toggle.GetButton(num)
            if button:
                button.SetValue(visible)
        self.Refresh()      
        
    def OnToggleServo(self, evt):
        button = evt.GetEventObject()
        servo = self.servos.getServo(button.GetLabel())
        if servo:
            servo.visible = button.GetValue()
            servo.Render()
        else:
            servoNum = int(button.GetLabel())
            self.servos.AddServo(servoNum, (0,0), active=False)
        self.Refresh()
        
    def OnEditOffsets(self, evt):
        #show the servo offsets for writing
        for servo in self.servos.servos:
            servo.OffsetsToggle()
            servo.Render()
        self.Refresh()   
 
    def OnWriteOffsets(self, evt):
        #write that shit to the controller
        pass
        
    def OnDisableAll(self, evt):
        for servo in self.servos.servos:
            servo.SetActive(False)
            servo.Render()
        writeAndSendNote("RequestDisableAll", "", "robot")
        self.Refresh()

    def OnEnableAll(self, evt):
        for servo in self.servos.servos:
            servo.SetActive(True)
            servo.Render()
        writeAndSendNote("RequestEnableAll", "", "robot")
        self.Refresh()

    def OnCenterAll(self, evt):
        for servo in self.servos.servos:
            servo.SetDeg(0)
            servo.Render()
        writeAndSendNote("RequestCenterAll", "", "robot")
        self.Refresh()

class AboutPage(wx.Frame):

    def __init__(self,parent,id):
        wx.Frame.__init__(self, parent, id, 'Hexy Servo Calibration Wizard')
        wx.Frame.CenterOnScreen(self)
        self.panel = wx.Panel(self)

        self.vertical = wx.BoxSizer(wx.VERTICAL)

        text = "PoMoCo (Postition and Moction Controller) is an open-source robot control application developed by" \
               "ArcBotics LLC."
        part1 = wx.StaticText(self.panel, -1, text, style=wx.ALIGN_LEFT)

        hyper1 = hl.HyperLinkCtrl(self.panel, -1, "http://www.arcbotics.com\n", URL="http://www.arcbotics.com")

        text = "More information is available on it's homepage at:"
        part2 = wx.StaticText(self.panel, -1, text, style=wx.ALIGN_LEFT)

        hyper2 = hl.HyperLinkCtrl(self.panel, -1, "http://arcbotics.com/products/pomoco\n", URL="http://arcbotics.com/products/pomoco")

        text = "or at its github page at:"
        part3 = wx.StaticText(self.panel, -1, text, style=wx.ALIGN_LEFT)

        hyper3 = hl.HyperLinkCtrl(self.panel, -1, "http://github.com/arcbotics/github\n", URL="http://github.com/arcbotics/github")

        text = "PoMoCo is developed and released under the MIT License:\n" \
               "\n" \
               "The MIT License (MIT)\n" \
               "Copyright 2015 ArcBotics LLC.,\n" \
               "http://arcbotics.com\n" \
               "\n" \
               "Permission is hereby granted, free of charge, to any person obtaining a copy\n" \
               "of this software and associated documentation files (the 'Software'), to deal\n" \
               "in the Software without restriction, including without limitation the rights\n" \
               "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n" \
               "copies of the Software, and to permit persons to whom the Software is\n" \
               "furnished to do so, subject to the following conditions:\n" \
               "\n" \
               "The above copyright notice and this permission notice shall be included in\n" \
               "all copies or substantial portions of the Software.\n" \
               "\n" \
               "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n" \
               "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n" \
               "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n" \
               "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n" \
               "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n" \
               "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n" \
               "THE SOFTWARE.\n"


        part4 = wx.StaticText(self.panel, -1, text, style=wx.ALIGN_LEFT)


        self.vertical.Add(part1, border=5, flag=wx.LEFT|wx.RIGHT|wx.TOP)
        self.vertical.Add(hyper1, border=5, flag=wx.LEFT|wx.RIGHT)
        self.vertical.Add(part2, border=5, flag=wx.LEFT|wx.RIGHT)
        self.vertical.Add(hyper2, border=5, flag=wx.LEFT|wx.RIGHT)
        self.vertical.Add(part3, border=5, flag=wx.LEFT|wx.RIGHT)
        self.vertical.Add(hyper3, border=5, flag=wx.LEFT|wx.RIGHT)
        self.vertical.Add(part4, border=5, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)

        self.panel.SetSizerAndFit(self.vertical)
        self.Fit()
        self.Show()

class ServoCalibrationWizard(wx.Frame):
    def __init__(self,parent,id):
        self.activeServo = None
        self.parent = parent
        self.id = id
        self.jointCounter = 0
        self.servoOrder = [5,6,7, 9,10,11, 13,14,15, 18, 17, 16, 22,21,20, 26,25,24, 31]
        self.servoPosition = ["Front Left Foot", "Front Left Thigh", "Front Left Hip",
                             "Middle Left Foot", "Middle Left Thigh", "Middle Left Hip",
                             "Back Left Foot", "Back Left Thigh", "Back Left Hip",
                             "Back Right Foot", "Back Right Thigh", "Back Right Hip",
                             "Middle Right Foot", "Middle Right Thigh", "Middle Right Hip",
                             "Front Right Foot", "Front Right Thigh", "Front Right Hip",
                             "Head"]
        self.servoType = ["Foot", "Thigh", "Hip",
                          "Foot", "Thigh", "Hip",
                          "Foot", "Thigh", "Hip",
                          "Foot", "Thigh", "Hip",
                          "Foot", "Thigh", "Hip",
                          "Foot", "Thigh", "Hip",
                          "Head"]
        self.offsetChoices = {}

        self.servoMapLocations = {5:[53,47], 6:[70,70], 7:[85,91],
                                  9:[16,158], 10:[34,161], 11:[57,163],
                                  13:[64,261], 14:[80,245], 15:[94,229],
                                  18:[236,260], 17:[222,242], 16:[205,227],
                                  22:[289,157], 21:[264,158], 20:[240,160],
                                  26:[240,46], 25:[225,67], 24:[210,87],
                                  31:[148,89]}

        self.initUI()

        for servo in self.servoOrder:
            writeAndSendNote("SetServoActive", "%d,%s"%(servo, "inactive"), "robot")
        self.startCalibratingServo()



    def initUI(self):
        wx.Frame.__init__(self, self.parent, self.id, 'Hexy Servo Calibration Wizard')
        wx.Frame.CenterOnScreen(self)
        self.panel = wx.Panel(self)

        #Window text at top
        self.vertical = wx.BoxSizer(wx.VERTICAL)
        calibrationTitle = wx.StaticText(self.panel, -1, "Calibrating Hexy", style=wx.ALIGN_CENTER)
        font = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        calibrationTitle.SetFont(font)
        self.vertical.Add(calibrationTitle, border=10, flag=wx.ALL|wx.CENTER)

        normalFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        #Left panel - overall guide on which servo is being calibrated
        self.leftBox  = wx.BoxSizer(wx.VERTICAL)
        self.servoTitle = wx.StaticText(self.panel, -1, "Joint 00/18 - None - Servo -1", style=wx.ALIGN_CENTER)
        self.servoTitle.SetFont(normalFont)
        self.leftBox.Add(self.servoTitle, 0, wx.CENTER)

        #image of hexy being calibrated, showing which servo is currently being calibrated
        #self.calGuideImage = wx.StaticBitmap(self.panel, wx.ID_ANY,  wx.BitmapFromImage(wx.Image('Images//robot_300.jpg', wx.BITMAP_TYPE_ANY)))
        #self.leftBox.Add(self.calGuideImage, border=10, flag=wx.ALL)

       #alternate image that is capable of drawing servos onto
        self.drawPanel = wx.Panel(self, size=(300, 300))
        self.drawPanel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.drawPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.selectBlinkOn = True #controls whether the blinking servo is blinked on or off

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.flashCurrentServo, self.timer)
        self.timer.Start(300)

        self.leftBox.Add(self.drawPanel, border=10, flag=wx.ALL)

        #buttons to choose previous/next servo
        self.prevNextButtons = wx.BoxSizer(wx.HORIZONTAL)

        self.prevServoBtn = wx.Button(self.panel, label="Previous")
        self.prevServoBtn.Bind(wx.EVT_BUTTON, self.prevServo)
        self.prevNextButtons.Add(self.prevServoBtn, 0, wx.LEFT)

        self.nextServoBtn = wx.Button(self.panel, label="Next")
        self.nextServoBtn.Bind(wx.EVT_BUTTON, self.nextServo)
        self.prevNextButtons.Add(self.nextServoBtn, 0, wx.RIGHT)

        self.leftBox.Add(self.prevNextButtons, 1, wx.CENTER)

        #Right pane - calibrating the individual servo
        self.rightBox = wx.BoxSizer(wx.VERTICAL)
        instructionTitle = wx.StaticText(self.panel, -1, "Adjust below until aligned as shown", style=wx.ALIGN_CENTER)
        instructionTitle.SetFont(normalFont)
        self.rightBox.Add(instructionTitle, 0, wx.CENTER)

        img = wx.EmptyImage(300,300)
        self.jointGuideImage = wx.StaticBitmap(self.panel, wx.ID_ANY,  wx.BitmapFromImage(wx.Image('Images//Hip_Guide_300.jpg', wx.BITMAP_TYPE_ANY)))
        self.rightBox.Add(self.jointGuideImage, border=10, flag=wx.ALL)

        self.offsetAdjustSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.offsetSlider = wx.Slider(self.panel, id=0, value=0, minValue=-30.0, maxValue=30.0, size=(250, -1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        self.offsetSlider.Bind(wx.EVT_SLIDER, self.changeOffset)
        self.offsetAdjustSizer.Add(self.offsetSlider, 0, border=5)

        self.rightBox.Add(self.offsetAdjustSizer, 0, wx.CENTER)

        #Bottom portion - finish calibration
        self.twoBoxes = wx.BoxSizer(wx.HORIZONTAL)
        self.twoBoxes.Add(self.leftBox)
        self.twoBoxes.Add(self.rightBox)

        self.vertical.Add(self.twoBoxes)

        finishedCalibrationBtn = wx.Button(self.panel, label="Finish Calibration")
        finishedCalibrationBtn.Bind(wx.EVT_BUTTON, self.OnClose)
        self.vertical.Add(finishedCalibrationBtn, border=10, flag=wx.ALL|wx.CENTER)

        self.panel.SetSizerAndFit(self.vertical)
        self.Fit()
        self.Show()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self.drawPanel)
            rect = self.drawPanel.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
            dc.SetBackground(wx.Brush('WHITE'))
            bmp = wx.Bitmap('Images//robot_300.jpg')
            dc.DrawBitmap(bmp, 0, 0)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.drawPanel)
        bmp = wx.Bitmap('Images//robot_300.jpg')
        dc.DrawBitmap(bmp, 0, 0)

        #draw the servos activated
        for servo in self.servoOrder:
            self.IndicateServo(dc, servo, 'Red')
        for servo in self.offsetChoices:
            self.IndicateServo(dc, servo, 'Green')

        if self.selectBlinkOn:
            self.IndicateServo(dc, self.activeServo, 'Yellow')
        else:
            self.IndicateServo(dc, self.activeServo, 'Red')

    def IndicateServo(self, dc, servo, color):
        dc.SetPen(wx.Pen('White', 6, wx.SOLID))
        dc.SetBrush(wx.Brush('WHITE', wx.TRANSPARENT))
        dc.DrawCircle(self.servoMapLocations[servo][0], self.servoMapLocations[servo][1], 8) # body outline circle
        dc.SetPen(wx.Pen(color, 4, wx.SOLID))
        dc.DrawCircle(self.servoMapLocations[servo][0], self.servoMapLocations[servo][1], 8) # body outline circle

    def flashCurrentServo(self, evt):
        if self.selectBlinkOn:
            self.selectBlinkOn = False
        else:
            self.selectBlinkOn = True

        x = self.servoMapLocations[self.activeServo][0]
        y = self.servoMapLocations[self.activeServo][1]

        self.drawPanel.RefreshRect(wx.Rect(x-10, y-10, 20, 20))

    def startCalibratingServo(self):
        #set current servo inactive
        if self.activeServo:
            writeAndSendNote("SetServoActive", "%d,%s"%(self.activeServo, "inactive"), "robot")
            #save the current servo state
            offset = self.offsetSlider.GetValue()
            self.offsetChoices[self.activeServo] = offset

        #change servo diagram picture accordingly
        if self.servoType[self.jointCounter] == "Foot":
            self.jointGuideImage.SetBitmap(wx.BitmapFromImage(wx.Image('Images//Foot_Guide_300.jpg', wx.BITMAP_TYPE_ANY)))
        if self.servoType[self.jointCounter] == "Thigh":
            self.jointGuideImage.SetBitmap(wx.BitmapFromImage(wx.Image('Images//Thigh_Guide_300.jpg', wx.BITMAP_TYPE_ANY)))
        if self.servoType[self.jointCounter] == "Hip":
            self.jointGuideImage.SetBitmap(wx.BitmapFromImage(wx.Image('Images//Hip_Guide_300.jpg', wx.BITMAP_TYPE_ANY)))
        if self.servoType[self.jointCounter] == "Head":
            self.jointGuideImage.SetBitmap(wx.BitmapFromImage(wx.Image('Images//Head_Guide_300.jpg', wx.BITMAP_TYPE_ANY)))

        #activate and center new servo
        self.activeServo = self.servoOrder[self.jointCounter]
        self.servoTitle.SetLabel("%.2d/%.2d - %s - Servo %.2d"%(self.jointCounter+1, len(self.servoOrder), self.servoPosition[self.jointCounter], self.activeServo))
        self.panel.Layout() #re-centers the text
        writeAndSendNote("SetServoActive", "%d,%s"%(self.activeServo, "active"), "robot")
        writeAndSendNote("SetServoPos", "%d,%.1f"%(self.activeServo, 0), "robot")

        self.Refresh()

        #reload servo offset, if it existed before. If not, set slider to zero.
        if self.activeServo in self.offsetChoices:
            offset = self.offsetChoices[self.activeServo]
            self.offsetSlider.SetValue(offset)
        else:
            self.offsetSlider.SetValue(0)

    def changeOffset(self, evt):
        #change offset output based on slider
        offset = self.offsetSlider.GetValue()
        self.offsetChoices[self.activeServo] = offset
        writeAndSendNote("SetServoOffset", "%d,%.1f"%(self.activeServo, offset), "robot")

    def nextServo(self, evt):
        #find out which is next servo, set it active
        self.jointCounter += 1
        if self.jointCounter > len(self.servoOrder)-1:
            self.jointCounter = len(self.servoOrder)-1
        else:
            self.startCalibratingServo()

    def prevServo(self, evt):
        #find out which is previous servo, set it active
        self.jointCounter -= 1
        if self.jointCounter < 0:
            self.jointCounter = 0
        else:
            self.startCalibratingServo()

    def OnClose(self, evt):
        self.timer.Stop()
        self.Destroy()

class RobotSelect():
    def __init__(self, panel):
        self.panel = panel
        self.robots = None

        #stuff the list with all the directories in ROBOTS_FOLDER_PATH
        for folder in os.listdir('Robots'):
            if os.path.isdir(folder):
                self.robots.append(str(folder))

        self.robots = ["Hexy V1"]
        
        cb = wx.ComboBox(self.panel, pos=(5, 5), choices=self.robots, style=wx.CB_READONLY)
        
        if len(self.robots) >= 1:
            cb.SetValue(self.robots[0])   
            ROBOT_FOLDER_PATH = ROBOTS_FOLDER_PATH + self.robots[0] + "\\"

    def OnComboSelect(self):
        pass

class ArduinoRecordWindow(wx.Frame):

    def __init__(self,parent,id):
        wx.Frame.__init__(self, parent, id, 'Record Arduino Moves', size=(400,300))
        wx.Frame.CenterOnScreen(self)
        self.panel = wx.Panel(self)

        icon = wx.Bitmap('Images//RecBtn.png')       
        self.recordBtn = wx.BitmapButton(self.panel, bitmap=icon, size=(30, 30))
        self.recordBtn.Bind(wx.EVT_BUTTON, self.recordMoves)
        
        icon = wx.Bitmap('Images//StopBtn.png')       
        self.stopBtn = wx.BitmapButton(self.panel, bitmap=icon, size=(30, 30))
        self.stopBtn.Bind(wx.EVT_BUTTON, self.stopRecordMoves)

        self.moveNameLabel = wx.StaticText(self.panel, label="Move Name:")
        self.moveName = wx.TextCtrl(self.panel, size=(300, 20))
        self.moveName.SetValue("hexy")

        self.arduinoCode = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        text = "How to record a move for Arduino:\n" \
               "0.) (Optional) Choose a move name in the box above\n" \
               "1.) Press the red record above button above\n" \
               "2.) Run a move or multiple moves in PoMoCo\n" \
               "3.) Press the black stop button above\n" \
               "4.) Copy the generated move code to the Arduino IDE"
        self.arduinoCode.ChangeValue(text)

        #GUI Layout
        self.horizontal = wx.BoxSizer()

        self.horizontal.Add(self.recordBtn, flag=wx.CENTER)
        self.horizontal.Add(self.stopBtn, flag=wx.CENTER)
        self.horizontal.Add(self.moveNameLabel, flag=wx.CENTER)
        self.horizontal.Add(self.moveName, flag=wx.CENTER)
        
        self.vertical = wx.BoxSizer(wx.VERTICAL)
        self.vertical.Add(self.horizontal, flag=wx.EXPAND)
        self.vertical.Add(self.arduinoCode, proportion=1, flag=wx.EXPAND)
        
        self.panel.SetSizerAndFit(self.vertical)  
        self.Show()

    def recordMoves(self, evt):
        moveNameStr = self.moveName.GetValue()
        self.arduinoCode.ChangeValue("Recording PoMoCo Moves...\nStop when finished for Arduino Code")
        writeAndSendNote("StartRecording", moveNameStr, "controller")
        
    def stopRecordMoves(self, evt):
        writeAndSendNote("StopRecording", "", "controller")

    def updateCodeBox(self, code):
        self.arduinoCode.ChangeValue(code)

class MoveControls():
    def __init__(self, panel):
        self.panel = panel
        self.moveFolderPath = None
        self.moves = []
        self.moveBtns = []
        
        #self.firmwareLabel = wx.StaticText(self.panel, label="Moves", pos=(30,7))        
        icon = wx.Bitmap('Images//Refresh.png')       
        refreshBtn = wx.BitmapButton(self.panel, bitmap=icon, pos=(5,5), size=(30, 22))
        refreshBtn.Bind(wx.EVT_BUTTON, self.loadButtons)
        
        icon = wx.Bitmap('Images//Arduino.png')       
        refreshBtn = wx.BitmapButton(self.panel, bitmap=icon, pos=(35,5), size=(30, 22))
        refreshBtn.Bind(wx.EVT_BUTTON, self.ArduinoRecord)

    def updateCodeBox(self, code):
        if self.arduinoCodeWindow:
            self.arduinoCodeWindow.updateCodeBox(code)

    def ArduinoRecord(self, evt):
        self.arduinoCodeWindow = ArduinoRecordWindow(self.panel,1)

    def SetMovesFolder(self, folderPath):
        self.moveFolderPath = folderPath
        self.loadButtons()
        
    def loadButtons(self, evt=None):
        offsetY=30 
        if len(self.moveBtns) > 0:
            for button in self.moveBtns:
                button.Destroy() 
        self.moves = []   
        self.moveBtns = [] 

        if self.moveFolderPath:
            for fileName in os.listdir(self.moveFolderPath):
                if os.path.splitext(fileName)[1] == '.py':
                    fileName = os.path.splitext(fileName)[0]
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', fileName)
                    self.moves.append(s1)
            
            self.moves.sort()
         
            for move in self.moves:
                cbtn = wx.Button(self.panel, style=wx.BU_LEFT, label=str(move), pos=(5,offsetY), size=(85, 20))
                cbtn.moveName = move
                cbtn.Bind(wx.EVT_BUTTON, self.OnMoveButton)
                self.moveBtns.append(cbtn)
                offsetY += 22   

    def OnMoveButton(self, evt):
        moveName = evt.GetEventObject().moveName
        writeAndSendNote("RunMove", "%s"%(moveName), "robot")
                       
class ServoWidget(wx.Panel):
    def __init__(self, parent, width , height):
        self.parent = parent
        self.servos = []
        self.dragImage = None
        self.dragShape = None
        self.dragPos = None
        self.hiliteShape = None

        self.parent.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        self.bg_bmp = wx.EmptyBitmap(width, height)            
        
        self.parent.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.parent.Bind(wx.EVT_PAINT, self.OnPaint)
        self.parent.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.parent.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.parent.Bind(wx.EVT_MOTION, self.OnMotion)
        self.parent.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.parent.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        self.LastDrivenTimer = wx.Timer(self.parent)
        self.parent.Bind(wx.EVT_TIMER, self.LastDrivenCheck, self.LastDrivenTimer)
        self.LastDrivenTimer.Start(50)

    def LastDrivenCheck(self, evt):
        for servo in self.servos:
            servo.CheckDriven()

    def SetBackgroundImage(self, bmp):
        self.bg_bmp = bmp
        
    def AddServo(self, num, pos, deg=float(0.0), offset=float(0.0), visible=True, active=False, joint=""):
        servo = ServoControl(self, num, pos, deg, offset, visible, active, joint)
        self.servos.append(servo)
        
    def OnToggleServo(self, evt):
        obj = evt.GetEventObject()
        isPressed = obj.GetValue()
        servo = self.getServo(int(obj.label))
        servo.SetActive(isPressed)
        self.parent.Update()
        
    def getServo(self, servoNum):
        for servo in self.servos:
            if servo.num == int(servoNum):
                return servo
        return None

    def OnLeaveWindow(self, evt):
        pass

    # tile the background bitmap
    def TileBackground(self, dc):
        dc.SetBackground(wx.Brush('WHITE'))
        dc.DrawBitmap(self.bg_bmp, 0, 0)

    # Go through our list of shapes and draw them in whatever place they are.
    def DrawShapes(self, dc):
        for shape in self.servos:
            if shape.visible:
                shape.Draw(dc)

    # This is actually a sophisticated 'hit test', but in this
    # case we're also determining which shape, if any, was 'hit'.
    def FindShape(self, pt):
        for shape in self.servos:
            if shape.HitTest(pt):
                return shape
        return None

    # Clears the background, then redraws it. If the DC is passed, then
    # we only do so in the area so designated. Otherwise, it's the whole thing.
    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.parent.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        self.TileBackground(dc)

    # Fired whenever a paint event occurs
    def OnPaint(self, evt):
        dc = wx.PaintDC(self.parent)
        #self.PrepareDC(dc)
        self.DrawShapes(dc)
        
    def OnLeftDClick(self, evt):
        pt = evt.GetPosition()
        shape = self.FindShape(pt)
        if shape:
            if shape.ActiveOnButtonTest(pt):
                #print shape.num,"turned active"
                shape.SendActive(True)
                self.parent.RefreshRect(shape.GetRect(), True)
                self.parent.Update()
                
            if shape.ActiveOffButtonTest(pt):
                #print shape.num,"turned inactive"
                shape.SendActive(False)
                self.parent.RefreshRect(shape.GetRect(), True)
                self.parent.Update()
                
            if shape.OffsetPlusTest(pt):
                shape.SendOffset(shape.offset + 1)
                shape.Render()
                self.parent.RefreshRect(shape.GetRect(), True)
                self.parent.Update() 
                               
            if shape.OffsetMinusTest(pt):
                shape.SendOffset(shape.offset - 1)
                shape.Render()
                self.parent.RefreshRect(shape.GetRect(), True)
                self.parent.Update()
            
            if shape.ServoControlTest(pt):
                shape.SendDeg(0)
                shape.Refresh()
                
            if shape.offsetsShown:
                rect = wx.Rect(shape.pos[0]+12, shape.pos[1]+40, 24, 10)
                if rect.InsideXY(pt.x, pt.y):
                    shape.offset = 0
                    shape.Render()
                    self.parent.RefreshRect(shape.GetRect(), True)
                    self.parent.Update()
        
    # Left mouse button is down.
    def OnLeftDown(self, evt):
        pt = evt.GetPosition()
        # Did the mouse go down on one of our shapes?
        shape = self.FindShape(pt)

        # If a shape was 'hit', then set that as the shape we're going to
        # drag around. Get our start position. Dragging has not yet started.
        # That will happen once the mouse moves, OR the mouse is released.
        if shape:
            if(shape.ControlTest(pt)):
                if shape.ServoControlTest(pt):
                    self.dragPos = True
                    self.dragPosServo = shape
                    
                if shape.ActiveOnButtonTest(pt):
                    #print shape.num,"turned active"
                    shape.SendActive(True)
                    self.parent.RefreshRect(shape.GetRect(), True)
                    self.parent.Update()
                    
                if shape.ActiveOffButtonTest(pt):
                    #print shape.num,"turned inactive"
                    shape.SendActive(False)
                    self.parent.RefreshRect(shape.GetRect(), True)
                    self.parent.Update()
                    
                if shape.OffsetPlusTest(pt):
                    shape.SendOffset(shape.offset + 1)
                    shape.Render()
                    self.parent.RefreshRect(shape.GetRect(), True)
                    self.parent.Update()
                    
                if shape.OffsetMinusTest(pt):
                    shape.SendOffset(shape.offset - 1)
                    shape.Render()
                    self.parent.RefreshRect(shape.GetRect(), True)
                    self.parent.Update()
            else:
                self.dragShape = shape
                self.dragStartPos = pt

    # Left mouse button up.
    def OnLeftUp(self, evt):
        self.dragPos = None
        self.dragPosServo = None
        if not self.dragImage or not self.dragShape:
            self.dragImage = None
            self.dragShape = None
            return

        # Hide the image, end dragging, and nuke out the drag image.
        self.dragImage.Hide()
        self.dragImage.EndDrag()
        self.dragImage = None

        if self.hiliteShape:
            self.parent.RefreshRect(self.hiliteShape.GetRect())
            self.hiliteShape = None

        # reposition and draw the shape

        # Note by jmg 11/28/03 
        # Here's the original:
        #
        # self.dragShape.pos = self.dragShape.pos + evt.GetPosition() - self.dragStartPos
        #
        # So if there are any problems associated with this, use that as
        # a starting place in your investigation. I've tried to simulate the
        # wx.Point __add__ method here -- it won't work for tuples as we
        # have now from the various methods
        #
        # There must be a better way to do this :-)
        #
        
        self.dragShape.pos = (
            self.dragShape.pos[0] + evt.GetPosition()[0] - self.dragStartPos[0],
            self.dragShape.pos[1] + evt.GetPosition()[1] - self.dragStartPos[1]
            )
            
        self.dragShape.visible = True
        self.parent.RefreshRect(self.dragShape.GetRect())
        self.dragShape = None


    # The mouse is moving
    def OnMotion(self, evt):
        #servo control dragging trumps dragging shape dragging
        if self.dragPos:
            self.dragPosServo.SetServoControl(evt.GetPosition())
            #get position relative to "center" of servo

        else:
            # Ignore mouse movement if we're not dragging.
            if not self.dragShape or not evt.Dragging() or not evt.LeftIsDown():
                return

            # if we have a shape, but haven't started dragging yet
            if self.dragShape and not self.dragImage:

                # only start the drag after having moved a couple pixels
                tolerance = 2
                pt = evt.GetPosition()
                dx = abs(pt.x - self.dragStartPos.x)
                dy = abs(pt.y - self.dragStartPos.y)
                if dx <= tolerance and dy <= tolerance:
                    return

                # refresh the area of the window where the shape was so it
                # will get erased.
                self.dragShape.visible = False
                self.parent.RefreshRect(self.dragShape.GetRect(), True)
                self.parent.Update()

                self.dragImage = wx.DragImage(self.dragShape.bmp,
                                             wx.StockCursor(wx.CURSOR_HAND))


                hotspot = self.dragStartPos - self.dragShape.pos
                self.dragImage.BeginDrag(hotspot, self.parent, self.dragShape.fullscreen)

                self.dragImage.Move(pt)
                self.dragImage.Show()


            # if we have shape and image then move it, posibly highlighting another shape.
            elif self.dragShape and self.dragImage:
                onShape = self.FindShape(evt.GetPosition())
                unhiliteOld = False
                hiliteNew = False

                # figure out what to hilite and what to unhilite
                if self.hiliteShape:
                    if onShape is None or self.hiliteShape is not onShape:
                        unhiliteOld = True

                if onShape and onShape is not self.hiliteShape and onShape.visible:
                    hiliteNew = True

                # if needed, hide the drag image so we can update the window
                if unhiliteOld or hiliteNew:
                    self.dragImage.Hide()

                if unhiliteOld:
                    dc = wx.ClientDC(self.parent)
                    self.hiliteShape.Draw(dc)
                    self.hiliteShape = None

                if hiliteNew:
                    dc = wx.ClientDC(self.parent)
                    self.hiliteShape = onShape
                    self.hiliteShape.Draw(dc, wx.INVERT)

                # now move it and show it again if needed
                self.dragImage.Move(evt.GetPosition())
                if unhiliteOld or hiliteNew:
                    self.dragImage.Show()

            if os.name == 'posix':
                self.parent.Refresh()
                self.parent.Update()
                self.parent.RefreshRect(self.dragShape.GetRect(), True)


class ServoControl:
    def __init__(self, parent, num, pos, deg=float(0.0), offset=float(0.0), visible=True, active=False, joint=""):
        self.offsetsShown = False
        self.parent = parent
        self.width = 48
        if self.offsetsShown:
            self.height = 56
        else:
            self.height = 44
        self.dc = wx.MemoryDC()
        self.num = int(num)
        self.pos = pos
        self.deg = float(deg)
        self.offset = float(offset)
        self.active = bool(active)
        self.visible = bool(visible)
        self.joint = str(joint)
        self.freshlyDriven = False #keeps track if servo was just moved recently
        self.lastDriven = time.clock()

        self.fullscreen = False
        self.x = 0
        self.y = 0
        self.r = 20
        
        self.InitialMessages()

        self.Render()

    def InitialMessages(self):
        if self.active:
            outActive = "active"
        else:
            outActive = "inactive"
        writeAndSendNote("SetServoActive", "%d,%s"%(self.num, outActive), "robot")
        writeAndSendNote("SetServoPos", "%d,%.1f"%(self.num, self.deg), "robot")
        writeAndSendNote("SetServoOffset", "%d,%.1f"%(self.num, self.offset), "robot")
        
    def SetServoControl(self, pt):
        #center of control
        centerX = self.pos[0]+self.width/2
        centerY = self.pos[1]+self.r+3
        
        #these are in regular positive x-y Cartesian
        relativeX = pt[0]-centerX
        relativeX = pt[0]-centerX
        relativeY = centerY-pt[1]
        
        #calculate the degree of the mouse from the center (maxing at +/- 90 deg)
        deg = float(0.0)
        if relativeY <= 0:
            if relativeX >= 0:
                deg = float(90.0)
            else:
                deg = float(-90.0)
        else:
            deg = -math.degrees(math.atan(float(relativeX)/float(relativeY)))
        
        #get degree relative to center
        self.SendDeg(deg)
        self.Refresh()

    def OnDriven(self):
        #run when the servo position or offset was changed. Changes control color to let user know it was changed.
        self.freshlyDriven = True
        self.lastDriven = time.clock()

    def CheckDriven(self):
        #function activated by OnDriven after sufficient time has passed to return the control to its regular color
        if self.freshlyDriven:
            if time.clock() - self.lastDriven > 0.1: #if its been more than 0.1 seconds since the last drive event
                self.freshlyDriven = False
                self.Render()
                self.Refresh()
                return True
        return False

    def SendDeg(self, deg):
        #notify the robot module the servo position was changed
        writeAndSendNote("SetServoPos", "%d,%.1f"%(self.num, deg), "robot")
        
    def SetDeg(self, deg):
        self.deg = float(deg)
        self.OnDriven()
        self.Render()
        
    def SendOffset(self, offset):
        #notify the robot module the servo position was changed
        writeAndSendNote("SetServoOffset", "%d,%.1f"%(self.num, offset), "robot")

    def SendActive(self, state):
        if state:
            outActive = "active"
        else:
            outActive = "inactive"
        writeAndSendNote("SetServoActive", "%d,%s"%(self.num, outActive), "robot")

    def SetOffset(self, offset):
        self.offset = float(offset)
        self.OnDriven()
        self.Render()
        
    def OffsetsToggle(self):
        self.offsetsShown = not self.offsetsShown
        self.Render()        
        
    def SetActive(self, active):
        self.active = bool(active)
        self.OnDriven()
        self.Render()
        
    def HitTest(self, pt):
        rect = self.GetRect()
        if rect.InsideXY(pt.x, pt.y): self.ControlTest(pt)
        return rect.InsideXY(pt.x, pt.y)

    def ControlTest(self, pt):
        servoControl = self.ServoControlTest(pt)
        activeButton = self.ActiveOnButtonTest(pt) or self.ActiveOffButtonTest(pt)
        offsetButton = self.OffsetPlusTest(pt) or self.OffsetMinusTest(pt)
        return (servoControl or activeButton or offsetButton)

    def ServoControlTest(self, pt):
        rect = wx.Rect(self.pos[0], self.pos[1], self.width, self.r+3)
        return rect.InsideXY(pt.x, pt.y)

    def ActiveOnButtonTest(self, pt):
        rect = wx.Rect(self.pos[0]+33, self.pos[1]+23, 12, 17)
        return rect.InsideXY(pt.x, pt.y)
        
    def ActiveOffButtonTest(self, pt):
        rect = wx.Rect(self.pos[0]+4, self.pos[1]+23, 12, 17)
        return rect.InsideXY(pt.x, pt.y)
        
    def OffsetPlusTest(self, pt):
        if not self.offsetsShown:
            return False
        rect = wx.Rect(self.pos[0]+37, self.pos[1]+40, 7, 10)
        return rect.InsideXY(pt.x, pt.y)
        
    def OffsetMinusTest(self, pt):
        if not self.offsetsShown:
            return False
        rect = wx.Rect(self.pos[0]+4, self.pos[1]+40, 7, 10)
        return rect.InsideXY(pt.x, pt.y)                
                      
    def GetRect(self):
        return wx.Rect(self.pos[0], self.pos[1],
                      self.width, self.height)

    def Render(self):
        if self.offsetsShown:
            self.height = 56
        else:
            self.height = 44
        
        # create a bitmap the same size as our text
        self.bmp = wx.EmptyBitmap(self.width, self.height)

        # 'draw' the text onto the bitmap
        dc = wx.MemoryDC()
        dc.SelectObject(self.bmp)
        dc.SetBackground(wx.Brush(wx.BLUE, wx.SOLID))
        dc.Clear()

        if self.active:
            brush_color = wx.Brush('WHITE')
            pen_color = 'WHITE'
        else:
            brush_color = wx.Brush('LIGHT GREY')
            pen_color = 'LIGHT GREY'

        if self.freshlyDriven:
            brush_color = wx.Brush('YELLOW')
            pen_color = 'YELLOW'

        ### draw outline of control
        pen = wx.Pen(pen_color, 4, wx.SOLID)
        pen.SetJoin(wx.JOIN_BEVEL)
        dc.SetPen(pen)     
        dc.DrawCircle(self.x+24, self.y+24, self.r+2) # body outline circle
        dc.DrawRectangle(self.x+1, self.y+24, 46, self.height-20) # body outline rectangle

        ### draw servo control
        dc.SetBrush(brush_color)
        pen = wx.Pen('BLACK', 2, wx.SOLID)
        pen.SetJoin(wx.JOIN_BEVEL)
        dc.SetPen(wx.Pen('BLACK', 2, wx.SOLID))   
        dc.DrawCircle(self.x+24, self.y+24, self.r) # black circle  
        
        #draw line for servo angle
        # dc.DrawLine(self.x+55, self.y+70/2-8, 
                    # self.x+55+(self.r-2)*math.sin(math.radians(self.deg)), 
                    # self.y+70/2-(self.r-2)*math.cos(math.radians(self.deg))-8)
          
        #draw servo angle end cap
        dc.DrawCircle(self.x+24+(self.r-2)*math.sin(math.radians(-self.deg)),
                      self.y+70/2-(self.r-2)*math.cos(math.radians(-self.deg))-11, 4)
        
        #display position angle in degrees
        t = dc.GetTextExtent("%.1f"%self.deg)[0]
        if os.name == 'nt':
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
            dc.DrawText("%.1f"%self.deg, self.x+40-t, self.y+11)      
        elif os.name == 'posix':
            dc.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
            dc.DrawText("%.1f"%self.deg, self.x+28-int(float(t)*0.5), self.y+11)      

        ### servo number display and on/off button
        offsetY = 23
        dc.SetPen(wx.Pen('BLACK', 2, wx.SOLID))
        dc.SetBrush(brush_color)
        dc.DrawRectangle(self.x+4,self.y+offsetY,self.r*2+1,17) # box for pos/offset servos
        if os.name == 'nt':
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
            dc.DrawText("%.2d"%self.num, self.x+17, self.y+offsetY) # servo number display
        elif os.name == 'posix':
            dc.SetFont(wx.Font(13, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
            dc.DrawText("%.2d"%self.num, self.x+17, self.y+offsetY+2) # servo number display
        dc.SetBrush(wx.Brush('RED'))
        dc.DrawRectangle(self.x+4,self.y+offsetY, 12, 17) # box for turning servo off
        dc.SetBrush(wx.Brush('FOREST GREEN'))
        dc.DrawRectangle(self.x+33,self.y+offsetY, 12, 17) # box for turning servo on

        ### offset adjust buttons
        if self.offsetsShown:
            offsetY = 38
            dc.SetPen(wx.Pen('BLACK', 2, wx.SOLID))

            dc.SetBrush(brush_color)
            dc.DrawRectangle(self.x+4,self.y+offsetY+1,self.r*2+1,13) # box for pos/offset servos
            dc.SetPen(wx.Pen('BLACK', 1, wx.SOLID))
            dc.DrawLine(self.x+11, self.y+offsetY, self.x+11, self.y+offsetY+12) # vertical bar on left side
            dc.SetBrush(wx.Brush('BLACK'))
            dc.DrawPolygon(((self.x+5,self.y+offsetY+6), (self.x+11,self.y+offsetY+2), (self.x+11,self.y+offsetY+10))) # offset arrow on left side (left, top, bottom points)
            dc.DrawLine(self.x+36, self.y+offsetY, self.x+36, self.y+offsetY+12) # vertical bar on right side
            dc.DrawPolygon(((self.x+self.width-5,self.y+offsetY+6), (self.x+self.width-11,self.y+offsetY+2), (self.x+self.width-11,self.y+offsetY+10))) # offset arrow on right side (right, top, bottom points)
            t = dc.GetTextExtent("%.1f"%self.offset)[0]
            if os.name == 'nt':
                dc.SetFont(wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
                dc.DrawText("%.1f"%self.offset, self.x+38-t, self.y+offsetY) # offset display
            elif os.name == 'posix':
                dc.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.BOLD, faceName="Helvetica"))
                dc.DrawText("%.1f"%self.offset, self.x+34-t, self.y+offsetY+3) # offset display

        ### cover for servo control circle if offsets not active
        pen.SetJoin(wx.JOIN_BEVEL)
        dc.SetPen(wx.Pen(pen_color, 3, wx.SOLID))   
        if not self.offsetsShown: 
            dc.DrawRectangle(self.x+4, self.y+self.height-3, self.width-4, 2)
        
        ### set masking
        dc.SelectObject(wx.NullBitmap)
        mask = wx.Mask(self.bmp, wx.BLUE)
        self.bmp.SetMask(mask)
 
    def Refresh(self):
        self.parent.parent.RefreshRect(self.GetRect(), True)
 
    def Draw(self, dc, op = wx.COPY):
        if self.bmp.Ok():
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)

            dc.Blit(self.pos[0], self.pos[1],
                    self.width, self.height,
                    memDC, 0, 0, wx.COPY, True)

            return True
        else:
            return False
     
class ServoToggle():
    def __init__(self, panel):
        self.panel = panel
        self.toggleButtons = []
        
        # cbtn = wx.ToggleButton(panel, id=00, label="00", pos=DefaultPosition,
             # size=DefaultSize, style=0, val=DefaultValidator, name=CheckBoxNameStr)

        #bulk servo actions
        offsetY = 0
        spacingY = 20
        self.disableAllBtn = wx.Button(self.panel, label='Disable All')
        self.enableAllBtn = wx.Button(self.panel, label='Enable All')
        self.centerAllBtn = wx.Button(self.panel, label='Center All')
        self.offsetsEditBtn = wx.Button(self.panel, label='Edit Offsets')


        #Servo Toggle Buttons
        for i in range(32):
            if os.name == 'nt':
                servoButton = wx.ToggleButton(self.panel, i, str("%.2d"%(i)), size=(18,20))
                self.toggleButtons.append(servoButton)
            elif os.name == 'posix':  
                servoButton = wx.ToggleButton(self.panel, i, str("%.2d"%(i)), size=(30,20))
                self.toggleButtons.append(servoButton)

        topBox = wx.BoxSizer(wx.VERTICAL)        
        
        if os.name == 'nt':
            toggleBtns = wx.BoxSizer(wx.HORIZONTAL)
            for i in range(32):
                toggleBtns.Add(self.toggleButtons[i], flag=wx.CENTER)
                
            topBox.Add(toggleBtns)    
        elif os.name == 'posix':  
             toggleBtns = wx.BoxSizer(wx.HORIZONTAL)
             for i in range(16):
                toggleBtns.Add(self.toggleButtons[i])
                
             toggleBtns2 = wx.BoxSizer(wx.HORIZONTAL)
             for i in range(16):
                toggleBtns2.Add(self.toggleButtons[i+16])
                
             topBox.Add(toggleBtns, flag=wx.CENTER)  
             topBox.Add(toggleBtns2, flag=wx.CENTER)  

        commandBtns = wx.BoxSizer(wx.HORIZONTAL)
        commandBtns.Add(self.disableAllBtn)
        commandBtns.Add(self.enableAllBtn)
        commandBtns.Add(self.centerAllBtn)
        commandBtns.Add(self.offsetsEditBtn)
        topBox.Add(commandBtns, flag=wx.CENTER)
 
        self.panel.SetSizerAndFit(topBox)
 
    def GetButton(self, num):
        for button in self.toggleButtons:
            if int(button.GetLabel()) == int(num):
                return button
        return None
     
class ControllerPanel():
    def __init__(self, panel):
        self.panel = panel
        self.initUI()
        #self.ScanSerialPorts()
        self.portList = []
        
    def initUI(self):
        # controller type drop-down
        self.controllerSelect = wx.ComboBox(self.panel, choices=["Servotor32"], style=wx.CB_READONLY)
        self.controllerSelect.SetValue("Servotor32")

        # serial port selection drop-down 
        self.serialPortSelect = wx.ComboBox(self.panel, choices=[], style=wx.CB_READONLY)

        # serial auto-connect button        
        self.autoConnectBtn = wx.Button(self.panel, label='Auto-Connect')
        self.autoConnectBtn.Bind(wx.EVT_BUTTON, self.OnAutoConnect)

        # controller firmware version
        self.firmwareLabel = wx.StaticText(self.panel, label=" Firmware: %s"%("N/A                         "))
        
        # controller status icon image
        self.greenButton = wx.Bitmap('Images//greenBut2.png')
        self.redButton = wx.Bitmap('Images//redBut2.png')
        self.statusImage = wx.StaticBitmap(self.panel, bitmap=wx.EmptyBitmap(25, 25))
        self.SetConnectionStatus(False)
        
        # controller status icon image
        self.connectBtn = wx.Button(self.panel, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.OnConnect)

        #GUI Layout
        serialSizer = wx.BoxSizer(wx.HORIZONTAL|wx.ALIGN_LEFT)
        serialSizer.Add(self.statusImage, border=5, flag=wx.CENTER)
        serialSizer.Add(wx.Size(5,5))
        serialSizer.Add(self.controllerSelect, border=5, flag=wx.CENTER)
        serialSizer.Add(wx.Size(5,5))
        serialSizer.Add(self.serialPortSelect, border=5, flag=wx.CENTER)
        serialSizer.Add(wx.Size(5,5))
        serialSizer.Add(self.autoConnectBtn, border=5, flag=wx.CENTER)
        serialSizer.Add(wx.Size(5,5))
        serialSizer.Add(self.connectBtn, border=5, flag=wx.CENTER)
        serialSizer.Add(wx.Size(5,5))
        serialSizer.Add(self.firmwareLabel, border=5, flag=wx.CENTER)
        

        self.panel.SetSizerAndFit(serialSizer)

    def OnConnect(self, evt):
        writeAndSendNote("RequestConnectPort",self.serialPortSelect.GetValue(),"controller")

    def SetConnectionStatus(self, status):
        if status:
            self.statusImage.SetBitmap(self.greenButton)
        else:
            self.statusImage.SetBitmap(self.redButton)

#     def OnRefresh(self, evt):
#         writeAndSendNote("RequestPortList","","controller")
        
    def ScanSerialPorts(self):
        writeAndSendNote("RequestPortList","","controller")

    def SetPortList(self, portList):
        self.serialPortSelect.Clear()
        self.portList = portList
        for port in portList:
            self.serialPortSelect.Append(port)
        if len(portList) > 0:
            self.serialPortSelect.SetValue(portList[0])
            
    def SetFirmwareV(self, firmwareV):
        self.firmwareLabel.SetLabel("Firmware: %s"%(firmwareV))

    def OnAutoConnect(self, evt):
        writeAndSendNote("RequestAutoConnect","","controller")

def start(robot="hexy"):
    app = wx.App()
    frame = MainGui()
    app.MainLoop()
 
if __name__ == '__main__':
    start()
