import RPi.GPIO as GPIO
from time import sleep

class ServoControl:
    # Angles
    dutyLeft = 2 + 90/18
    dutyMiddle = 2 + 45/18
    dutyRight = 2 + 0

    # Servo setup
    def __init__(self, servoPin=16, pwmFreq=50):
        self.servoPin = servoPin
        # Pin numbering scheme setup
        GPIO.setmode(GPIO.BOARD)
        # Pin mode setup
        GPIO.setup(self.servoPin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servoPin, pwmFreq)
        self.pwm.start(0)
        self.rotateMiddle()

    def rotateLeft(self):
        self.pwm.ChangeDutyCycle(self.dutyLeft)
        sleep(0.5)
        self.pwm.ChangeDutyCycle(0)

    def rotateMiddle(self):
        self.pwm.ChangeDutyCycle(self.dutyMiddle)
        sleep(0.5)
        self.pwm.ChangeDutyCycle(0)
    
    def rotateRight(self):
        self.pwm.ChangeDutyCycle(self.dutyRight)
        sleep(0.5)
        self.pwm.ChangeDutyCycle(0)

    def delete(self):
        self.rotateMiddle()
        self.pwm.stop()
        GPIO.cleanup()