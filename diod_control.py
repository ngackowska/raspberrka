from gpiozero import LED
from time import sleep


class Diodes:
    redPin = 17
    yellowPin = 27
    bluePin = 22

    ledRed = LED(redPin)
    ledYellow = LED(yellowPin)
    ledBlue = LED(bluePin)

    def turnOn(self, red=False, yellow=False, blue=False):
        if red: self.ledRed.on()
        else: self.ledRed.off()
        if yellow: self.ledYellow.on()
        else: self.ledYellow.off()
        if blue: self.ledBlue.on()
        else: self.ledBlue.off()


