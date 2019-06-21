# The MIT License (MIT)
#
# Copyright (c) 2019 Gaston Williams
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`sparkfun_qwiictwist`
================================================================================

CircuitPython library for the Sparkfun Qwiic Twist Rotary Encoder


* Author(s): Gaston Williams

Implementation Notes
--------------------

**Hardware:**

*  This is library is for the SparkFun Qwiic Joystick.
*  SparkFun sells these at its website: www.sparkfun.com
*  Do you like this library? Help support SparkFun. Buy a board!
   https://www.sparkfun.com/products/15083

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/fourstix/Sparkfun_CircuitPython_QwiicTwist.git"

# imports

from time import sleep
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

# public constants
QWIIC_TWIST_ADDR = const(0x3F) # default I2C Address
QWIIC_TWIST_ID = const(0x5c) # value returned by id register



# private constants

# bit constants
_BUTTON_CLICKED_BIT = const(2)
_BUTTON_PRESSED_BIT = const(1)
_ENCODER_MOVED_BIT = const(0)
_BUTTON_INT_ENABLE = const(1)
_ENCODER_INT_ENABLE = const(0)

# register constants
_TWIST_ID = const(0x00)
_TWIST_STATUS = const(0x01) # 2 - button clicked, 1 - button pressed, 0 - encoder moved
_TWIST_VERSION = const(0x02)
_TWIST_ENABLE_INTS = const(0x04) # 1 - button interrupt, 0 - encoder interrupt
_TWIST_COUNT = const(0x05)
_TWIST_DIFFERENCE = const(0x07)
_TWIST_LAST_ENCODER_EVENT = const(0x09) # Millis since last movement of knob
_TWIST_LAST_BUTTON_EVENT = const(0x0B) # Millis since last press/release
_TWIST_RED = const(0x0D)
_TWIST_GREEN = const(0x0E)
_TWIST_BLUE = const(0x0F)
_TWIST_CONNECT_RED = (0x10) # Amount to change red LED for each encoder tick
_TWIST_CONNECT_GREEN = (0x12)
_TWIST_CONNECT_BLUE = const(0x14)
_TWIST_TURN_INT_TIMEOUT = const(0x16)
_TWIST_CHANGE_ADDRESS = const(0x18)

# class
class Sparkfun_QwiicTwist:
    """CircuitPython class for the Sparkfun QwiicTwist RGB Rotary Encoder"""

    def __init__(self, i2c, address=QWIIC_TWIST_ADDR, debug=False):
        """Initialize Qwiic Twist for i2c communication."""
        self._device = I2CDevice(i2c, address)
        #save handle to i2c bus in case address is changed
        self._i2c = i2c
        self._debug = debug

# public properites (read-only)

    @property
    def connected(self):
        """Check the id of Rotary Encoder.  Returns True if successful."""
        if self._read_register8(_TWIST_ID) != QWIIC_TWIST_ID:
            return False
        return True

    @property
    def version(self):
        """Return the version string for the Twist firmware."""
        value = self._read_register16(_TWIST_VERSION)
        # LSB is Major and MSB is minor
        major = value & 0xFF
        minor = (value >> 8) & 0xFF

        return 'v' + str(major) + '.' + str(minor)

    @property
    def moved(self):
        """Return true if the knob has been twisted."""
        status = self._read_register8(_TWIST_STATUS)

        moved = status & (1<<_ENCODER_MOVED_BIT)

        # We've read this status bit, now clear it
        self._write_register8(_TWIST_STATUS,
                              status & ~(1<<_ENCODER_MOVED_BIT))

        return moved

    @property
    def pressed(self):
        """"Return true if button is currently pressed."""
        status = self._read_register8(_TWIST_STATUS)

        pressed = status & (1<<_BUTTON_PRESSED_BIT)

        # We've read this status bit, now clear it
        self._write_register8(_TWIST_STATUS,
                              status & ~(1<<_BUTTON_PRESSED_BIT))

        return pressed

    @property
    def clicked(self):
        """Return true if a click event has occurred. Event flag is then reset."""
        status = self._read_register8(_TWIST_STATUS)

        clicked = status & (1<<_BUTTON_CLICKED_BIT)

        # We've read this status bit, now clear it
        self._write_register8(_TWIST_STATUS,
                              status & ~(1<<_BUTTON_CLICKED_BIT))

        return clicked

# public properties (read-write)

    @property
    def count(self):
        """Returns the number of indents since the user turned the knob."""
        value = self._read_register16(_TWIST_COUNT)
        return self._signed_int16(value)


    @count.setter
    def count(self, value):
        """Set the number of indents to a given amount."""
        self._write_register16(_TWIST_COUNT, value)

    @property
    def red(self):
        """Get the value of the red LED."""
        return self._read_register8(_TWIST_RED)

    @red.setter
    def red(self, value):
        """Set the value of the red LED 0-255."""
        self._write_register8(_TWIST_RED, value)

    @property
    def green(self):
        """Get the value of the green LED."""
        return self._read_register8(_TWIST_GREEN)

    @green.setter
    def green(self, value):
        """Set the value of the green LED 0-255."""
        self._write_register8(_TWIST_GREEN, value)

    @property
    def blue(self):
        """Get the value of the blue LED"""
        return self._read_register8(_TWIST_BLUE)

    @blue.setter
    def blue(self, value):
        """Set the value of the blue LED 0-255."""
        self._write_register8(_TWIST_BLUE, value)

    @property
    def red_connection(self):
        """Get the value of the red LED connection"""
        value = self._read_register16(_TWIST_CONNECT_RED)
        return self._signed_int16(value)

    @red_connection.setter
    def red_connection(self, value):
        """Set the value of the red LED connection."""
        self._write_register16(_TWIST_CONNECT_RED, value)

    @property
    def green_connection(self):
        """Get the value of the green LED connection."""
        return self._read_register16(_TWIST_CONNECT_GREEN)

    @green_connection.setter
    def green_connection(self, value):
        """Set the value of the green LED connection"""
        value = self._write_register16(_TWIST_CONNECT_GREEN, value)
        return self._signed_int16(value)

    @property
    def blue_connection(self):
        """Get the value of the blue LED connection."""
        value = self._read_register16(_TWIST_CONNECT_BLUE)
        return self._signed_int16(value)

    @blue_connection.setter
    def blue_connection(self, value):
        """Set the value of the blue LED connection."""
        self._write_register16(_TWIST_CONNECT_BLUE, value)

    @property
    def int_timeout(self):
        """Get number of milliseconds that elapse between
        the end of the knob turning and interrupt firing."""
        return self._read_register16(_TWIST_TURN_INT_TIMEOUT)

    @int_timeout.setter
    def int_timeout(self, value):
        """Set the number of milliseconds that elapse between
        the end of knob turning and interrupt firing."""
        self._write_register16(_TWIST_TURN_INT_TIMEOUT, value)

# public functions

    def get_difference(self, clear=True):
        """"Return the number of clicks since last check."""
        value = self._read_register16(_TWIST_DIFFERENCE)
        diff = self._signed_int16(value)

        if clear:
            self._write_register16(_TWIST_DIFFERENCE, 0)
        return diff

    def time_since_last_movement(self, clear=True):
        """Return the number of milliseconds since the last encoder movement"""
        # unsigned 16-bit value
        elapsed_time = self._read_register16(_TWIST_LAST_ENCODER_EVENT)

        # Clear the current value if requested
        if clear:
            self._write_register16(_TWIST_LAST_ENCODER_EVENT, 0)
        return elapsed_time

    def time_since_last_press(self, clear=True):
        """Return the number of milliseconds since the last button press and release"""
        # unsigned 16-bit value
        elapsed_time = self._read_register16(_TWIST_LAST_BUTTON_EVENT)
        # Clear the current value if requested
        if clear:
            self._write_register16(_TWIST_LAST_BUTTON_EVENT, 0)
        return elapsed_time

    def clear_interrupts(self):
        """Clears the moved, clicked, and pressed bits"""
        self._write_register8(_TWIST_STATUS, 0)

    def set_color(self, red_value, green_value, blue_value):
        """Set the rgb color of the encoder LEDs"""
        self._write_register24(_TWIST_RED,
                               (red_value & 0xFF) << 16 |
                               (green_value & 0xFF) << 8 |
                               blue_value & 0xFF)

    def connect_color(self, red_value, green_value, blue_value):
        """Connect all the rgb color for the encoder LEDs"""
        self._write_register16(_TWIST_CONNECT_RED, red_value)
        self._write_register16(_TWIST_CONNECT_GREEN, green_value)
        self._write_register16(_TWIST_CONNECT_BLUE, blue_value)

    def change_address(self, new_address):
        """Change the i2c address of Twist Rotary Encoder snd return True if successful."""
        # check range of new address
        if (new_address < 8 or new_address > 119):
            print('ERROR: Address outside 8-119 range')
            return False
        # write new address
        self._write_register8(_TWIST_CHANGE_ADDRESS, new_address)

	# wait a second for joystick to settle after change
        sleep(1)

        # try to re-create new i2c device at new address
        try:
            self._device = I2CDevice(self._i2c, new_address)
        except ValueError as err:
            print('Address Change Failure')
            print(err)
            return False

        #if we made it here, everything went fine
        return True

# No i2c begin function is needed since I2Cdevice class takes care of that

# private functions

    def _signed_int16(self, value):
        # convert a 16-bit value into a signed integer
        result = value
        if self._debug:
            print('Unsigned 16-bit value = ' + str(result))

        if result & (1<<15):
            result -= 1<<16

        if self._debug:
            print('Signed 16-bit value = ' + str(result))
        return result

    def _read_register8(self, addr):
        # Read and return a byte from the specified 8-bit register address.
        with self._device as device:
            device.write(bytes([addr & 0xFF]))
            result = bytearray(1)
            device.readinto(result)
            if self._debug:
                print("$%02X => %s" % (addr, [hex(i) for i in result]))
            return result[0]

    def _write_register8(self, addr, value):
        # Write a byte to the specified 8-bit register address
        with self._device as device:
            device.write(bytes([addr & 0xFF, value & 0xFF]))
            if self._debug:
                print("$%02X <= 0x%02X" % (addr, value))

    def _read_register16(self, addr):
        # Read and return a 16-bit value from the specified 8-bit register address.
        with self._device as device:
            device.write(bytes([addr & 0xFF]))
            result = bytearray(2)
            device.readinto(result)
            if self._debug:
                print("$%02X => %s" % (addr, [hex(i) for i in result]))
            return (result[1] << 8) | result[0]

    def _write_register16(self, addr, value):
        # Write a 16-bit big endian value to the specified 8-bit register
        with self._device as device:
            # write LSB then MSB
            device.write(bytes([addr & 0xFF,
                                value & 0xFF,
                                (value >> 8) & 0xFF]))
            if self._debug:
                print("$%02X <= 0x%02X" % (addr, value & 0xFF))
                print("$%02X <= 0x%02X" % (addr, (value >> 8) &0xFF))

    def _write_register24(self, addr, value):
        # Write a byte to the specified 8-bit register address
        with self._device as device:
            device.write(bytes([addr & 0xFF,
                                (value >> 16) & 0xFF,
                                (value >> 8) & 0xFF,
                                value & 0xFF]))
            if self._debug:
                print("$%02X <= 0x%02X" % (addr, (value >> 16) &0xFF))
                print("$%02X <= 0x%02X" % (addr, (value >> 8) &0xFF))
                print("$%02X <= 0x%02X" % (addr, value & 0xFF))
