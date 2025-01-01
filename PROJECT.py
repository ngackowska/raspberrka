import RPi.GPIO as GPIO
from time import sleep
from gpiozero import LED

from pwm import *
from diod_control import diodes


diod = diodes()

pwm=initServo()
SetAngle(pwm,90)

servoStop(pwm)
for i in range(5):
    diod.turnWhite()
    sleep(1)
    diod.turnNull()
    sleep(1)