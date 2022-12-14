'''
'     ______ _   __ ______   ____   __                           ______             __   _              
'    / ____// | / // ____/  / __ \ / /_   ____   ____   ___     /_  __/___   _____ / /_ (_)____   ____ _
'   / /    /  |/ // /      / /_/ // __ \ / __ \ / __ \ / _ \     / /  / _ \ / ___// __// // __ \ / __ `/
'  / /___ / /|  // /___   / ____// / / // /_/ // / / //  __/    / /  /  __/(__  )/ /_ / // / / // /_/ / 
'  \____//_/ |_/ \____/  /_/    /_/ /_/ \____//_/ /_/ \___/    /_/   \___//____/ \__//_//_/ /_/ \__, /  
'                                                                                              /____/   
'''

from ast import arg
#from ensurepip import version
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
from logger import *



#FREQUENTLY USED VARIABLES
TROUBLESHOOTING = True
BACKOFF = 5 #DO NOT CHANGE - Changing this will cause the axis to hit the switches
BACKOFF_FORCE = 3000
SCREEN_CORDINATES_PADDING = BACKOFF + 4
FSPEED = 3_000
COMPORT = ""
CountofArguments = len(sys.argv)
Auto = False
Zero = False
Name = None
Port = None
Image = None
Camera = None
gs20u = None



#Helper Functions
def cls():
  #os.system('cls' if os.name=='nt' else 'clear')
  pass

def command(ser, strCommand): #Sends a command to the controller
  
  time.sleep(.25)
  
  if ser.is_open is False: #If the serial port is not open, reopen it
    print("Reconnecting to Device")
    ser.close()
    ser1 = serial.Serial(cnc.COMport, 115200, timeout=1) #Reconecting to the device
    ser = ser1
    setupConnection(ser) #Clear the buffer
    print("Sleeping for 3 seconds...")
    time.sleep(10)
    command(ser, strCommand) #If the serial port was closed, resend the command now that the port is open
  
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
    command(ser, f'G1 Y-{BACKOFF + 1} FF{BACKOFF_FORCE}') #Move Down
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
    print("First Z move up sent")
    command(ser, f'G1 Z300 F{FSPEED}') #Move Z axis Up again 
    print("Second Z move up sent")
    time.sleep(10) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Z Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Clear any alarms
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

def click(ser): #Currently - Lower and then raise the Z-Axis - Future - lower and raise the Z-Axis and also turn on and off the spindle
  command(ser, f'G1 Z-35 F{FSPEED}')
  command(ser, f'G1 Z-30 F{FSPEED}')










#MAIN TEST FUNCTIONS
def screenTest(ser, PassedTemplate):
  print("Starting Screen Test")
  #Test order should be , Touch, Top Left corner, Top Right corner, bottom right coner, 
  #bottom left corner, top left, bottom right, bottom left, almost top right, 
  #CAMERA_IMAGE, almost top right, top right
  command(ser, PassedTemplate["testLocations"]["Touch"]) #GOTO touch button
  click(ser) #Touch the screen and raise back up
  command(ser, PassedTemplate["Display"]["Top Left Corner"])
  command(ser, f'G1 Z-35  F{FSPEED}')
  command(ser, PassedTemplate["Display"]["Top Right Corner"])
  command(ser, PassedTemplate["Display"]["Bottom Right Corner"])
  command(ser, PassedTemplate["Display"]["Bottom Left Corner"])
  command(ser, PassedTemplate["Display"]["Top Left Corner"])
  command(ser, PassedTemplate["Display"]["Bottom Right Corner"])
  command(ser, PassedTemplate["Display"]["Bottom Left Corner"])
  command(ser, PassedTemplate["Display"]["Almost Top Right Corner"])
  command(ser, PassedTemplate["testLocations"]["Camera Center"]) #Take a picture of an ~almost~ complete test
  time.sleep(63) #Wait 1 mminute
  path = capturePicture("afterScreenTest" + gs20u.IMEI, cnc) #Returns the path to the new image
  result = analyzeTouchTest(path) #Analyze the image
  #Save the result to the log
  addToIMEILog(gs20u.IMEI, {
    "IMEI": gs20u.IMEI,
    "Test": "Screen Test",
    "Result": result
    })
  #Finish the test
  command(ser, PassedTemplate["Display"]["Almost Top Right Corner"])
  command(ser, f'G1 Z-35 F{FSPEED}') #Touch the screen
  command(ser, PassedTemplate["Display"]["Top Right Corner"])
  command(ser, f'G1 Z-15 F{FSPEED}')

def Red(ser, PassedTemplate):
  print("Starting Red LED Test - Internal")
  command(ser, PassedTemplate['testLocations']['Red'])
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(15)  
  print("Just sent Camera Center")
  capturePicture("GoodRed" + str(gs20u.IMEI), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  #command(ser, "G1 Z-24")
  click(ser)

def Green(ser, PassedTemplate):
  print("Starting Green LED Test")
  command(ser, PassedTemplate['testLocations']['Green'])
  command(ser, f'G1 Z-35  F{FSPEED}')
  command(ser, "G1 Z-30")
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodGreeen" + str(gs20u.IMEI), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  command(ser, "G1 Z-35")
  command(ser, "G1 Z-21")

def Blue(ser, PassedTemplate):
  print("Starting Blue LED Test")
  command(ser, PassedTemplate['testLocations']['Blue'])
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(15)
  capturePicture("GoodBlue" + str(gs20u.IMEI), cnc)
  command(ser, f'G1 Y-66 F{FSPEED}') #Move to a touchable location
  click(ser)

def PowerButton(ser, PassedTemplate):
  print("Clicking Power Button")
  command(ser, PassedTemplate['testLocations']['Power Button'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeDown(ser, PassedTemplate):
  print("Clicking Volume Down Button")
  command(ser, PassedTemplate['testLocations']['Volume Down'])
  command(ser, "G1 Z-25")  #Lower the pen
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, "G1 Z-15")  #Raise the finger

def VolumeUp(ser, PassedTemplate):
  print("Clicking Volume Up Button")
  command(ser, PassedTemplate['testLocations']['Volume Up'])
  command(ser, "G1 Z-25")
  #Lower the finger
  command(ser, "M1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  #Raise the finger
  command(ser, "G1 Z-15")

def Receiver(ser, PassedTemplate):
  print("Starting Receiver Test")
  command(ser, PassedTemplate['testLocations']['Receiver'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(8)
  capturePicture("WhiteScreen" + str(gs20u.IMEI), cnc)
  command(ser, "G1 Y-58") #Move to a touchable location
  click(ser)

def Vibration(ser, PassedTemplate): #Need a way to check if the vibration motor is working
  print("Starting Vibration Test")
  command(ser, PassedTemplate['testLocations']['Vibration'])
  click(ser) #Turn on the vibration motor
  click(ser) #Turn off the vibration motor

def MegaCam(ser, PassedTemplate): #Image is very dark compared to the other images
  print("Starting MegaCam Test")
  command(ser, PassedTemplate['testLocations']['Mega Cam'])
  click(ser)
  command(ser, "G1 X91 Y-90")   #Move to camera capture botton
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(30)
  capturePicture("MegaCam" + str(gs20u.IMEI), cnc)
  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)
  click(ser)

def Sensor(ser, PassedTemplate): #Image is very bright compared to the other images
  print("Starting Sensor Test")
  command(ser, PassedTemplate['testLocations']['Sensor'])
  click(ser)
  #Take a picture of the screen
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  #input("Press Enter to take a picture")
  time.sleep(30)
  capturePicture("Sensor" + str(gs20u.IMEI), cnc)
  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)
  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)

def Speaker(ser, PassedTemplate): #Needs some way to test the audio levels that play after the botton is pressed
  print("Starting Speaker Test")
  command(ser, PassedTemplate['testLocations']['Speaker'])
  click(ser) #All Speakers
  #TestAudioLevels()
  click(ser) #Bottom Speaker
  #TestAudioLevels()
  click(ser) #Top Speaker
  #TestAudioLevels()
  click(ser) #Stop the audio

def SubKey(ser, PassedTemplate): 

  print("Starting SubKey Test")
  command(ser, PassedTemplate['testLocations']['Sub Key'])
  click(ser)

  imagePaths = []
  individualTestResults = []
  results = {}
  
  command(ser, PassedTemplate['testLocations']['Volume Up'])
  print("Just hit Volume Up")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  whiteImage = capturePicture("SubKey_VolumeUp" + str(gs20u.IMEI), cnc) #Takes a picture and returns the path to the image
  imagePaths.append(whiteImage)


  command(ser, PassedTemplate['testLocations']['Volume Down'])
  print("Just hit Volume Down")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  greenImage = capturePicture("SubKey_VolumeDown" + str(gs20u.IMEI), cnc)
  imagePaths.append(greenImage)
  
  command(ser, PassedTemplate['testLocations']['Power Button'])
  print("Just hit Power Button")
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  redImage = capturePicture("SubKey_PowerButton" + str(gs20u.IMEI), cnc)
  imagePaths.append(redImage) #Stores the path to the image
  
  command(ser, PassedTemplate['Display']['Back Button'])
  print("Just hit Back Button")
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  magentaImage = capturePicture("SubKey_BackButton" + str(gs20u.IMEI), cnc)
  imagePaths.append(magentaImage) #Stores the path to the image
  
  command(ser, PassedTemplate['Display']['Home Button'])
  print("Just hit Home Button")
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  blueImage = capturePicture("SubKey_HomeButton" + str(gs20u.IMEI), cnc)
  imagePaths.append(blueImage) #Stores the path to the image
  
  command(ser, PassedTemplate['Display']['Menu Button'])
  print("Just hit Menu Button")
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  print("Just sent Camera Center")
  time.sleep(20)
  orangeImage = capturePicture("SubKey_MenuButton" + str(gs20u.IMEI), cnc)
  imagePaths.append(orangeImage) #Stores the path to the image

  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)
  click(ser)
  command(ser, 'G1 Z-5 F{FSPEED}')
  print("Starting SubKey Image Testing")
  for imagePath in imagePaths:
    r = testImages(imagePath) #In the Camera.py file
    individualTestResults.append(r)
  results['Volume Up'] = individualTestResults[0]
  results['Volume Down'] = individualTestResults[1]
  results['Power'] = individualTestResults[2]
  results['Back'] = individualTestResults[3]
  results['Home'] = individualTestResults[4]
  results['Menu'] = individualTestResults[5]
  for key in results:
    addToIMEILog(
      gs20u.IMEI,
      {"IMEI": gs20u.IMEI,
      "Test": "SubKey " + key,
      "Result": results[key]})
  return results

def FrontCamera(ser, PassedTemplate): 
  print("Starting Front Camera Test")
  command(ser, PassedTemplate['testLocations']['Front Cam'])
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("FrontCamera" + str(gs20u.IMEI), cnc)
  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)
  click(ser)

def GripSensor(ser, PassedTemplate): #INCOMPLETE
  print("Starting Grip Sensor Test")
  pass

def Black(ser, PassedTemplate): 
  print("Starting Black LED Test")
  command(ser, PassedTemplate['testLocations']['Black'])
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("Black" + str(gs20u.IMEI), cnc)
  command(ser, PassedTemplate['testLocations']['Power Button'])
  command(ser, "G1 Z-25") #Lower the finger
  command(ser, "G1 Y-128") #Bump the button
  command(ser, "G1 Y-131") #Back up off the button

def HallIC(ser, PassedTemplate): #INCOMPLETE
  pass

def sPen(ser, PassedTemplate): #INCOMPLETE
  pass

def MST(ser, PassedTemplate): #INCOMPLETE
  command(ser, PassedTemplate['testLocations']['MST'])
  click(ser)
  OneTimeTrackOne = "G1 INCOMPLETE"
  OneTimeTrackTwo = "G1 INCOMPLETE"
  ContinousTrackOne = "G1 INCOMPLETE"
  ContinousTrackTwo = "G1 INCOMPLETE"
  ContinousTrackOneandTwo = "G1 INCOMPLETE"
  ContinousOff = "G1 INCOMPLETE"

def MLC(ser, PassedTemplate): #INCOMPLETE
  pass

def LoopBack(ser, PassedTemplate): #INCOMPLETE
  command(ser, PassedTemplate['testLocations']['Loop Back'])
  click(ser)
  RCV_1stMic = "G1 INCOMPLETE"
  SPK_2ndMic = "G1 INCOMPLETE"
  SPK_3rdMic = "G1 INCOMPLETE"
  EP = "G1 INCOMPLETE"
  ExitButton = "G1 INCOMPLETE"

def Version(ser, PassedTemplate): 
  print("Starting Version Test")
  command(ser, PassedTemplate['testLocations']['Version'])
  click(ser)
  command(ser, PassedTemplate['testLocations']['Camera Center'])
  time.sleep(15)
  capturePicture("Version" + str(gs20u.IMEI), cnc)
  command(ser, PassedTemplate['Display']['Back Button'])
  click(ser)
  click(ser)

def waterSeal(ser, PassedTemplate):
  #Open waterSeal app ### HANDLED EXTERNALLY ###
  #Click button to start collecting data
  command(ser, PassedTemplate['testLocations']['Water Seal']['Start'])
  #Press HARD on the middle of the screen and hold for 10 seconds
  command(ser, PassedTemplate['Display']['Center'])
  command(ser, f'G1 Z-35 F{FSPEED}') #Move Z axis down
  #extend the finger

  #Click button to stop collecting data
  command(ser, PassedTemplate['testLocations']['Water Seal']['Stop'])
  #Click the button to send the data
  command(ser, PassedTemplate['testLocations']['Water Seal']['Send'])




#Once a test is complete, add it to this array to include it in the test suite
ViableTests = [waterSeal]



#The Template stores testing information for a specific device (Galaxy Note 20 Ultra)
Template = {
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
        "Almost Top Right Corner": f'G1 X220 Y-115 F{FSPEED}', #!!UNTESTED LOCATION!! *Used for the screen test
        "Back Button":f'G1 X80.5 Y-105 F{FSPEED}',
        "Home Button":f'G1 X80.5 Y-88 F{FSPEED}',
        "Menu Button":f'G1 X80.5 Y-65 F{FSPEED}',
        "Center": f'G1 X150 Y-88 F{FSPEED}'
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
        "Camera Center": f'G1 X153 Y-38 Z5 F{FSPEED}',
        "Top Speaker": f'UNKNOWN',
        "Bottom Speaker": f'G1 X75 Y-70 Z-30 F{FSPEED}',
    } 
}

Note4Template = {
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
        "Almost Top Right Corner": f'G1 X220 Y-115 F{FSPEED}', #!!UNTESTED LOCATION!! *Used for the screen test
        "Back Button":f'G1 X80.5 Y-105 F{FSPEED}',
        "Home Button":f'G1 X80.5 Y-88 F{FSPEED}',
        "Menu Button":f'G1 X80.5 Y-65 F{FSPEED}',
        "Center": f'G1 X150 Y-88 F{FSPEED}'
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
        "Camera Center": f'G1 X153 Y-38 Z5 F{FSPEED}',
        "Top Speaker": f'UNKNOWN',
        "Bottom Speaker": f'G1 X75 Y-70 Z-30 F{FSPEED}',
    }
}

iPhone6Template = {
    "X Length": 138.3,
    "Y Length": 67.1,
    "Z Length": 6.9,
    "Display": {
        "Diagnol Size": 4.7,
        "Aspect Ratio": round(16/9, 2),
        "Width": 0, #138.3
        "Height": 0, #67.1
        "Top Left Corner": f'G1 X224.4 Y-53  F{FSPEED}',
        "Top Right Corner": f'G1 X224.4 Y-121  F{FSPEED}',
        "Bottom Right Corner": f'G1 X78.5 Y-121  F{FSPEED}',
        "Bottom Left Corner": f'G1 X78.5 Y-53  F{FSPEED}',
        "Almost Top Right Corner": f'G1 X220 Y-115 F{FSPEED}', #!!UNTESTED LOCATION!! *Used for the screen test
        "Back Button":f'G1 X80.5 Y-105 F{FSPEED}',
        "Home Button":f'G1 X80.5 Y-88 F{FSPEED}',
        "Menu Button":f'G1 X80.5 Y-65 F{FSPEED}',
        "Center": f'G1 X150 Y-88 F{FSPEED}'
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
        "Camera Center": f'G1 X153 Y-38 Z5 F{FSPEED}',
        "Top Speaker": f'UNKNOWN',
        "Bottom Speaker": f'G1 X75 Y-70 Z-30 F{FSPEED}'
        }
    }




#Device Profile - Needs to be changed to a class so we can have multiple devices
#Profile should only have IMEI and Test Results
class IndividualDeviceProfile:
  def __init__(self, IMEI):
    self.IMEI = IMEI
    self.TestResults = {}
    createIMEILog(self.IMEI)
  def addTestResult(self, TestName, TestResult):
    self.TestResults[TestName] = TestResult
    addToIMEILog(self.IMEI, {
      "IMEI": self.IMEI,
      "Test Name": TestName,
      "Test Result": TestResult
    })



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
        n = "CNC_"+str(gs20u.IMEI)
    
    C = CNCMachine(n, cport, cam, ipath) #Create the CNCMachine object
    print("CNC Object Created")
    #Log the CNCMachine object using the AddLogEntry function
    addLogEntry(C.viewSelf()) #Log the CNCMachine object
    addLogEntry("IMEI: " + str(gs20u.IMEI))
    if TROUBLESHOOTING:
        print(C.viewSelf())
    return C
    
cls() #Clear the Screen

def setupDevice(**options):
    IMEI = ""
    if options.get("IMEI") != None:
        IMEI = options.get("IMEI")
    else:
        IMEI = input("Enter the IMEI of the device: ")
    D = IndividualDeviceProfile(IMEI)
    print("Device Object Created")
    addLogEntry("Device Object Created")
    if TROUBLESHOOTING:
        print(D.IMEI)
    return D



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
    elif sys.argv[i] == "--IMEI":
          IMEI_Option = sys.argv[i+1]
          gs20u = setupDevice(IMEI = IMEI_Option)
    elif sys.argv[i] == "-A":
          Auto = True
    elif sys.argv[i] == "-Z":
          Zero = True
cnc = setupCNC(Name=Name, COMPORT=Port, CameraID=Camera, Path=Image)
ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
#If gs20u is not defined, prompt for the IMEI and create the device object
if gs20u == None:
    gs20u = setupDevice(IMEI = input("Enter the IMEI of the device: "))
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
    ser.close() #Close the serial port that was opened on line 619
    ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
    setupConnection(ser)
    command(ser, "G90")
    for x in ViableTests:
      x(ser, Template)
    print("All Tests Completed - Going to Home")
    command(ser, "G1 X0 Y0 Z0")

elif Auto and not Zero:
  print("Closing Previous connection -- auto --")
  ser.close()
  ser = serial.Serial(cnc.getComPort(), 115200, timeout=1) #Setup the serial port
  setupConnection(ser)
  command(ser, "G90")
  print("Starting all tests ---auto---")
  for x in ViableTests:
    x(ser, Template)
  print("All Tests Complete - Going to Home")
  command(ser, "G1 X0 Y0 Z0")

elif Zero and not Auto:
  set00(ser, cnc)
