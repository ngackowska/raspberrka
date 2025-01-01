from picamera2 import Picamera2
import cv2 as cv

class Camera:
    def __init__(self):
        pass

    def initiate():
        picam2 = Picamera2()
        picam2.start()

    def destroy():
        cv.destroyAllWindows()
        picam2.close()


