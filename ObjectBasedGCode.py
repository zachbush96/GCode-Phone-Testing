#Pip3 install serial
from ast import arg
import sys
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import time
import math
import os
import random
#Local Import
from Camera import *


'''

'  ████████╗ ██████╗ ██████╗  ██████╗ 
'  ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗
'     ██║   ██║   ██║██║  ██║██║   ██║
'     ██║   ██║   ██║██║  ██║██║   ██║
'     ██║   ╚██████╔╝██████╔╝╚██████╔╝
'     ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ 
'                                     
- Find an API that can get phone dimensions and screen dimensions [⛔] ---HOLD---
- Calculate the screen coordinates based on the phone dimensions and return GCode [✅]
- Top 5 phones in facility and create profiles for each [⛔] ---HOLD---
- Swap from Spindle control to finger control (When to touch, drap, and lift) []
- Function that accepts length in mm and returns Gcode to move that length []
- How many mm are between X10 and X20? []
- How many mm are between Y10 and Y20? []
- Read in a GCode file (*.nc) and send it over serial [✅] 
- Instead of calculting the test positions and screen positions, use predetermined static values (known good) [✅]
- Make the Test functions in the Menu.py dynamic to show all the possible tests the phone can do []
- Make the test to test camera function [✅]
- After the color tests, the finger should move to a point on the screen (currently touching the board) [✅]
- Touch test points (corners) need to be more accurate [✅]
- Touch test should leave one square blank, take a picture, then complete the test []
- Pass an argument to the Meny.py to select a COM port, if none is passed - prompt the user to select[✅]
- Take pictures of the phone screen after each color test automatically [✅]
- How to link a COMPORT and camera to eachother []
- Sub Key test needs to take a picture after hitting each key to make sure the key is pressed []
- Address cameras based on a selection instead of a hard coded value []
- Error handling for camera failure (*USUALLY CAUSED BY CAMERA BEING OPEN IN ANOTHER PROGRAM*) []
- RUNNING OPTIONS python ObjectBasedGCode.py {COMPORT} {CAMERA NUMBER}




Helpful Websites:
https://marlinfw.org/docs/gcode/M083.html #ALL GCODE COMMANDS
https://www.sainsmart.com/blogs/news/grbl-v1-1-quick-reference #GCODE ERROR CODES
https://smoothieware.org/on_boot.gcode
https://smoothieware.org/supported-g-codes
'''


#Helper Functions
def cls():
  os.system('cls' if os.name=='nt' else 'clear')
def command(ser, strCommand):
  time.sleep(.25)
  ser.write(str.encode(strCommand+"\r\n"))
  response = ser.readline().decode('utf-8') #<--- This is supposed to be the response from the controller, but the response doesnt mean the command was executed until the end
  if(TROUBLESHOOTING):
    print("Sent:" + str(strCommand) + " received:" + response)
#Sends a few blank commands to the controller to clear the buffer
def setupConnection(ser):
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
  command(ser, "G90") #Set to absolute mode
#Goes to the limit switch of each axis, scoots off the limit switch by *BACKOFF* millimeters, and sets the current position to 0,0,0
def set00(ser, cnc):
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
  #At the end of this block - the X cordinate is alligned with the hole
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




#MAIN TEST FUNCTIONS
def screenTest(ser, DeviceProfile):
  if ser.is_open is False:
    print("Reconnecting to Device")
    ser = serial.Serial(cnc.COMport, 115200, timeout=1)
    setupConnection(ser)
  command(ser, DeviceProfile["testLocations"]["Touch"]) #GOTO touch button
  #Touch the screen and raise back up
  command(ser, "G1 Z-35 F1000")
  command(ser, "G1 Z-2")
  command(ser, DeviceProfile["Display"]["Top Left Corner"])
  command(ser, "G1 Z-35 F1000")
  command(ser, DeviceProfile["Display"]["Top Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Left Corner"])
  command(ser, DeviceProfile["Display"]["Top Left Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Right Corner"])
  command(ser, DeviceProfile["Display"]["Bottom Left Corner"])
  command(ser, DeviceProfile["Display"]["Top Right Corner"])
  command(ser, DeviceProfile["testLocations"]["Camera Center"])
  #input("Press Enter to take a picture")
  time.sleep(63) #Wait 1 mminute
  capturePicture("afterScreenTest" + str(random.randint(0, 100000)), cnc)

def Red(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Red'])
  #command(ser, "G1 Z-24")
  command(ser, "G1 Z-35")
  command(ser, "G1 Z-20")
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  capturePicture("GoodRed" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-58 F{FSPEED}') #Move to a touchable location
  #command(ser, "G1 Z-24")
  command(ser, "G1 Z-35")
  command(ser, "G1 Z-20") 

def Green(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Green'])
  command(ser, "G1 Z-35 F1000")
  command(ser, "G1 Z-2")
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodGreeen" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-58 F{FSPEED}') #Move to a touchable location
  command(ser, "G1 Z-35")
  command(ser, "G1 Z-21")

def Blue(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Blue'])
  command(ser, "G1 Z-35 F1000")
  command(ser, "G1 Z-2")
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodBlue" + str(random.randint(0, 100000)), cnc)
  command(ser, f'G1 Y-58 F{FSPEED}') #Move to a touchable location
  command(ser, "G1 Z-35") #touch the screen
  command(ser, "G1 Z-21") #raise back up

def PowerButton(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Power Button'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeDown(ser, DeviceProfile):
  #Code to start Volume Button Test
  command(ser, DeviceProfile['testLocations']['Volume Down'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeUp(ser, DeviceProfile):
  #Code to start Volume Button Test
  command(ser, DeviceProfile['testLocations']['Volume Up'])
  command(ser, "G1 Z-25")
  #Lower the finger
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  #Raise the finger
  command(ser, "G1 Z-15")

def Receiver(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Receiver'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  time.sleep(25)
  capturePicture("WhiteScreen" + str(random.randint(0, 100000)), cnc)
  command(ser, "G1 Y-58") #Move to a touchable location
  command(ser, "G1 Z-24") #Touch the screen
  command(ser, "G1 Z-21") #Raise back up

def Vibration(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Vibration'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger

def MegaCam(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Mega Cam'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 X91 Y-90")   #Move to camera capture botton
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  #take a picture of the screen
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  #input("Press Enter to take a picture")
  time.sleep(30)
  capturePicture("MegaCam" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger

def Sensor(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Sensor'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  #Take a picture of the screen
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  #input("Press Enter to take a picture")
  time.sleep(30)
  capturePicture("Sensor" + str(random.randint(0, 100000)), cnc)
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger

def Speaker(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Speaker'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger

def SubKey(ser, DeviceProfile):
  command(ser, DeviceProfile['testLocations']['Sub Key'])
  command(ser, DeviceProfile['testLocations']['Volume Up'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_VolumeUp" + str(random.randint(0, 100000)), cnc)

  command(ser, DeviceProfile['testLocations']['Volume Down'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_VolumeDown" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['testLocations']['Power Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_PowerButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_BackButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Home Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_HomeButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Menu Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_MenuButton" + str(random.randint(0, 100000)), cnc)
  
  command(ser, DeviceProfile['Display']['Back Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Z-15") #Raise the finger
  command(ser, DeviceProfile['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("SubKey_BackButton" + str(random.randint(0, 100000)), cnc)


#FREQUENTLY USED VARIABLES
TROUBLESHOOTING = True
BACKOFF = 5 #Hit the limit switch and and then move back a few mm with the force of BACKOFF_FORCE
BACKOFF_FORCE = 1000
SCREEN_CORDINATES_PADDING = BACKOFF + 4
FSPEED = 10000
COMPORT = ""


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
        "Top Left Corner": "G1 X224.4 Y-53 F3000",
        "Top Right Corner": "G1 X224.4 Y-121 F3000",
        "Bottom Right Corner": "G1 X78.5 Y-121 F3000",
        "Bottom Left Corner": "G1 X78.5 Y-53 F3000",
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
        "Power Button": f'G1 X169 Y-131 F{FSPEED}',
        "Volume Down": f'G1 X184 Y-131 F{FSPEED}', #Test Created
        "Volume Up": f'G1 X198 Y-131 F{FSPEED}', #Test Created
        "Camera Center": f'G1 X153 Y-38 Z5 F{FSPEED}'
    }  
}



#A class for a CNC machine that has the name of the device(ex. Berta), the COM port (ex. COM26), the Camera (ex. 0), and an image path(ex. "/TestingImages/")
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
        #print("Name: " + self.name)
        #print("COM Port: " + self.COMport)
        #print("Camera: " + str(self.camera))
        #print("Image Path: " + self.imagePath)
        InfoString = "Name: " + self.name + "\nCOM Port: " + self.COMport + "\nCamera: " + str(self.camera) + "\nImage Path: " + self.imagePath
        return InfoString


#Name, ComPort, Camera, ImagePath
#CNC_MACHINE = CNCMachine("Berta", "COM26", 0, "/TestingImages/")


#A function that can be passed arguments for specific options, or they can be prompted for
def setupCNC(**options):
    n = ""
    cport = ""
    cam = 0
    ipath = ""
    #If a COMPORT is passed as an argument, use that, otherwise prompt for it
    if "COMPORT" in options:
        cport = options["COMPORT"]
    else:
        ports = serial.tools.list_ports.comports() #Initial COMPORT setup
        for port, desc, hwid in sorted(ports):
          print("{}: {} [{}]".format(port, desc, hwid))
        cport = input("Enter the COMPORT of the CNC Machine: ")
    
    #If a CameraID is passed as an argument, use that, otherwise prompt for it
    if "CameraID" in options:
        cam = options["CameraID"]
    else:
        #Show user a split view of all the attached cameras (Camera import is in Camera.py)
        cam = int(input("\nSelect Camera ID(example: 0): "))

    if "PATH" in options:
        ipath = options["PATH"]
    else:
        ipath = "/images/" + input("Enter Relative Image Path:(example: TestingImages/) ")
    
    #If a name is specified, use that, otherwise name it up with a random number
    if "Name" in options:
        n = options["Name"]
    else:
        n = "CNC_"+str(random.randint(0, 100000))
    C = CNCMachine(n, cport, cam, ipath)
    print("CNC Object Created")
    print(C)
    return C
    



cls() #Clear the Screen


if len(sys.argv) < 2:
    #Run setup if no arguments are passed
    cnc = setupCNC()
else:
    #Run setup if arguments are passed
    #If one option is passed
    if len(sys.argv) == 2:
        if sys.argv[1] == "help":
            print("Options: COMPORT, CameraID, PATH, Name")
        else:
            cnc = setupCNC(COMPORT=sys.argv[1])
    #If two options are passed
    elif len(sys.argv) == 3:
        cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2])
    #If three options are passed
    elif len(sys.argv) == 4:
        cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3])
    #If four options are passed
    elif len(sys.argv) == 5:
      cnc = setupCNC(COMPORT=sys.argv[1], CameraID=sys.argv[2], PATH=sys.argv[3], Name=sys.argv[4])



ser = serial.Serial(cnc.COMport, 115200, timeout=1)
setupConnection(ser)
command(ser, "G90") #Set the position to absolute mode

