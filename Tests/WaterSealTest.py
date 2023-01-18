import tkinter as tk
import requests
from ast import arg
import sys
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import time
from supabase import create_client, Client

'''
Usage:
0. 
1. Select the COM port that the CNC machine is connected to
2. Scan the IMEI of the phone using the barcode scanner
3. Connect scanner to phone using the USB cable adapter
4. Open the baro_home app on the phone
5. Unplug the scanner from the phone
6. Tape the phone according to the instructions on the PC screen (bottom speaker, top speaker, camera, side buttons, etc.)
7. Place phone on center of CNC machine
8. Click "Start" on the PC screen
9. Wait for the test to complete and the CNC to reset
10. Remove the phone and click "Start Sending Data" on the phone to send the data to the server
'''


TROUBLESHOOTING = True
SelectedComPort = "COM0"
url = "https://zulpluhciltvsqvtrhhw.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp1bHBsdWhjaWx0dnNxdnRyaGh3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzMzNzAxMzEsImV4cCI6MTk4ODk0NjEzMX0.sLq7RhUyfpbvrzfVnrBWtyNdaXdjr-WDNVF1leSJ-Do"
client = create_client(url, api_key)
FSPEED = 3000
BACKOFF = 5
BACKOFF_FORCE = 3000




#Helper Functions
def command(ser, strCommand): #Sends a command to the controller
  time.sleep(.50)
  if ser.is_open is False: #If the serial port is not open, reopen it
    print("Reconnecting to Device")
    ser.close()
    ser1 = serial.Serial(cnc.COMport, 115200, timeout=1) #Reconecting to the device
    ser = ser1
    setupConnection(ser) #Clear the buffer
    print("Sleeping for 3 seconds...")
    time.sleep(3)
    command(ser, strCommand) #If the serial port was closed, resend the command now that the port is open
  ser.write(str.encode(strCommand+"\r\n"))
  #response = ser.readline().decode('utf-8') #<--- This is supposed to be the response from the controller, but the response doesnt mean the command was executed until the end
  response = "OK"
  if "error" in response.lower():
    print("Error: " + response)
    print("Command: " + strCommand)
  if(TROUBLESHOOTING):
    print("Sent:" + str(strCommand) + " received:" + response)
def setupConnection(ser): #Sends a few blank commands to the controller to clear the buffer\
    command(ser, " ")
    command(ser, " ")
    command(ser, " ")
    command(ser, "G90") #Set to absolute mode
def StartTest(model, imei, selectedComPort):
    ser = serial.Serial(selectedComPort, 115200, timeout=1)
    setupConnection(ser) #Clear the buffer
    command(ser, "G1 X150 Y-70 F3000") #Go to center of the CNC machine
    time.sleep(5)
    for x in range(2):
        command(ser, "G1 Z-28 F3000") #Move the Z axis down 33 millimeters
        time.sleep(3)
        command(ser, "M3 S5000") #Turn on the AIR
        time.sleep(6)
        command(ser, "M5") #Turn off the AIR
        time.sleep(2)
        command(ser, "G1 Z0 F3000")
    command(ser, "G90") #Set to absolute mode
    command(ser, "G1 X0 Y0 Z0")
    time.sleep(9)
def getInfoFromSupaBase(phone_model):
    print(f'Getting infor for {phone_model.lower()} from SupaBase')
    try:
        data = client.table("MainTable").select("*").eq("phone_model", phone_model.lower()).execute()
        return data.data
    except:
        print("Error getting data from SupaBase")
        return None
def set00(ser, cnc): #Goes to the limit switch of each axis, scoots off the limit switch by *BACKOFF* millimeters, and sets the current position to 0,0,0
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")

    #Setup X Axis
    command(ser, "G91") #Set to relative mode
    command(ser, f'G1 X-300 F{FSPEED}') #Move to the left
    time.sleep(7) #Sleep while waiting for large move to complete
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
    time.sleep(7) #Sleep while waiting for large move to complete
    command(ser, "$X") #Reset the alarm
    command(ser, "$H")
    ser.close() #Close the connection
    print("Y Axis switch hit")
    
    time.sleep(1) #Wait for the connection to close
    ser = serial.Serial(cnc.COMport, 115200, timeout=1) #Reopen the connection
    setupConnection(ser) #Setup the new connection
    command(ser, "$X") #Clear any alarms
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
    command(ser, f'G1 Y-{BACKOFF + 20} FF{BACKOFF_FORCE}') #Move Down
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
    time.sleep(5) #Sleep while waiting for large move to complete
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
class CNC:
    def __init__(self):
        self.COMport = ""
    


    

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IMEI GUI")
        self.root.geometry("400x200")
        self.state = False
        self.imei_var = tk.StringVar()
        self.imei_entry = tk.Entry(self.root, textvariable=self.imei_var)
        self.imei_entry.pack(padx=10, pady=10)
        self.imei_entry.focus_set()

        self.com_port_var = tk.StringVar()
        self.com_port_var.set("Select COM Port")
        self.com_port_menu = tk.OptionMenu(self.root, self.com_port_var, *self.get_com_ports())
        self.com_port_menu.pack(padx=10, pady=10)
        self.com_port_selected = self.get_selected_com_port()

        self.make_model_text = tk.Text(self.root, height=2)
        self.make_model_text.pack(padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Start", command=self.start)
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        self.stop_button.pack(side="right", padx=10, pady=10)

        self.spindle_button = tk.Button(self.root, text="Spindle", command=self.spindle)
        self.spindle_button.pack(side="right", padx=10, pady=10)

        #Button that will zero the CNC
        self.zero_button = tk.Button(self.root, text="Zero", command=self.go_to_00)
        self.zero_button.pack(side="right", padx=10, pady=10)
    def spindle(self):
        ser = serial.Serial(self.get_selected_com_port(), 115200, timeout=1) #Setup the serial port
        setupConnection(ser) #Clear the buffer
        if self.state == False:
            command(ser, "M3 S5000") #Press the finger down
            self.state = True
        else:
            command(ser, "M5") #Raise the finger up
            self.state = False
        ser.close() #Close the connection
    def get_com_ports(self):
        com_ports = []
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            com_ports.append(port.device)
        return com_ports
    def get_selected_com_port(self):
        print("This function juust got hit")
        return self.com_port_var.get()
    def go_to_00(self):
        ser = serial.Serial(self.get_selected_com_port(), 115200, timeout=1)
        setupConnection(ser)
        #Create a dict object with an attribute called COMport that is the selected COM port
        cnc = CNC()
        cnc.COMport = self.get_selected_com_port()
        set00(ser,cnc)
        #Update the text box with "READY"
        self.make_model_text.delete("1.0", "end")
        self.make_model_text.insert("1.0", "READY")
        ser.close()
    def start(self):
        if self.get_selected_com_port() == "Select COM Port":
            self.make_model_text.delete("1.0", "end")
            self.make_model_text.insert("1.0", "Please select a COM Port")
            return
        if self.imei_var.get() == "":
            self.make_model_text.delete("1.0", "end")
            self.make_model_text.insert("1.0", "Please enter an IMEI")
            return
        imei = self.imei_var.get()
        headers = {'Accept': 'text/plain','APIClient': 'Serial','APIKey': '40166963-025F-4E4C-B501-6FE3696E153E'}
        response = requests.get('https://robotbeta.electronicsrenewal.com/Serial?imei=' + imei, headers=headers)
        print(response.json())
        try:
            make = response.json()['data']['received_make']
            model = response.json()['data']['received_model']
            print(f'Here --- Make: {make} | Model: {model}')
            self.make_model_text.delete("1.0", "end")
            self.make_model_text.insert("1.0", f'Make: {make} | Model: {model}')
        except:
            self.make_model_text.delete("1.0", "end")
            self.make_model_text.insert("1.0", "IMEI not found in system")
        if model:
            phone_data = getInfoFromSupaBase(model)
            try:
                print("Supabase Data: ")
                print(f'size_x: {phone_data[0]["size_x"]}  |  size_y: {phone_data[0]["size_y"]}  |  acceptable_change: {phone_data[0]["acceptable_change"]}')
                self.make_model_text.insert("2.0", f'\nAcceptable Change: {phone_data[0]["acceptable_change"]}')
            except:
                print("No data found in Supabase")
                self.make_model_text.insert("2.0", f'\nAcceptable Change Undetermined')
            SelectedComPort = self.get_selected_com_port()
            StartTest(model, imei, SelectedComPort)
        #Clear the IMEI entry box and set focus to it
        #self.imei_entry.delete(0, "end")
        self.imei_entry.focus_set()

    def stop(self):
        imei = self.imei_var.get()
        com_port = self.com_port_var.get()
        print(f"Stop button clicked with IMEI: {imei} and COM Port: {com_port}")



app = App()
app.root.mainloop()
