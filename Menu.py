import random
from ObjectBasedGCode import *
from Camera import *
import serial

cls()
TROUBLESHOOTING = True
Testing_Device = GalaxyNote20Ultra


while True:
    print("MAIN MENU")
    print("1. Zero Out Axis")
    print("2. Start Tests")
    print("3. Change Variables")
    print("4. Custom Code")
    print("5. Setup Connection")
    print("6. Camera Testing")
    print("7. Exit")
    print("8. CNC Device Profile")
    choice = input("Enter choice: ")

    if choice == "1": #Zero Out Axis
        print("Zeroing Out Axis")
        set00(ser, cnc)
    
    elif choice == "2": #Start Tests
        print("1. Start All Tests")
        print("2. Red")
        print("3. Green")
        print("4. Blue")
        print("5. Touch Test")
        print("7. Hit Power Button")
        print("6. MAIN MENU")
        print("8. Volume Down Button")
        print("9. Volume Up Button")
        choice = input("Enter choice: ")
        print(f'Serial Connection Details {ser}')
        if ser.is_open is False:
            print("Reconnecting to Device")
            ser = serial.Serial(cnc.COMport, 115200, timeout=1)
            setupConnection(ser)
        if choice == "1":
            #SHOULD be a for loop that runs through all the tests
            print("Starting All Tests")
            Red(ser, Testing_Device)
            Green(ser, Testing_Device)
            Blue(ser, Testing_Device)
            screenTest(ser, Testing_Device)
            PowerButton(ser, Testing_Device)
            VolumeDown(ser, Testing_Device)
            VolumeUp(ser, Testing_Device)
            Receiver(ser, Testing_Device)
            Vibration(ser, Testing_Device)
            MegaCam(ser, Testing_Device)
            Sensor(ser, Testing_Device)
            command(ser, "G1 X0 Y0 Z0")
    
        elif choice == "2": #Red
            print("Starting Red Test")
            Red(ser, Testing_Device)                
        
        elif choice == "3": #Green
            print("Starting Green Test")
            Green(ser, Testing_Device)
        
        elif choice == "4": #Blue
            Blue(ser, Testing_Device)
        
        elif choice == "5": #Touch Test
            print("Starting Touch Test")
            screenTest(ser, Testing_Device)        
        
        elif choice == "6": #Main Menu
            print("Returning to MAIN MENU")        
        
        elif choice == "7": #Power Button
            print("Starting Power Button Test")
            PowerButton(ser, Testing_Device)        
        
        elif choice == "8": #Volume Down Button
            print("Starting Volume Down Test")
            VolumeDown(ser, Testing_Device)       
        
        elif choice == "9": #Volume Up Button
            print("Starting Volume Up Test")
            VolumeUp(ser, Testing_Device)
        
        else:
            print("Invalid Input")    
    
    elif choice == "3": #Change Variables
        print("Change Variables")
        print("1. SPEED")
        print("2. SCREEN_CORDINATES_PADDING")
        print("3. MAIN MENU")
        choice = input("Enter choice: ")
        if choice == "1":
            print("Changing SPEED")
            FSPEED = input("Enter new FSPEED: ")
            #Code to change SPEED
        elif choice == "2":
            print("Chainging SCREEN_CORDINATES_PADDING")
            SCREEN_CORDINATES_PADDING = input("Enter new SCREEN_CORDINATES_PADDING: ")
            #Code to change BUFFER SIZE
        elif choice == "3":
            print("Returning to MAIN MENU")
    
    elif choice == "5": #Setup Connection
        print("Exiting")
        break
    
    elif choice == "4": #Custom Code
        userInput = input("Enter Code: ")
        if "quit" in userInput:
            print("Exiting")
            break
        else:
            setupConnection(ser)
            getUserInput(ser, userInput)
    
    elif choice == "5": #Setup Connection
        try:
            ser.close()
        except:
            print("No COMPORT to close")
        print("Current Connection: " + COMPORT)
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))

        COMPORT = input("Select COM PORT(example: COM26): ")
        ser = serial.Serial(COMPORT, 115200, timeout=1)
        setupConnection(ser)
    
    elif choice == "6": #Camera Testing
        print("Camera Testing")
        print("1. Center Camera") #G1 X150 Y-45 Z-5
        print("2. Take Picture")
        print("3. Show Camera View")
        print("4. Show all Camera Views")

        choice = input("Enter choice: ")
        if ser.is_open is False:
            print("Reconnecting to Device")
            ser = serial.Serial(COMPORT, 115200, timeout=1)
            setupConnection(ser)
        if choice == "1": #Center Camera
            print("Centering Camera")
            command(ser, Testing_Device['testLocations']['Camera Center'])
        if choice == "2": #Take Picture using camera selected in the CNC Profile
            print("Taking Picture")
            capturePicture("TestPicture" + str(random.randint(0, 100000)), cnc)
        if choice == "3": #Show Camera View of camera selected in the CNC Profile
            print("Showing Camera View")
            showCameraView(cnc)
        if choice == "4":
            print("Showing all Camera Views")
            showAllConnectedCameras()
    
    elif choice == "8": #CNC Device Profile
        print("CNC Device Profile\n")
        print(f'Profile: {cnc.viewSelf()}')
        print("1. Change CNC Device Profile")
        print("2. MAIN MENU")
        choice = input("Enter choice: ")
        if choice == "1":
            print("1. Update COMPORT")
            print("2. Update Camera Number")
            print("3. Update Name")
            print("4. Update Image Path")
            print("5. Main Menu")
            choice = input("Enter choice: ")
            if choice == "1":
                cnc.COMport = input("Enter COMPORT: ")
            elif choice == "2":
                cnc.camera = input("Enter Camera Number: ")
            elif choice == "3":
                cnc.name = input("Enter Name: ")
            elif choice == "4":
                cnc.imagePath = input("Enter Image Path: ")
            elif choice == "5":
                print("Returning to MAIN MENU")
            else:
                print("Invalid Input")

    elif choice == "7": #Exit
        
        print("Exiting")
        break