import random
import time
import cv2 as cv
import numpy as np
import ObjectBasedGCode

#camera = cv.VideoCapture(0) #Camera 1
#camera = cv.VideoCapture(1) #Camera 2




def capturePicture(name, cncDeviceProfile):
    camera = cv.VideoCapture(int(cncDeviceProfile.camera))
    camera.set(3, 3840)
    camera.set(4, 2160)
    time.sleep(1)
    ret, frame = camera.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...\n")
        return
    #Save image to folder called IMAGES with the name of the parameter
    cv.imwrite("/IMAGES/" + cncDeviceProfile.imagePath +  name + ".jpg", frame)
    print(f'\nImage Taken: {name}\n')
    camera.release()
    cv.destroyAllWindows()
    if name == "Sensor Information":
        #Do OCR on the image
        pass


def showCameraView(cncDeviceProfile):
    camera = cv.VideoCapture(int(cncDeviceProfile.camera))
    camera.set(3, 1280)
    camera.set(4, 720)
    time.sleep(5)
    while True:
        ret, frame = camera.read()
        cv.imshow(f'Camera', frame)
        if cv.waitKey(1) == ord("q"):
            break
    camera.release()
    cv.destroyAllWindows()



def showAllConnectedCameras():
    #Ask user how many cameras are connected
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