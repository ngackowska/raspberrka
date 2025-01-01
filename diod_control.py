from gpiozero import LED
from time import sleep


class diodes:

    redPin = 17
    yellowPin = 27
    bluePin = 22

    ledRed = LED(redPin)
    ledYellow = LED(yellowPin)
    ledBlue = LED(bluePin)

    def setup(self):
        self.ledRed.off()
        self.ledYellow.off()
        self.ledBlue.off()

    def turnRed(self):
        self.ledRed.on()
        self.ledYellow.off()
        self.ledBlue.off()


    def turnYellow(self):
        self.ledRed.off()
        self.ledYellow.on()
        self.ledBlue.off()


    def turnBlue(self):
        self.ledRed.off()
        self.ledYellow.off()
        self.ledBlue.on()


    def turnOrange(self):
        self.ledRed.on()
        self.ledYellow.on()
        self.ledBlue.off()


    def turnPurple(self):
        self.ledRed.on()
        self.ledYellow.off()
        self.ledBlue.on()


    def turnGreen(self):
        self.ledRed.off()
        self.ledYellow.on()
        self.ledBlue.on()


    def turnWhite(self):
        self.ledRed.on()
        self.ledYellow.on()
        self.ledBlue.on()


    def turnNull(self):
        self.ledRed.off()
        self.ledYellow.off()
        self.ledBlue.off()


