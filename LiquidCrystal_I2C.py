"""
Micropython ESP32 library for the 1602A LCD screen with pcf8574 I2C
interface.
Ported from the Arduino LiquidCrystal_I2C implementation

by jOrtegaFreire (BadProgrammer)
github: https://github.com/jOrtegaFreire
"""

from machine import Pin, I2C
from time import sleep_ms, sleep_us

# commands
LCD_CLEARDISPLAY            =   0x01
LCD_RETURNHOME              =   0x02
LCD_ENTRYMODESET            =   0x04
LCD_DISPLAYCONTROL          =   0x08
LCD_FUNCTIONSET             =   0x20
LCD_INIT                    =   0x30
LCD_SETDDRAMADDR            =   0x80

# flags for display entry mode
LCD_ENTRYRIGHT              =   0x00
LCD_ENTRYLEFT               =   0x02
LCD_ENTRYSHIFTINCREMENT     =   0x01
LCD_ENTRYSHIFTDECREMENT     =   0x00

# flags for display on/off control
LCD_DISPLAYON               =   0x04
LCD_DISPLAYOFF              =   0x00
LCD_CURSORON                =   0x02
LCD_CURSOROFF               =   0x00
LCD_BLINKON                 =   0x01
LCD_BLINKOFF                =   0x00

# flags for display control
LCD_8BITMODE                =   0x10
LCD_4BITMODE                =   0X00
LCD_2LINE                   =   0x08
LCD_1LINE                   =   0x00
LCD_5x10DOTS                =   0x04
LCD_5x8DOTS                 =   0x00

# flags for backlight control
LCD_BACKLIGHT               =   0x08
LCD_NOBACKLIGHT             =   0x00

# text-aling control
ALIGN_LEFT                  =   1
ALIGN_RIGHT                 =   2
ALIGN_CENTER                =   3

En                          =   0x04
Rw                          =   0x02
Rs                          =   0x01

class LiquidCrystal_I2C:

    def __init__(self,sda=21,scl=22,lcd_cols=16,lcd_rows=2):
        self.i2c=I2C(1,sda=Pin(21),scl=Pin(22))
        self.addr=0x27
        self._cols=lcd_cols
        self._rows=lcd_rows
        self._backlightval=LCD_BACKLIGHT
        self._displaycontrol=0
        self._displayfunction=0
        self._displaymode=0

    def set_addr(self,addr):
        self.addr=addr

    def begin(self):

        # SEE PAGE 45/46 FOR INITIALIZATION SPECIFICATION!
        # according to datasheet, we need at least 40ms after power rises above 2.7V
        # before sending commands. Arduino can turn on way befer 4.5V so we'll wait 50
        sleep_ms(50)

        self.expanderWrite(LCD_INIT)
        sleep_ms(5)
        self.expanderWrite(LCD_INIT)
        sleep_ms(1)
        self.expanderWrite(LCD_INIT)
        sleep_ms(1)

        # set 4bit mode
        self.write4bits(LCD_FUNCTIONSET|LCD_4BITMODE)

        # set 2lines mode
        self.command(LCD_FUNCTIONSET|LCD_2LINE)
        
        # clear screen
        self.clear()

        # return home
        self.home()
        
        # display on, cursor on
        self.command(LCD_DISPLAYCONTROL|LCD_DISPLAYON|LCD_CURSORON)

    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        sleep_ms(2)

    def home(self):
        self.command(LCD_RETURNHOME)
        sleep_ms(2)


    def set_cursor(self,row,col):
        if row==0:
            self.command(LCD_SETDDRAMADDR|col)
        elif row==1:
            self.command(LCD_SETDDRAMADDR|0x40|col)


    # Turn Display on/off
    def display(self):
        self.command(LCD_DISPLAYCONTROL|LCD_DISPLAYON)
        sleep_us(50)

    def noDisplay(self):
        self.command(LCD_DISPLAYCONTROL|LCD_DISPLAYOFF)
        sleep_us(50)

    # Turn the backlight off/on
    def noBacklight(self):
        self._backlightval=LCD_NOBACKLIGHT
        self.expanderWrite(0)
    
    def backlight(self):
        self._backlightval=LCD_BACKLIGHT
        self.expanderWrite(0)

    # mid level commands, for sending data/cmds
    def command(self,value):
        self.send(value,0)
    
    def write(self,value):
        self.send(value,Rs)
        return 1
    
    # low level data pushing commands
    def send(self,value,mode):
        highnib=value & 0xF0
        lownib=(value << 4) & 0xF0
        self.write4bits((highnib)|mode)
        self.write4bits((lownib)|mode)

    def write4bits(self,value):
        self.expanderWrite(value)
        self.pulseEnable(value)

    def expanderWrite(self,_data):
        self.i2c.writeto(self.addr,bytes([(int)(_data)|self._backlightval]))
        
    def pulseEnable(self,_data):
        self.expanderWrite(_data | En)
        sleep_us(1)

        self.expanderWrite(_data)
        sleep_us(50)

    def print(self,s):
        for c in s:
            self.write(ord(c))
