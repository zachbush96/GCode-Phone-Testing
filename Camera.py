import random
import time
import cv2 as cv
import numpy as np
import ObjectBasedGCode
import os

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
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...\n")
        return
    #Save image to folder called IMAGES with the name of the parameter
    cv.imwrite(os.path.join(dirname, name + '.jpg'), frame)
    if ObjectBasedGCode.TROUBLESHOOTING:
        print(f'\nImage Taken: {name}\n')
        print(f'File Path: {cncDeviceProfile.imagePath + name + ".jpg"}\n')
    camera.release()
    cv.destroyAllWindows()
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
