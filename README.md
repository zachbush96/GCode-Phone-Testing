'     _____ _   _  _____   _____  _                        _______        _   _             
'    / ____| \ | |/ ____| |  __ \| |                      |__   __|      | | (_)            
'   | |    |  \| | |      | |__) | |__   ___  _ __   ___     | | ___  ___| |_ _ _ __   __ _ 
'   | |    | . ` | |      |  ___/| '_ \ / _ \| '_ \ / _ \    | |/ _ \/ __| __| | '_ \ / _` |
'   | |____| |\  | |____  | |    | | | | (_) | | | |  __/    | |  __/\__ \ |_| | | | | (_| |
'    \_____|_| \_|\_____| |_|    |_| |_|\___/|_| |_|\___|    |_|\___||___/\__|_|_| |_|\__, |
'                                                                                      __/ |
'                                                                                     |___/ 



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
- Make the Test functions in the Menu.py dynamic to show all the possible tests the phone can do [⛔] ---HOLD--
- Make the test to test camera function [✅]
- After the color tests, the finger should move to a point on the screen (currently touching the board) [✅]
- Touch test points (corners) need to be more accurate [✅]
- Touch test should leave one square blank, take a picture, then complete the test []
- Pass an argument to the Meny.py to select a COM port, if none is passed - prompt the user to select[✅]
- Take pictures of the phone screen after each color test automatically [✅]
- How to link a COMPORT and camera to eachother [ ✅
    - Created a class called CNCMachine that holds the COMport, Camera ID, Name, and file path to save images
    - Called the class via the SetupCNC function that can be passed multiple options and will prompt for the others
    ]
- Sub Key test needs to take a picture after hitting each key to make sure the key is pressed []
- Address cameras based on a selection instead of a hard coded value [✅
    - Camers are addressed via the CNCMachine class (example cnc.camera)  
    ]
- Error handling for camera failure (*USUALLY CAUSED BY CAMERA BEING OPEN IN ANOTHER PROGRAM*) []
- The images folder contain the machine name folder - but it should also create a folder for the device. (Folder name an IMEI?) []


- RUNNING OPTIONS python ObjectBasedGCode.py {COMPORT} {CAMERA NUMBER} {}
- RUNNING EXAMPLES
    - python Menu.py COM3 0 (*uses COMPORT 3 and the first camera*)
    - python Menu.py COM28 1 BertaImages Berta zero (*Uses COMPORT 28, the second camera, and saves the images to the BertaImages folder, sets the name to Berta, and zero's out the axi's*)
    - python Menu.py COM28 1 BertaImages Berta autozero (*Uses COMPORT 28, the second camera, and saves the images to the BertaImages folder, sets the name to Berta, and zero's out the axi's and runs all the tests*)




Helpful Websites:

https://marlinfw.org/docs/gcode/M083.html

https://www.sainsmart.com/blogs/news/grbl-v1-1-quick-reference

https://smoothieware.org/on_boot.gcode

https://smoothieware.org/supported-g-codes


<!-- GETTING STARTED -->
## Getting Started
**It's assumed you have Python 3 installed
### Prerequisites

Pyserial
```sh
pip3 install serial
```

## Usage
The 'Main' package is Menu.py
### Running Examples
#### Manual Setup -  
You will be prompted to enter the COM Port, Camera ID & Directory to save images to.
```sh
python Menu.py
```
#### Specifying COM Port - 
You will be prompted to enter a Camera ID & Directory to save images to.
```sh
python Menu.py COM5
```

#### Specifying COM Port & Camera ID
You will be prompted to enter a Directory to save images to.
```sh
python Menu.py COM5 0
```

#### Specifying COM Port, Camera ID, and Image Directory
You will be brought to the main Menu
```sh
python Menu.py COM6 1 imageDirectory
```
#### Single Line Run
After specifying the COM Port, Camera ID, Image Directory, and a name
This will zero out the axis's and run all the programmed tests.
This assumes the axis's are NOT zero'd out
```sh
python Menu.py COM8 0 imageDir myName autozero
```
If the axis's ARE zero'd out this following line will start the tests automaticly
```sh
python Menu.py COM8 0 imageDir myName auto
```
