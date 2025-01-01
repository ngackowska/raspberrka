#from picamzero import Camera
from time import sleep
#from cv2 import *
import cv2 as cv
#from picamera import PiCamera
#from picamera.array import PiRGBArray

from picamera2 import Picamera2
import mediapipe as mp

#print(cv2.__version__)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)

mp_draw = mp.solutions.drawing_utils

picam2 = Picamera2()
picam2.start()


while True:
    frame = picam2.capture_array()
    
    frame = cv.flip(frame, 0)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    frame.flags.writeable = False
    results = hands.process(frame)
    frame.flags.writeable = True

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv.imshow("dupa", frame)
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


    
cv.destroyAllWindows()
picam2.close()

#cam = Camera()
#cam.flip_camera()
#cam.start_preview()

#sleep(5)

print("priviet")