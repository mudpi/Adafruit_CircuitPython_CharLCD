# Copyright (C) 2020 Eric Davisson

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

"""Low-level interface to charLCD."""

import busio
import board
import microcontroller
from micropython import const

from adafruit_character_lcd.character_lcd import _PIN_ENABLE, _RS_INSTRUCTION, _LCD_BACKLIGHT, _LCD_NOBACKLIGHT

# _PIN_ENABLE = const(0x4)
# _RS_INSTRUCTION = const(0x00)
# _LCD_BACKLIGHT = const(0x08)
# _LCD_NOBACKLIGHT = const(0x00)

class Character_LCD_Interface:
    def __init__(self, rs, en, d4, d5, d6, d7):
        """
        :param address: The I2C address of your LCD.
        """
        #  save pin numbers
        self.reset = rs
        self.enable = en
        self.dl4 = d4
        self.dl5 = d5
        self.dl6 = d6
        self.dl7 = d7

        # set all pins as outputs
        for pin in (rs, en, d4, d5, d6, d7):
            pin.direction = digitalio.Direction.OUTPUT

    @property
    def backlight(self):
        return self._backlight

    @backlight.setter
    def backlight(self, enable):
        self._backlight = enable

    # Low level commands

    def send(self, value, char_mode=False):
        """Send the specified value to the display in 4-bit nibbles."""
        
        # Sends 8b ``value`` in ``char_mode``.
        # :param value: bytes
        # :param char_mode: character/data mode selector. False (default) for
        # data only, True for character bits.
        #  one ms delay to prevent writing too quickly.
        time.sleep(0.001)
        #  set character/data bit. (charmode = False)
        self.reset.value = char_mode
        # WRITE upper 4 bits
        self.dl4.value = ((value >> 4) & 1) > 0
        self.dl5.value = ((value >> 5) & 1) > 0
        self.dl6.value = ((value >> 6) & 1) > 0
        self.dl7.value = ((value >> 7) & 1) > 0
        #  send command
        self._pulse_enable()
        # WRITE lower 4 bits
        self.dl4.value = (value & 1) > 0
        self.dl5.value = ((value >> 1) & 1) > 0
        self.dl6.value = ((value >> 2) & 1) > 0
        self.dl7.value = ((value >> 3) & 1) > 0
        self._pulse_enable()

    def _pulse_enable(self):
        # Pulses (lo->hi->lo) to send commands.
        self.enable.value = False
        # 1microsec pause
        time.sleep(0.0000001)
        self.enable.value = True
        time.sleep(0.0000001)
        self.enable.value = False
        time.sleep(0.0000001)
