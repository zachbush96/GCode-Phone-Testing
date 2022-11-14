import random
import time
import cv2 as cv
import ObjectBasedGCode
import os
import easyocr
import requests

#camera = cv.VideoCapture(0) #Camera 1
#camera = cv.VideoCapture(1) #Camera 2

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
    camera.set(3, 3840) #Images are captured in 4K
    camera.set(4, 2160)
    ret, frame = camera.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...\n")
        return
    #Rotate the image -90 degrees
    frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
    #Save image to folder called IMAGES with the name of the parameter
    cv.imwrite(os.path.join(dirname, name + '.jpg'), frame)
    if ObjectBasedGCode.TROUBLESHOOTING:
        print(f'\nImage Taken: {name}\n')
        print(f'File Path: {cncDeviceProfile.imagePath +"/"+ name + ".jpg"}\n')
    camera.release()
    #cv.destroyAllWindows() #Is this not needed?
    if name == "Sensor Information":
        pass

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



#A function that accepts an image path and returns if the image of a phone has screen burn in
def checkForScreenBurnIn(imagePath):
    img = cv.imread(imagePath)
    img = cv.resize(img, (1280, 720))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(img, contours, -1, (0, 255, 0), 3)
    cv.imshow('img', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return contours[0]



if __name__ == "__main__":
    #print(readText("IMAGES/rotatedImages/Sensor143.jpg"))
    #print(checkForScreenBurnIn("IMAGES/path1114/GoodBlue59528.jpg"))
    pass
