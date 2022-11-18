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
- Error handling for camera failure (*USUALLY CAUSED BY CAMERA BEING OPEN IN ANOTHER PROGRAM*) [✅]
- The images folder contain the machine name folder - but it should also create a folder for the device. (Folder name an IMEI?) []
- I think the CNCMachine object should also hold the Serial Connection object []
- This will eventually need to send the test results to our API []
- Try to have as much processing done off the main thread as possible []
    - Image analysis
    - Audio analysis
    - API calls
- Make the list of possible tests dynamic, so that if a new test is added, it will be added to a single list [✅]
    - Currently new tests need to be added to the Menu.py(line50) and ObjectBasedGCode.py(line615)
- Can the movements be speed up and still be accurate?, optimize movement routes?, optimize test order? []
- Set sleep to a single variable and use that variable for all sleeps []
    - Some sleep times will need to be adjusted to account for long travel distances
- Solution to make sure all the images are consistant (brightness, contrast, focus, etc) []
    - Will this need to be done on the camera, or in the software?
- Each test should have a pass/fail result []
- Each test should end with being back at the 'home' screen []
- Come up with a way to make sure the audio test noise does not interfere with other devices []
    - "Soundproof the container"?
- Sound Test needs to measure the volume of the sound, and make sure it is within a certain range []
- Sound Test needs to be able to play a sound file []
    - What is that range?
- Update the phone device profile with the test results []


----- Once I get the touch Device -----
- Update screenTest fucntion (line 206) to raise itself early on the bottom left corner of the screen, take a picture, and then "complete" the test by touching that exact corner []
- Update the 'click' function to use the piston/spindle controller and not move the Z-Axis as much []



Helpful Websites:

https://marlinfw.org/docs/gcode/M083.html

https://www.sainsmart.com/blogs/news/grbl-v1-1-quick-reference

https://smoothieware.org/on_boot.gcode

https://smoothieware.org/supported-g-codes



## Getting Started
**It's assumed you have Python 3 installed
### Prerequisites

Pyserial
```sh
pip3 install serial
```
Torch
```sh
pip3 install torch torchvision torchaudio
```
EasyOCR (https://github.com/JaidedAI/EasyOCR)
```sh
pip install easyocr
```



## Usage
The 'Main' package is Menu.py
### Running Examples
#### Manual Setup -  
You will be prompted to enter the COM Port, Camera ID & Directory to save images to.
```sh
python Menu.py
```
#### Automatic Setup -
You can pass the COM Port, Camera ID, Name & Directory to save images to as arguments.
```sh
python Menu.py --Port COM3 --Camera 0 --Name CNC1 --Images myImages
```
AutoRun - If you supply all the needed information, the program can auto run the tests.
```sh
python Menu.py --Port COM3 --Camera 0 --Name CNC1 --Images myImages -A
```
Auto 0 - If you supply all the needed information, the program can 0 itself out
```sh
python Menu.py --Port COM3 --Camera 0 --Name CNC1 --Images myImages -Z
```
Auto 0 & AutoRun - If you supply all the needed information, the program can 0 itself out and then run the tests.
```sh
python Menu.py --Port COM3 --Camera 0 --Name CNC1 --Images myImages -Z -A
```
