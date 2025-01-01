import I2C_LCD_driver
from time import *

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string("Dupa", 1)
mylcd.lcd_display_string("Under The Sea", 2)