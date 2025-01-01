# from gpiozero import Servo
# from gpiozero import LED

# import I2C_LCD_driver
# from time import sleep

# # The maximum value of servo rotation
# # 1.0 -> 90 degrees
# # 0.5 -> 45 degrees
# maxTurnValue = 0.5
# # How fast the rotation value gets incremented
# rotationIncrement = 0.1

# # Define which pins are used for what
# servoPin = 29
# redPin = 11
# yellowPin = 13
# bluePin = 15

# # Initialize pins
# servo = Servo(servoPin)
# ledRed = LED(redPin)
# ledYellow = LED(yellowPin)
# ledBlue = LED(bluePin)

# # With servo calibration
# myCorrection=0.0
# #myCorrection=0.45
# maxPW=(2.0+myCorrection)/1000
# minPW=(1.0-myCorrection)/1000
# servo = Servo(servoPin, min_pulse_width=minPW, max_pulse_width=maxPW)

# # Initialize LCD

# # Using I2C_LCD_driver
# lcd = I2C_LCD_driver.lcd()

# def setup():
#     servo.mid()
#     ledRed.off()
#     ledYellow.off()
#     ledBlue.off()
#     # For I2C_LCD_driver
#     lcd.lcd_clear()


# # Main code
# # If gesture detected:
# #   detectedGestureMessage(gesture)
# #   switch:
# #       gesture == 'right'
# #            turnServoRight()
# #       gesture == 'left'
# #            turnServoLeft()
# #       gesture == 'R'
# #           turnRed()
# #       gesture == 'Y'
# #           turnYellow()
# #       gesture == 'B'
# #           turnBlue()
# #       gesture == 'O'
# #           turnOrange()
# #       gesture == 'P'
# #           turnPurple()
# #       gesture == 'G'
# #           turnGreen()
# #       gesture == 'W'
# #           turnWhite()
# #       gesture == 'N'
# #           turnNull()
# # Else:
# #   noGestureDetected()


# # Using I2C_LCD_driver
# def detectedGestureMessage(gesture):
#     lcd.lcd_clear()
#     lcd.lcd_display_string('Detected:', 1)
#     lcd.lcd_display_string(f'{gesture}', 2)

# # Using I2C_LCD_driver
# def noGestureDetected():
#     lcd.lcd_clear()
#     lcd.lcd_display_string('No gesture', 1)
#     lcd.lcd_display_string('detected', 2)


# def turnServoRight():
#     val = servo.value
#     while val != maxTurnValue:
#         val = val + rotationIncrement
#         if val > maxTurnValue:
#             val = maxTurnValue
#         servo.value = val
#         sleep(0.1)
#     # OR
#     #servo.max()


# def turnServoLeft():
#     val = servo.value
#     while val != -maxTurnValue:
#         val = val - rotationIncrement
#         if val < -maxTurnValue:
#             val = -maxTurnValue
#         servo.value = val
#         sleep(0.1)
#     # OR
#     #servo.min()


# def turnRed():
#     ledRed.on()
#     ledYellow.off()
#     ledBlue.off()


# def turnYellow():
#     ledRed.off()
#     ledYellow.on()
#     ledBlue.off()


# def turnBlue():
#     ledRed.off()
#     ledYellow.off()
#     ledBlue.on()


# def turnOrange():
#     ledRed.on()
#     ledYellow.on()
#     ledBlue.off()


# def turnPurple():
#     ledRed.on()
#     ledYellow.off()
#     ledBlue.on()


# def turnGreen():
#     ledRed.off()
#     ledYellow.on()
#     ledBlue.on()


# def turnWhite():
#     ledRed.on()
#     ledYellow.on()
#     ledBlue.on()


# def turnNull():
#     ledRed.off()
#     ledYellow.off()
#     ledBlue.off()
























from time import sleep

from gpiozero import LED

redPin = 17
yellowPin = 27
bluePin = 22

ledRed = LED(redPin)
ledYellow = LED(yellowPin)
ledBlue = LED(bluePin)

def setup():
    ledRed.off()
    ledYellow.off()
    ledBlue.off()

def turnRed():
    ledRed.on()
    ledYellow.off()
    ledBlue.off()


def turnYellow():
    ledRed.off()
    ledYellow.on()
    ledBlue.off()


def turnBlue():
    ledRed.off()
    ledYellow.off()
    ledBlue.on()


def turnOrange():
    ledRed.on()
    ledYellow.on()
    ledBlue.off()


def turnPurple():
    ledRed.on()
    ledYellow.off()
    ledBlue.on()


def turnGreen():
    ledRed.off()
    ledYellow.on()
    ledBlue.on()


def turnWhite():
    ledRed.on()
    ledYellow.on()
    ledBlue.on()


def turnNull():
    ledRed.off()
    ledYellow.off()
    ledBlue.off()






led_red = LED(17)

def blink(led, how_long):
    for _ in range(how_long):
        led.on()
        sleep(1)
        led.off()
        sleep(1)

def turn_on():
    led_red.on()

# blink(led_red, 5)
# # print("przed")
# turn_on()
# # # sleep(10)
# # # print("po")
# while True:
#     pass