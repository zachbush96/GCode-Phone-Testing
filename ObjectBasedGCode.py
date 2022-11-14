'''
'     ______ _   __ ______   ____   __                           ______             __   _              
'    / ____// | / // ____/  / __ \ / /_   ____   ____   ___     /_  __/___   _____ / /_ (_)____   ____ _
'   / /    /  |/ // /      / /_/ // __ \ / __ \ / __ \ / _ \     / /  / _ \ / ___// __// // __ \ / __ `/
'  / /___ / /|  // /___   / ____// / / // /_/ // / / //  __/    / /  /  __/(__  )/ /_ / // / / // /_/ / 
'  \____//_/ |_/ \____/  /_/    /_/ /_/ \____//_/ /_/ \___/    /_/   \___//____/ \__//_//_/ /_/ \__, /  
'                                                                                              /____/   
'''

from ast import arg
from ensurepip import version
import sys
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import time
import math
import os
import random
from Camera import *



#FREQUENTLY USED VARIABLES
TROUBLESHOOTING = False
BACKOFF = 5 #Hit the limit switch and and then move back a few mm with the force of BACKOFF_FORCE
BACKOFF_FORCE = 1000
SCREEN_CORDINATES_PADDING = BACKOFF + 4
FSPEED = 10_000
COMPORT = ""



#Helper Functions
def cls():
  os.system('cls' if os.name=='nt' else 'clear')

def command(ser, strCommand): #Sends a command to the controller
  
  time.sleep(.25)
  
  if ser.is_open is False: #If the serial port is not open, reopen it
    print("Reconnecting to Device")
    ser.close()
    ser1 = serial.Serial(cnc.COMport, 115200, timeout=1) #Reconecting to the device
    setupConnection(ser1) #Clear the buffer
    print("Sleeping for 3 seconds...")
    time.sleep(3)
    command(ser1, strCommand) #If the serial port was closed, resend the command now that the port is open
  
  ser.write(str.encode(strCommand+"\r\n"))
  response = ser.readline().decode('utf-8') #<--- This is supposed to be the response from the controller, but the response doesnt mean the command was executed until the end
  if(TROUBLESHOOTING):
    print("Sent:" + str(strCommand) + " received:" + response)

def setupConnection(ser): #Sends a few blank commands to the controller to clear the buffer\
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
  command(ser, "G90") #Set to absolute mode

def set00(ser, cnc): #Goes to the limit switch of each axis, scoots off the limit switch by *BACKOFF* millimeters, and sets the current position to 0,0,0
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")

    #Setup X Axis
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 X-300 F{FSPEED}') #Move to the left
    time.sleep(15) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("X Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 X100 F{FSPEED}') #Move to the right
    time.sleep(1)
    ser.close()
    print("X Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 X{BACKOFF} F{BACKOFF_FORCE}') #Move to the right
    time.sleep(2.5)
    ser.close()
    print("""
    '------------------------------------------------------------------ 
    '   __   __                  _         _____        _   
    '   \ \ / /     /\          (_)       / ____|      | |  
    '    \ V /     /  \   __  __ _  ___  | (___    ___ | |_ 
    '     > <     / /\ \  \ \/ /| |/ __|  \___ \  / _ \| __|
    '    / . \   / ____ \  >  < | |\__ \  ____) ||  __/| |_ 
    '   /_/ \_\ /_/    \_\/_/\_\|_||___/ |_____/  \___| \__|
    '                                                       
    '------------------------------------------------------------------                                                        
    """)

    #Setup Y Axis
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 Y300 F{FSPEED}') #Move Up 
    time.sleep(15) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Y Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Y-100 F{FSPEED}') #Move Down until the limit switch releases
    time.sleep(1)
    ser.close() #Close the connection after releasing the limit switch
    print("Y Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Clear any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Y-{BACKOFF} FF{BACKOFF_FORCE}') #Move Down
    time.sleep(2.5)
    ser.close()
    print("""
    '------------------------------------------------------------------ 
    '   __     __                      _            _____          _   
    '   \ \   / /       /\            (_)          / ____|        | |  
    '    \ \_/ /       /  \    __  __  _   ___    | (___     ___  | |_ 
    '     \   /       / /\ \   \ \/ / | | / __|    \___ \   / _ \ | __|
    '      | |       / ____ \   >  <  | | \__ \    ____) | |  __/ | |_ 
    '      |_|      /_/    \_\ /_/\_\ |_| |___/   |_____/   \___|  \__|
    '                                                                  
    '------------------------------------------------------------------                                                                  
    """)
    
    #Setup Z Axis
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 Z300 F{FSPEED}') #Move Z axis Up 
    time.sleep(5) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Z Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Z-100 F{FSPEED}') #Move Down until the limit switch releases
    time.sleep(3)
    ser.close() #Close the connection after releasing the limit switch
    print("Z Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Clear any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Z-{BACKOFF} F{BACKOFF_FORCE}') #Move Down on the Z axis
    time.sleep(2.5)
  
    print("""
    '-----------------------------------------------------------------
    '    ______                      _            _____          _   
    '   |___  /       /\            (_)          / ____|        | |  
    '      / /       /  \    __  __  _   ___    | (___     ___  | |_ 
    '     / /       / /\ \   \ \/ / | | / __|    \___ \   / _ \ | __|
    '    / /__     / ____ \   >  <  | | \__ \    ____) | |  __/ | |_ 
    '   /_____|   /_/    \_\ /_/\_\ |_| |___/   |_____/   \___|  \__|
    '                                                                
    '------------------------------------------------------------------                                                                
    """)
    
    #Set position to 0,0, 0
    command(ser, "G92 X0 Y0 Z0")
    command(ser, "G90") #Set to absolute mode
    command(ser, "$X")
    command(ser, "$H")

def getUserInput(ser, userInput): 
  print(ser)
  if ser.is_open is False:
    print("Reconnecting to Device")
    ser = serial.Serial(cnc.COMport, 115200, timeout=1)
    setupConnection(ser)
    command(ser, userInput)
  else:
    print("Sending Command")
    command(ser, userInput)

#Emulate a touch on the screen
def click(ser): #Currently - Lower and then raise the Z-Axis - Future - lower and raise the Z-Axis and also turn on and off the spindle
  command(ser, f'G1 Z-35 F{FSPEED}')
  command(ser, f'G1 Z-30 F{FSPEED}')





#MAIN TEST FUNCTIONS
def screenTest(ser, DeviceProfile):
  print("Starting Screen Test")
  #Test order should be , Touch, Top Left corner, Top Right corner, bottom right coner, 
  #bottom left corner, top left, bottom right, bottom left, almost top right, 
  #CAMERA_IMAGE, almost top right, top right
  command(ser, DeviceProfile["testLocations"]["Touch"]) #GOTO touch button
  click(ser) #Touch the screen and raise back up
  command(ser, DeviceProfile["Display"]["Top Left Corner"])
  command(ser, f'G1 Z-35  F{FSPEED}')
  command(ser, DeviceProfile["Display"]["Top Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Left Corner"])
  command(ser, DeviceProfile["Display"]["Top Left Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Left Corner"])
  command(ser, DeviceProfile["Display"]["Top Right Corner"]) #Eventually replace "Top Right Corner" with "Almost Top Right Corner"
  command(ser, DeviceProfile["testLocations"]["Camera Center"]) #Take a picture of an ~almost~ complete test
                                                    #WORKING ON - command(ser, DeviceProfile["TestLocations"]["Top Right Corner"])
  time.sleep(63) #Wait 1 mminute
  capturePicture("afterScreenTest" + str(random.randint(0, 100000)), cnc)

def Red(ser, DeviceProfile):
  print("Starting Red LED Test - Internal")
  command(ser, DeviceProfile['testLocations']['Red'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(15)  
  print("Just sent Camera Center")
  capturePicture("GoodRed" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  #command(ser, "G1 Z-24")
  click(ser)

def Green(ser, DeviceProfile):
  print("Starting Green LED Test")
  command(ser, DeviceProfile['testLocations']['Green'])
  command(ser, f'G1 Z-35  F{FSPEED}')
  command(ser, "G1 Z-30")
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodGreeen" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  command(ser, "G1 Z-35")
  command(ser, "G1 Z-21")

def Blue(ser, DeviceProfile):
  print("Starting Blue LED Test")
  command(ser, DeviceProfile['testLocations']['Blue'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodBlue" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  click(ser)

def PowerButton(ser, DeviceProfile):
  print("Clicking Power Button")
  command(ser, DeviceProfile['testLocations']['Power Button'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeDown(ser, DeviceProfile):
  print("Clicking Volume Down Button")
  command(ser, DeviceProfile['testLocations']['Volume Down'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeUp(ser, DeviceProfile):
  print("Clicking Volume Up Button")
  command(ser, DeviceProfile['testLocations']['Volume Up'])
  command(ser, "G1 Z-25")
  #Lower the finger
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  #Raise the finger
  command(ser, "G1 Z-15")

def Receiver(ser, DeviceProfile):
  print("Starting Receiver Test")
  command(ser, DeviceProfile['testLocations']['Receiver'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(8)
  capturePicture("WhiteScreen" + str(random.randint(0, 100000)), cnc)
  command(ser, "G1 Y-58") #Move to a touchable location
  click(ser)

def Vibration(ser, DeviceProfile):
  print("Starting Vibration Test")
  command(ser, DeviceProfile['testLocations']['Vibration'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger

def MegaCam(ser, DeviceProfile): #Image is very dark compared to the other images
  print("Starting MegaCam Test")
  command(ser, DeviceProfile['testLocations']['Mega Cam'])
  click(ser)
  command(ser, "G1 X91 Y-90")   #Move to camera capture botton
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(30)
  capturePicture("MegaCam" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)
  click(ser)

def Sensor(ser, DeviceProfile): #Image is very bright compared to the other images
  print("Starting Sensor Test")
  command(ser, DeviceProfile['testLocations']['Sensor'])
  click(ser)
  #Take a picture of the screen
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  #input("Press Enter to take a picture")
  time.sleep(30)
  capturePicture("Sensor" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)

def Speaker(ser, DeviceProfile): 
  print("Starting Speaker Test")
  command(ser, DeviceProfile['testLocations']['Speaker'])
  click(ser)
  click(ser)
  click(ser)
  click(ser)

def SubKey(ser, DeviceProfile): 

  print("Starting SubKey Test")
  command(ser, DeviceProfile['testLocations']['Sub Key'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Volume Up'])
  print("Just hit Volume Up")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(10)
  capturePicture("SubKey_VolumeUp" + str(random.randint(0, 100000)), cnc)

  command(ser, DeviceProfile['testLocations']['Volume Down'])
  print("Just hit Volume Down")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(10)
  capturePicture("SubKey_VolumeDown" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['testLocations']['Power Button'])
  print("Just hit Power Button")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(10)
  capturePicture("SubKey_PowerButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Back Button'])
  print("Just hit Back Button")
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_BackButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Home Button'])
  print("Just hit Home Button")
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_HomeButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Menu Button'])
  print("Just hit Menu Button")
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_MenuButton" + str(random.randint(0, 100000)), cnc)

  #Leave the SubKey test (double tap the back button)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)
  click(ser)

def FrontCamera(ser, DeviceProfile): 
  print("Starting Front Camera Test")
  command(ser, DeviceProfile['testLocations']['Front Cam'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("FrontCamera" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)
  click(ser)

def GripSensor(ser, DeviceProfile): #INCOMPLETE
  print("Starting Grip Sensor Test")
  pass

def Black(ser, DeviceProfile): 
  print("Starting Black LED Test")
  command(ser, DeviceProfile['testLocations']['Black'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("Black" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['testLocations']['Power Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button

def HallIC(ser, DeviceProfile): #INCOMPLETE
  pass

def sPen(ser, DeviceProfile): #INCOMPLETE
  pass

def MST(ser, DeviceProfile): #INCOMPLETE
  command(ser, DeviceProfile['testLocations']['MST'])
  click(ser)
  OneTimeTrackOne = "G1 INCOMPLETE"
  OneTimeTrackTwo = "G1 INCOMPLETE"
  ContinousTrackOne = "G1 INCOMPLETE"
  ContinousTrackTwo = "G1 INCOMPLETE"
  ContinousTrackOneandTwo = "G1 INCOMPLETE"
  ContinousOff = "G1 INCOMPLETE"

def MLC(ser, DeviceProfile): #INCOMPLETE
  pass

def LoopBack(ser, DeviceProfile): #INCOMPLETE
  command(ser, DeviceProfile['testLocations']['Loop Back'])
  click(ser)
  RCV_1stMic = "G1 INCOMPLETE"
  SPK_2ndMic = "G1 INCOMPLETE"
  SPK_3rdMic = "G1 INCOMPLETE"
  EP = "G1 INCOMPLETE"
  ExitButton = "G1 INCOMPLETE"

def Version(ser, DeviceProfile): 
  print("Starting Version Test")
  command(ser, DeviceProfile['testLocations']['Version'])
  click(ser)
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("Version" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  click(ser)
  click(ser)


#Once a test is complete, add it to this array to include it in the test suite
ViableTests = [
  #Red,
  #Green,
  #Blue,
  Receiver,
  Vibration,
  MegaCam,
  Sensor,
  screenTest,
  Speaker,
  SubKey,
  FrontCamera,
  Black,
  Version
]



#Device Profile
GalaxyNote20Ultra = {
    "X Length": 164.8,
    "Y Length": 77.2,
    "Z Length": 8.1,
    "Display": {
        "Diagnol Size": 175,
        "Aspect Ratio": round(19.3/9, 2),
        "Width": 0, #158.6
        "Height": 0, #73.95
        "Top Left Corner": f'G1 X224.4 Y-53  F{FSPEED}',
        "Top Right Corner": f'G1 X224.4 Y-121  F{FSPEED}',
        "Bottom Right Corner": f'G1 X78.5 Y-121  F{FSPEED}',
        "Bottom Left Corner": f'G1 X78.5 Y-53  F{FSPEED}',
        "Almost Top Right Corner": f'', #Used for the screen test
        "Back Button":f'G1 X80.5 Y-105 F{FSPEED}',
        "Home Button":f'G1 X80.5 Y-88 F{FSPEED}',
        "Menu Button":f'"G1 X80.5 Y-65 F{FSPEED}',
    },
    "testLocations": {
        "Red": f'G1 X216 Y-65 F{FSPEED}', #Test Created
        "Green": f'G1 X216 Y-90 F{FSPEED}', #Test Created
        "Blue": f'G1 X216 Y-114 F{FSPEED}', #Test Created
        "Receiver":f'G1 X203 Y-65 F{FSPEED}', #CAN ALSO TEST WHITE SCREEN
        "Vibration":f'G1 X203 Y-90 F{FSPEED}',
        "Mega Cam":f'G1 X203 Y-114 F{FSPEED}',
        "Sensor":f'G1 X180 Y-65 F{FSPEED}',
        "Touch": f'G1 X180 Y-90 F{FSPEED}', #Test Created
        "Speaker":f'G1 X180 Y-114 F{FSPEED}',
        "Sub Key":f'G1 X160 Y-65 F{FSPEED}',
        "Front Cam":f'G1 X160 Y-90 F{FSPEED}',
        "Black":f'G1 X160 Y-114 F{FSPEED}',
        "Hall IC":f'G1 X140 Y-65 F{FSPEED}',
        "S-Pen":f'G1 X140 Y-90 F{FSPEED}',
        "MST Test":f'G1 X140 Y-114 F{FSPEED}',
        "MLC":f'G1 X120 Y-65 F{FSPEED}',
        "Loopback":f'G1 X120 Y-90 F{FSPEED}',
        "Version": f'G1 X117 Y-110 F{FSPEED}',
        "Grip Sensor":f'G1 X100 Y-65 F{FSPEED}',
        "Power Button": f'G1 X169 Y-131 F{FSPEED}', #Test Created
        "Volume Down": f'G1 X184 Y-131 F{FSPEED}', #Test Created
        "Volume Up": f'G1 X198 Y-131 F{FSPEED}', #Test Created
        "Camera Center": f'G1 X153 Y-38 Z5 F{FSPEED}'
    }  
}



#A class for a CNC machine that has the name of the device(ex. Berta), the COM port (ex. COM26), the Camera (ex. 0), an image path(ex. "/TestingImages/")
class CNCMachine:
    name = ""
    COMport = ""
    camera = 0
    imagePath = ""
    def __init__(self, name, COMport, camera, imagePath):
        self.name = name
        self.COMport = COMport
        self.camera = camera
        self.imagePath = imagePath
    def viewSelf(self):
        InfoString = "Name: " + self.name + "\nCOM Port: " + self.COMport + "\nCamera: " + str(self.camera) + "\nImage Path: " + self.imagePath + "\n"
        return InfoString
    def getComPort(self):
        return self.COMport
    def getCamera(self):
        return self.camera
    def getImagePath(self):
        return self.imagePath


#A function to setup a CNCMahcine object
#If a passed variable is blank, prompt for the information, else use the passed variable to create the CNCMachine object
#Checked arguments are: Name, COMPORT, CameraID, Path
def setupCNC(**options):
    n = ""
    cport = ""
    cam = 0
    ipath = ""
    
    if options.get("COMPORT") != None: #If the COMPORT option is not blank, set the CNCMachine's COMPORT to it, otherwise prompt for it
        cport = options.get("COMPORT")
    else:
        ports = serial.tools.list_ports.comports() #Initial COMPORT setup
        for port, desc, hwid in sorted(ports):
          print("{}: {} [{}]".format(port, desc, hwid))
        cport = input("Enter the COMPORT of the CNC Machine: ")
        
    if options.get("CameraID") != None: #If a CameraID is not None, set the CNCMachine's CameraID to it, otherwise prompt for it
        cam = options["CameraID"]
    else:
        cam = int(input("\nSelect Camera ID(example: 0): "))

    if options.get("Path") != None: #If a Path is not None, set the CNCMachine's Path to it, otherwise prompt for it
        ipath = options["Path"]
    else:
        ipath = "/IMAGES/" + input("Folder name to save images:(example: TestingImages or CNC1) ")
    
    if options.get("Name") != None: #If a name is not None, set the CNCMachine's name to it, otherwise generate a random name
        n = options["Name"]
    else:
        n = "CNC_"+str(random.randint(0, 100000))
    
    C = CNCMachine(n, cport, cam, ipath) #Create the CNCMachine object
    print("CNC Object Created")
    if TROUBLESHOOTING:
        print(C.viewSelf())
    return C
    
#cls() #Clear the Screen

#Handle passing arguments from the command line
CountofArguments = len(sys.argv)
Auto = False
Zero = False
Name = None
Port = None
Image = None
Camera = None
if CountofArguments > 1:
  for i in range(1, CountofArguments):
    if sys.argv[i] == "--Name":
          Name = sys.argv[i+1]
    elif sys.argv[i] == "--Port":
          Port = sys.argv[i+1]
    elif sys.argv[i] == "--Image":
          Image = sys.argv[i+1]
    elif sys.argv[i] == "--Camera":
          Camera = int(sys.argv[i+1])
    elif sys.argv[i] == "-A":
          Auto = True
    elif sys.argv[i] == "-Z":
          Zero = True
cnc = setupCNC(Name=Name, COMPORT=Port, CameraID=Camera, Path=Image)
ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
setupConnection(ser)
command(ser, "G90")

if Auto and Zero:
    print("Closing Previous connection -- az --")
    ser.close() #Close the serial port that was opened on line 619
    ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
    setupConnection(ser)
    command(ser, "G90")
    set00(ser, cnc)
    print("Starting all tests ---az---")
    for x in ViableTests:
      x(ser, GalaxyNote20Ultra)
    print("All Tests Completed - Going to Home")
    command(ser, "G1 X0 Y0")

elif Auto and not Zero:
  print("Closing Previous connection -- auto --")
  ser.close()
  ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
  setupConnection(ser)
  command(ser, "G90")
  print("Starting all tests ---auto---")
  for x in ViableTests:
    x(ser, GalaxyNote20Ultra)
  print("All Tests Complete - Going to Home")
  command(ser, "G1 X0 Y0")

elif Zero and not Auto:
  set00(ser, cnc)









'''
if len(sys.argv) < 2:  #Run setup if no arguments are passed
    cnc = setupCNC()
    ser = serial.Serial(cnc.COMport, 115200, timeout=1)
    setupConnection(ser)
    command(ser, "G90")
else:
  if sys.argv[1] == "help":
    print("Options: COMPORT, CameraID, PATH, Name \{auto\}")
    sys.exit()
  if len(sys.argv) == 2:
      if help in sys.argv:
          print("Options: COMPORT, CameraID, PATH, Name \{auto\}")
      else:
          cnc = setupCNC(COMPORT=sys.argv[1])
          ser = serial.Serial(cnc.COMport, 115200, timeout=1)
          setupConnection(ser)
          command(ser, "G90") #Set the position to absolute mode
  elif len(sys.argv) == 3:
      cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2])
      ser = serial.Serial(cnc.COMport, 115200, timeout=1)
      setupConnection(ser)
      command(ser, "G90") #Set the position to absolute mode
  elif len(sys.argv) == 4:
      cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3])
      ser = serial.Serial(cnc.COMport, 115200, timeout=1)
      setupConnection(ser)
      command(ser, "G90") #Set the position to absolute mode
  elif len(sys.argv) == 5:
      cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3], Name=sys.argv[4])
      ser = serial.Serial(cnc.COMport, 115200, timeout=1)
      setupConnection(ser)
      command(ser, "G90") #Set the position to absolute mode
  elif len(sys.argv) == 6:
      if "auto" in sys.argv:
          cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3], Name=sys.argv[4])
          ser = serial.Serial(cnc.COMport, 115200, timeout=1)
          setupConnection(ser)
          command(ser, "G90") #Set the position to absolute mode
          #Run all the tests
          for x in ViableTests:
            x(ser, GalaxyNote20Ultra)
          print("Returning to 000, auto")
          command(ser, "G1 X0 Y0 Z0 F1000") #Return to 0,0,0 to swap out the phone
          print("All Tests Complete")
      
      elif "zero" in sys.argv:
          cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3], Name=sys.argv[4])
          ser = serial.Serial(cnc.COMport, 115200, timeout=1)
          setupConnection(ser)
          command(ser, "G90")
          set00(ser, cnc)
      elif "autozero" in sys.argv:
          cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3], Name=sys.argv[4])
          ser = serial.Serial(cnc.COMport, 115200, timeout=1)
          setupConnection(ser)
          command(ser, "G90")
          set00(ser, cnc)
          for x in ViableTests:
            x(ser, GalaxyNote20Ultra)
          print("Going back to 000, autozero")
          command(ser, "G1 X0 Y0 Z0 F1000") #Return to 0,0,0 to swap out the phone
          print("All Tests Complete")
      else:
          print("Invalid Arguments")

'''
