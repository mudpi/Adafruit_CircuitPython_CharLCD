# Copyright (C) 2020 Eric Davisson
# Adapted from https://github.com/dhalbert/CircuitPython_LCD, Copyright (C) 2017 Dan Halbert
# and from https://github.com/Tim-Jackins/pcf8574/blob/master/pcf8574.py Copyright (C) 2019 Jack Timmins

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Low-level interface to PCF8574."""

import busio
import board
import microcontroller
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

from adafruit_character_lcd.character_lcd import _PIN_ENABLE, _RS_INSTRUCTION, _LCD_BACKLIGHT, _LCD_NOBACKLIGHT

# _PIN_ENABLE = const(0x4)
# _RS_INSTRUCTION = const(0x00)
# _LCD_BACKLIGHT = const(0x08)
# _LCD_NOBACKLIGHT = const(0x00)

class I2CPCF8574Interface:
    """Write to PCF8574."""
    def __init__(self, i2c, address):
        """
        CharLCD via PCF8574 I2C port expander.

        Pin mapping::

            7  | 6  | 5  | 4  | 3  | 2  | 1  | 0
            D7 | D6 | D5 | D4 | BL | EN | RW | RS

        :param address: The I2C address of your LCD.
        """
        self.i2c = i2c
        self.address = address
        self.i2c_device = I2CDevice(self.i2c, self.address)
        self.data_buffer = bytearray(1)
        self._backlight = True

    @property
    def backlight(self):
        return self._backlight

    @backlight.setter
    def backlight(self, enable):
        self._backlight = enable

    # Low level commands

    def send(self, value, char_mode=False):
        """Send the specified value to the display in 4-bit nibbles.
        The rs_mode is either ``_RS_DATA`` or ``_RS_INSTRUCTION``."""
        rs_mode = _RS_DATA if char_mode else _RS_INSTRUCTION
        self._write4bits(rs_mode | (value & 0xF0) | _LCD_BACKLIGHT if self._backlight else _LCD_NOBACKLIGHT)
        self._write4bits(rs_mode | ((value << 4) & 0xF0) | _LCD_BACKLIGHT if self._backlight else _LCD_NOBACKLIGHT)

    def _write4bits(self, value):
        """Pulse the `enable` flag to process value."""
        with self.i2c_device:
            self._i2c_write(value & ~_PIN_ENABLE)
            microcontroller.delay_us(1)
            self._i2c_write(value | _PIN_ENABLE)
            microcontroller.delay_us(1)
            self._i2c_write(value & ~_PIN_ENABLE)
        # Wait for command to complete.
        microcontroller.delay_us(100)

    def _i2c_write(self, value):
        self.data_buffer[0] = value
        self.i2c_device.write(self.data_buffer)
