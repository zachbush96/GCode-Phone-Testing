#Pip3 install serial
import serial
import time
from datetime import datetime
import time
import math
'''

'  ████████╗ ██████╗ ██████╗  ██████╗ 
'  ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗
'     ██║   ██║   ██║██║  ██║██║   ██║
'     ██║   ██║   ██║██║  ██║██║   ██║
'     ██║   ╚██████╔╝██████╔╝╚██████╔╝
'     ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ 
'                                     
- Find an API that can get phone dimensions and screen dimensions []
- Create a menu with options to perform tasks [] (
    Set 0's, 
    Set Phone Model[display cordinates,test cordinates], 
    Start Test[rgb, touch, sensors, etc.],
    change/set frequently used variables
    )
- Calculate the screen coordinates based on the phone dimensions and return GCode [✅]
- Top 5 phones in facility and create profiles for each []
- Swap from Spindle control to finger control (When to touch, drap, and lift) []
- Function that accepts length in mm and returns Gcode to move that length []
- How many mm are between X10 and X20? []
- How many mm are between Y10 and Y20? []
- Read in a GCode file (*.nc) and send it over serial []


Helpful Websites:
https://marlinfw.org/docs/gcode/M083.html
https://www.sainsmart.com/blogs/news/grbl-v1-1-quick-reference
https://smoothieware.org/on_boot.gcode
https://smoothieware.org/supported-g-codes

'''
TROUBLESHOOTING = True
BACKOFF = 5 #Hit the limit switch and and then move back a few mm with the force of BACKOFF_FORCE
BACKOFF_FORCE = 1000
COMPORT = "COM26"
SCREEN_CORDINATES_PADDING = BACKOFF + 1
#FSPEED = 1000 #Feed speed
FSPEED = 3000

def command(ser, strCommand):
  time.sleep(.25)
  ser.write(str.encode(strCommand+"\r\n"))
  response = ser.readline().decode('utf-8')
  if(TROUBLESHOOTING):
    print("Sent:" + str(strCommand) + " received:" + response)
#Sends a few blank commands to the controller to clear the buffer
def setupConnection(ser):
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
  command(ser, " ")
#Goes to the limit switch of each axis, scoots off the limit switch by *BACKOFF* millimeters, and sets the current position to 0,0,0
def set00(ser):
  #At the end of this block - the X cordinate is alligned with the hole
    #Setup X Axis
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 X-300 F{FSPEED}') #Move to the left
    time.sleep(10) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("X Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 X100 F{FSPEED}') #Move to the right
    time.sleep(1)
    ser.close()
    print("X Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
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
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 Y300 F{FSPEED}') #Move Up 
    time.sleep(10) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Y Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Y-100 F{FSPEED}') #Move Down until the limit switch releases
    time.sleep(1)
    ser.close() #Close the connection after releasing the limit switch
    print("Y Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
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
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 Z300 F{FSPEED}') #Move Z axis Up 
    time.sleep(3) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Z Axis switch hit")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Cleae any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Z-100 F{FSPEED}') #Move Down until the limit switch releases
    time.sleep(3)
    ser.close() #Close the connection after releasing the limit switch
    print("Z Axis switch released")
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(COMPORT, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Clear any alarms
    command(ser, "$H")
    time.sleep(1)
    command(ser, f'G1 Z-{BACKOFF} FF{BACKOFF_FORCE}') #Move Down on the Z axis
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
#Turns on the spindle at differeing speeds, then turns it off
def SpinningFun():
  for x in range(10):
    speed = (x / .8) * 85
    command(ser, "M3 S"+str(speed))
    time.sleep(.05)
    command(ser, "M5")
#Accepts the current Serial connection, closes it, and opens a new one
def resetConnection(ser):
  ser.close()
  newConnection = serial.Serial(COMPORT, 115200, timeout=1)
  setupConnection(newConnection)
  return newConnection
#A function that asks for user input and send that input over seial
def getUserInput():
  userInput = input("Enter a command: ")
  command(ser, userInput)

#A function that calculates a phones screen X and Y coordinates given the phones X length and Y length in millimeters
#Returns a dict. with gcode for the corners of the phone
def calculateScreenCoordinates(xLength, yLength):
    StartingX = 150 + (xLength / 2) - 8 #Subtracting 15 to account for the inaccurate screen test
    StartingY = 90 - (yLength / 2) #The starting corner is the center of the screen minus half the width of the screen
    topLeftCorner = "G1 X"+str(StartingX)+" Y-"+str(StartingY)+f' F{FSPEED}'
    topRightCornerX = 150 + (xLength / 2) -8 #Subtracing 15 for the inaccurate screen test
    topRightCornerY = 90 + (yLength / 2) - SCREEN_CORDINATES_PADDING #I shouldnt have to be using this padding, but I am
    topRightCorner = "G1 X"+str(topRightCornerX)+" Y-"+str(topRightCornerY)+f' F{FSPEED}'
    bottomRightCornerX = 150 - (xLength / 2) + SCREEN_CORDINATES_PADDING #I shouldnt have to be using this padding, but I am
    bottomRightCornerY = 90 + (yLength / 2) - SCREEN_CORDINATES_PADDING #I shouldnt have to be using this padding, but I am
    bottomRightCorner = "G1 X"+str(bottomRightCornerX)+" Y-"+str(bottomRightCornerY)+f' F{FSPEED}'
    bottomLeftCornerX = 150 - (xLength / 2) + SCREEN_CORDINATES_PADDING #I shouldnt have to be using this padding, but I am
    bottomLeftCornerY = 90 - (yLength / 2)
    bottomLeftCorner = "G1 X"+str(bottomLeftCornerX)+" Y-"+str(bottomLeftCornerY)+f' F{FSPEED}'
    
    if(TROUBLESHOOTING):
      print("Top Left Corner: "+topLeftCorner + " Top Right Corner: "+topRightCorner + " Bottom Right Corner: "+bottomRightCorner + " Bottom Left Corner: "+bottomLeftCorner)
    return [topLeftCorner, topRightCorner, bottomRightCorner, bottomLeftCorner] #Returns an array of the 4 corners of the screen
#Calulate the screen size of a phone given the diagnol size in mm and the aspect ration of the screen
def calculateScreenSize(DeviceProfile):
    #Calculate the height of the screen
    height = DeviceProfile["Display"]["Diagnol Size"] / math.sqrt(1 + (DeviceProfile["Display"]["Aspect Ratio"] * DeviceProfile["Display"]["Aspect Ratio"]))
    #Calculate the width of the screen
    width = height * DeviceProfile["Display"]["Aspect Ratio"]
   
    DeviceProfile["Display"]["Width"] = width
    DeviceProfile["Display"]["Height"] = height
    if(TROUBLESHOOTING):
      print("Screen Width: "+str(width)+" Screen Height: "+str(height))
      print("Device Profile Width/Heigth Updated")
    return [width, height]
#Calculate locaiton of test buttons and update the Device Profile
def calculateTestButtonCoordinates(DeviceProfile):
  RedLocation = "G1 X"+ str(int(150 + (DeviceProfile["Display"]["Width"] / 2) - DeviceProfile["Display"]["Width"] / DeviceProfile["testLocations"]["Test Columns"] + DeviceProfile["testLocations"]["Buffer"])) + " Y" + str(int(-90 + (DeviceProfile["Display"]["Height"] / 3))) + f' F{FSPEED}'
  GreenLocation = "G1 X"+ str(int(150 + (DeviceProfile["Display"]["Width"] / 2) - DeviceProfile["Display"]["Width"] / DeviceProfile["testLocations"]["Test Columns"] + DeviceProfile["testLocations"]["Buffer"])) + " Y" + str(int(-90 + (DeviceProfile["Display"]["Height"] / 3) - (DeviceProfile["Display"]["Height"] / 3))) + f' F{FSPEED}'
  Blue = "G1 X"+ str(int(150 + (DeviceProfile["Display"]["Width"] / 2) - DeviceProfile["Display"]["Width"] / DeviceProfile["testLocations"]["Test Columns"] + DeviceProfile["testLocations"]["Buffer"])) + " Y" + str(int(-90 + (DeviceProfile["Display"]["Height"] / 3) - (DeviceProfile["Display"]["Height"] / 3) - (DeviceProfile["Display"]["Height"] / 3))) + f' F{FSPEED}'
  Touch = "G1 X" + str(180) + " Y-90" +  f' F{FSPEED}'
  Version = "G1 X" + str(117) + " Y-110" + f' F{FSPEED}'
  DeviceProfile["testLocations"]["Red"] = RedLocation
  DeviceProfile["testLocations"]["Green"] = GreenLocation
  DeviceProfile["testLocations"]["Blue"] = Blue
  DeviceProfile["testLocations"]["Touch"] = Touch
  DeviceProfile["testLocations"]["Version"] = Version
  if(TROUBLESHOOTING):  
    print(DeviceProfile)
  return [RedLocation, GreenLocation, Blue, Touch, Version]



#Device Profiles
GalaxyNote20Ultra = {
    #Find an AIP we can query this information from
    "X Length": 164.8,
    "Y Length": 77.2,
    "Z Length": 8.1,
    "Display": {
        "Diagnol Size": 175,
        "Aspect Ratio": 19.3/9,
        "Width": 0, #158.6
        "Height": 0, #73.95
        "Top Left Corner": "",
        "Top Right Corner": "",
        "Bottom Right Corner": "",
        "Bottom Left Corner": ""
    },
    "testLocations": {
        "Test Columns": 7,
        "Buffer": 11,#mm
        "Red": "", 
        "Green": "",
        "Blue": "",
        "Touch": "",
        "Version": ""
    }  
}
#Updates the device profile with the screen size
calculateScreenSize(GalaxyNote20Ultra)


#MAIN CODE
ser = serial.Serial(COMPORT, 115200, timeout=1)
setupConnection(ser)
set00(ser)
ser = serial.Serial(COMPORT, 115200, timeout=1)
setupConnection(ser)
#Lower the Z axis almost all the way
command(ser, f'G1 Z-20 F{FSPEED}')
SpinningFun()
print("Loop Starting")
#Top left = 0 , Top right = 1, Bottom right = 2, Bottom left = 3
Coordinates = calculateScreenCoordinates(GalaxyNote20Ultra["X Length"], GalaxyNote20Ultra["Y Length"])
TestCoordinates = calculateTestButtonCoordinates(GalaxyNote20Ultra)
command(ser, Coordinates[0])
command(ser, Coordinates[1])
command(ser, Coordinates[2])
command(ser, Coordinates[3])
command(ser, Coordinates[0])
command(ser, Coordinates[1])
command(ser, Coordinates[0])
command(ser, Coordinates[2])
SpinningFun()
command(ser, TestCoordinates[0])
command(ser, TestCoordinates[1])
command(ser, TestCoordinates[2])
command(ser, TestCoordinates[3])
command(ser, TestCoordinates[4])
SpinningFun()
while True:
  command(ser, TestCoordinates[0])
  command(ser, TestCoordinates[1])
