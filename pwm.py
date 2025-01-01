import RPi.GPIO as GPIO
from time import sleep

def initServo():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.OUT)
    pwm=GPIO.PWM(16, 50)
    pwm.start(0)
    return pwm
	
def SetAngle(pwm,angle):
	duty = angle / 18 + 2
	GPIO.output(16, True)
	pwm.ChangeDutyCycle(duty)
	sleep(1)
	GPIO.output(16, False)
	pwm.ChangeDutyCycle(0)
	
# agl = 0
# while(agl<=180):
# 	SetAngle(agl)
# 	agl+=45

def servoStop(pwm):
    pwm.stop()
    GPIO.cleanup()
