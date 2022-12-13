import random
import time
import cv2 as cv
import ObjectBasedGCode
import os
import easyocr
import requests
import imutils
import numpy as np
import glob
from logger import *



#A function that returns an array containing the number of cameras attached to the computer
def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

def capturePicture(name, cncDeviceProfile):
    dirname = "IMAGES/"+cncDeviceProfile.imagePath
    if not os.path.exists(dirname): #If the folder does not exist, create it
        os.makedirs(dirname)
    try:
        camera = cv.VideoCapture(int(cncDeviceProfile.camera)) 
    except:
        print("Error: Check the camera number in the CNC Device Profile")
    camera.set(3, 3840)
    camera.set(4, 2160)
    ret, frame = camera.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...\n")
        return
    #Rotate the image 90 degrees
    frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
    #Save image to folder called IMAGES with the name of the parameter
    cv.imwrite(os.path.join(dirname, name + '.jpg'), frame)
    if ObjectBasedGCode.TROUBLESHOOTING:
        print(f'\nImage Taken: {name}\n')
        print(f'File Path: {cncDeviceProfile.imagePath +"/"+ name + ".jpg"}\n')
    camera.release()
    #Return the file path to the new image
    return cncDeviceProfile.imagePath +"/"+ name + ".jpg"
    
#Function that is mainly used for troubleshooting what the camera see's
def showCameraView(cncDeviceProfile):
    camera = cv.VideoCapture(int(cncDeviceProfile.camera))
    camera.set(3, 1280)
    camera.set(4, 720)
    time.sleep(1.5)
    while True:
        ret, frame = camera.read()
        font = cv.FONT_HERSHEY_SIMPLEX
        cv.putText(frame, "Camera Number: "+str(cncDeviceProfile.camera) + " Press Q to exit",(50, 50), font, 1, (0, 255, 255), 2, cv.LINE_4)
        cv.imshow(f'Camera', frame)
        if cv.waitKey(1) == ord("q"):
            break
    camera.release()
    cv.destroyAllWindows()

def showAllConnectedCameras():
    print(f'I have deteched {len(returnCameraIndexes())} cameras connected to this computer: {returnCameraIndexes()}')
    cameraCount = int(input("How many cameras are connected? "))
    #For each camera, show a stream of the camera with a number on top as to which option it is
    for i in range(cameraCount):
        camera = cv.VideoCapture(i)
        camera.set(3, 1280)
        camera.set(4, 720)
        time.sleep(1)
        while True:
            ret, frame = camera.read()
            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(frame, "Camera Number: "+str(i) + " Press Q to exit",(50, 50), font, 1, (0, 255, 255), 2, cv.LINE_4)
            cv.imshow(f'Camera {i}', frame)
            if cv.waitKey(1) == ord("q"):
                break
        camera.release()
        cv.destroyAllWindows()

#Function to determine the outline of the object
#Arguments: Path to image
#Returns: Array of points that make up the outline of the object
def findObjectOutline(imagePath):
    img = cv.imread(imagePath)
    img = cv.resize(img, (1280, 720))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #ret, thresh = cv.threshold(gray, 127, 255, 0)
    ret, thresh = cv.threshold(gray, 55, 120, cv.THRESH_BINARY_INV)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(img, contours, -1, (0, 255, 0), 3)
    cv.imshow('img', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return contours[0]

#A function that sends an image to a OCR API via a post request and returns the text
def readText(imagePath):
    API_IP = "http://127.0.0.1:5000/ocr"
    Request = requests.post(API_IP, files={'file': open(imagePath, 'rb')})
    Request.close()
    finalElements = []
    for element in Request.text.split("),"):
        finalElements.append(element.split("'")[1])
    return finalElements

#A function that accepts an image path, finds the edges of the object, and returns the areas of the object that fall outside a specific color range
def checkForScreenBurnIn(imagePath):
    img = cv.imread(imagePath)
    #Find the object outline
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(img, contours, -1, (0, 255, 0), 3)
    #Find the edges of the object
    edges = cv.Canny(img, 100, 200)
    #Show the edges
    cv.imshow('edges', edges)
    cv.waitKey(0)
    cv.destroyAllWindows()


def testImages(imagePath): #For the SubKey test, cnc argument is to get the image directory
    imagePath = "IMAGES/"+imagePath
    testResult = "FAIL" #Default to FAIL, but if all the images are good, set to PASS
    individualTestResults = [] #Dictionary to hold the results of each image
    print("Image File: " + imagePath)
    if "VolumeUp" in imagePath:
        exptectedColor = "White"
    elif "VolumeDown" in imagePath:
        exptectedColor = "Green"
    elif "Power" in imagePath:
        exptectedColor = "Red"
    elif "Back" in imagePath:
        exptectedColor = "Magenta"
    elif "Home" in imagePath:
        exptectedColor = "Blue"
    elif "Menu" in imagePath:
        exptectedColor = "Orange"
    print("Expected Color: " + exptectedColor)
    img = cv.imread(imagePath)
    img = cv.resize(img, (1, 1))
    color = img[0, 0]
    color = str(color)
    print("Color: " + color)
    color = color.replace("[", "")
    color = color.replace("]", "")
    #If color length is less than 11, then each color is only one digit
    if len(color) < 11:
        color = color.split(" ")
        print("Color: " + str(color))
        try:
            blueValue = int(color[0])
            greenValue = int(color[1])
            redValue = int(color[2])
        except:
            print("Hit Color Exception. Trying other options...")
            try:
                blueValue = int(color[0])
                greenValue = int(color[2])
                redValue = int(color[3])
            except:
                print("Coulnt figure it out...")
    else:
        blueValue = int(color[0]+color[1]+color[2])
        greenValue = int(color[4]+color[5]+color[6])
        redValue = int(color[8]+color[9]+color[10])
    print(f'Red: {redValue} Green: {greenValue} Blue: {blueValue}')  
    if exptectedColor == "White":
        if redValue > 200 and greenValue > 175 and blueValue > 200:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL")
    
    elif exptectedColor == "Green":
        if redValue < 100 and greenValue > 100 and blueValue < 150:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL")
    
    elif exptectedColor == "Red":
        if redValue > 200 and greenValue < 150 and blueValue < 150:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL")
    
    elif exptectedColor == "Magenta":
        if redValue > 100 and greenValue < 100 and blueValue > 100:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL") 
    
    elif exptectedColor == "Blue":
        if redValue < 100 and greenValue < 100 and blueValue > 100:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL")
    
    elif exptectedColor == "Orange":
        if redValue > 100 and greenValue > 100 and blueValue < 100:
            testResult = "PASS"
            individualTestResults.append(testResult)
        else:
            individualTestResults.append("FAIL")
    print("Test Result: " + testResult)
    return testResult

def analyzeTouchTest(imagePath):
    #Load an image using the image path (append IMAGES/) and get a percent of R G B values
    #The format of the colors are in B G R
    imagePath = "IMAGES/"+imagePath
    #Resize the image to be half the original size
    img = cv.imread(imagePath)
    img = cv.resize(img, (0, 0), fx=0.5, fy=0.5)
    greenPercent = 0
    totalPixels = 0
    for row in img:
        for pixel in row:
            totalPixels += 1
            #If the pixel is mostly green, add to the green percent
            if pixel[1] > pixel[0] and pixel[1] > pixel[2]:
                greenPercent += 1
    greenPercent = greenPercent/totalPixels
    print(f'Green: {greenPercent*100}')
    #If the green percent is greater than 15%, then the test passed
    if greenPercent*100 > 15:
        return "PASS"
    else:
        return "FAIL"

def analyzeTouchTest_old_DOESNT_WORK(imagePath):
    imagePath = "IMAGES/"+imagePath
    testResult = "FAIL" #Default to FAIL, but if the touch screen is working properly, set to PASS
    img = cv.imread(imagePath)
    #Resize the image to 1/2 the original size
    img = cv.resize(img, (0, 0), fx=0.5, fy=0.5)
    rows, cols, _ = img.shape
    greenPixels = 0
    totalPixels = 0
    for i in range(rows):
        for j in range(cols):
            if img[i, j][1] > 150:
                greenPixels += 1
            totalPixels += 1
    percentGreen = greenPixels/totalPixels
    #Convert to a percentage with no decimal places and make it an int
    percentGreen = int(percentGreen*100)
    print(f'Total Pixels: {totalPixels} Green Pixels: {greenPixels} Percent Green: {percentGreen}')
    if percentGreen > 50:
        testResult = "PASS"
    return testResult



if __name__ == "__main__":
    testImages("35655677285000971/SubKey_VolumeUp35655677285000971.jpg")
