from gpiozero import Servo
from time import sleep

# maxTurnValue = 0.5

# rotationIncrement = 0.1

# servoPin = 6

# servo = Servo(servoPin)

# With servo calibration
# myCorrection=0.0
# #myCorrection=0.45
# maxPW=(2.0+myCorrection)/1000
# minPW=(1.0-myCorrection)/1000
# servo = Servo(servoPin, min_pulse_width=minPW, max_pulse_width=maxPW)

def setup():
    servo.mid()

def turnServoLeft():
    val = servo.value
    while val != maxTurnValue:
        val = val + rotationIncrement
        if val > maxTurnValue:
            val = maxTurnValue
        servo.value = val
        sleep(0.1)
    # OR
    #servo.max()


def turnServoRight():
    val = servo.value
    while val != -maxTurnValue:
        val = val - rotationIncrement
        if val < -maxTurnValue:
            val = -maxTurnValue
        servo.value = val
        sleep(0.1)
    # OR


def main():
    print(servo.value)
    sleep(1)

    setup()
    sleep(1)

    print(servo.value)
    turnServoLeft()
    sleep(1)
    print(servo.value)

servo = Servo(6)
val = -1

while servo.value<1:
    servo.value = val
    sleep(0.1)
    val = val + 0.1






