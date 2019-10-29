# Basic Device Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect
from machine import Pin, PWM
from micropython import const
from time import sleep_ms


class PWMDevice:
    """ Wrapper for the machine.PWM Class with __enter__ and __exit__
        Methods to Safely Disable Critical Devices Like A/C Heaters,
        Even in Case of Python Exceptions.

        Usage Example:

            >>> import time
            >>> pwm = PWMDevice(32, freq = 500, timer = 1, duty = 0)
            >>> pwm.pwm
            PWM(pin: 32, freq=500 Hz, duty=0.00% [0], duty resolution=15 bits, channel=0, timer=1)
            >>> with pwm as p:
            >>>     p.duty(50)
            >>>     time.sleep(1)
            >>>     print(p)
            >>>     crash()
            >>>     time.sleep(10)
            PWM(pin: 32, freq=500 Hz, duty=50.00% [16384], duty resolution=15 bits, channel=0, timer=1)
            Traceback (most recent call last):
              File "<stdin>", line 6, in <module>
              File "<stdin>", line 5, in <module>
            NameError: name 'crash' isn't defined
            >>> pwm.pwm
            PWM(pin: 32, freq=500 Hz, duty=0.00% [0], duty resolution=15 bits, channel=0, timer=1)

        Thus, after Exiting the with-Body pwm.duty is Again 0. This
        Would Turn off the PWM Device if the Code Crashed.
    """

    pwm = None

    def __init__(self, pin, freq = 1, duty = 0.0, timer = 0):
        """ Initialize a New PWM Object. """
        if self.pwm is None:
            self.pwm = PWM(Pin(pin, Pin.OUT),
                           freq = freq,
                           timer = timer,
                           duty = float(duty))

    def __enter__(self):
        """ Return the PWM Object on 'with' Statement. """
        return self.pwm

    def __exit__(self, exc_type, exc_value, traceback):
        """ Reset PWM Duty Cycle to 0 After Exiting the 'with' Statement
            Body.
        """
        self.pwm.duty(0.0)
        return exc_type is None

    def deinit(self):
        """ Helper Method to Completely Remove PWM Device. The Method
            Deinitializes the PWM Device and Removes it, thus Freeing
            the PWM Channel.
            This is Critical, Since PWM Channel Assignments Survive a
            Soft Reset and therefore Have to be Properly Cleaned Up.
        """
        self.pwm.deinit()
        del(self.pwm)
        collect()

    def duty(self, duty = None):
        if duty is None:
            try:
                return self.pwm.duty()
            except:
                return 0.0
        self.pwm.duty(float(duty))


class PushButton:
    """ Class for Simple Push Buttons. """

    def __init__(self, pin):
        """ Initialize Push Button. """
        self._button_pressed = False
        self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._pin.irq(trigger = Pin.IRQ_FALLING,
                      handler = self._process_button)

    def _process_button(self, pin):
        """ Process Button Presses. """
        # Debounce
        if pin.value() == 0:
            sleep_ms(5)
            if pin.value() == 0:
                self._button_pressed = True

    def value(self):
        """ Return Current Push Button State and Reset It. """
        return self.reset_button()

    def reset_button(self):
        """ Return and Reset Push Button State. """
        tempstate = self._button_pressed
        self._button_pressed = False
        return tempstate


class Rotary:
    """ Rotary Encoder Class.

        Courtesy Mike Teachman:
        https://github.com/MikeTeachman/micropython-rotary
    """
    DIR_CW          = const(0x10)     # Clockwise step
    DIR_CCW         = const(0x20)     # Counter-Clockwise step

    # Rotary Encoder States
    _R_START        = const(0x0)
    _R_CW_1         = const(0x1)
    _R_CW_2         = const(0x2)
    _R_CW_3         = const(0x3)
    _R_CCW_1        = const(0x4)
    _R_CCW_2        = const(0x5)
    _R_CCW_3        = const(0x6)
    _R_ILLEGAL      = const(0x7)

    _transition_table = [
      #|------------- NEXT STATE -------------|            |CURRENT STATE|
      # CLK/DT    CLK/DT     CLK/DT    CLK/DT
      #   00        01         10        11
      [_R_START, _R_CCW_1,  _R_CW_1,  _R_START],            # _R_START
      [_R_CW_2,  _R_START,  _R_CW_1,  _R_START],            # _R_CW_1
      [_R_CW_2,  _R_CW_3,   _R_CW_1,  _R_START],            # _R_CW_2
      [_R_CW_2,  _R_CW_3,   _R_START, _R_START | DIR_CW],   # _R_CW_3
      [_R_CCW_2, _R_CCW_1,  _R_START, _R_START],            # _R_CCW_1
      [_R_CCW_2, _R_CCW_1,  _R_CCW_3, _R_START],            # _R_CCW_2
      [_R_CCW_2, _R_START,  _R_CCW_3, _R_START | DIR_CCW],  # _R_CCW_3
      [_R_START, _R_START,  _R_START, _R_START]]            # _R_ILLEGAL

    STATE_MASK      = const(0x7)
    DIR_MASK        = const(0x30)

    RANGE_UNBOUNDED = const(1)
    RANGE_WRAP      = const(2)
    RANGE_BOUNDED   = const(3)

    def __init__(self, pin_clk, pin_dt, pin_push, min_val, max_val,
                 range_mode = None):
        """ Initialize Rotary Encoder. """
        if range_mode is None:
            range_mode = Rotary.RANGE_UNBOUNDED
        self._pin_clk = Pin(pin_clk, Pin.IN, Pin.PULL_UP)
        self._pin_dt = Pin(pin_dt, Pin.IN, Pin.PULL_UP)
        self._pin_push = Pin(pin_push, Pin.IN, Pin.PULL_UP)
        self._min_val = min_val
        self._max_val = max_val
        self._range_mode = range_mode
        self._value = min_val
        self._button_pressed = False
        self._state = _R_START
        self._pin_clk.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
                          handler = self._process_rotary_pins)
        self._pin_dt.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
                         handler = self._process_rotary_pins)
        self._pin_push.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
                           handler = self._process_push_button)

    def _wrap(self, value, incr):
        """ Wrap Around. """
        val_range = self._max_val - self._min_val + 1
        value = value + incr

        if value < self._min_val:
            value += val_range * ((self._min_val - value) // val_range + 1)

        return self._min_val + (value - self._min_val) % val_range

    def _bound(self, value, incr):
        """ Enforce Boundaries. """
        return min(self._max_val, max(self._min_val, value + incr))

    def value(self):
        """ Return Current Value and Push Button State.
            Reset Push Button State in the Process.
        """
        button_state = self.reset_button()
        return (self._value, button_state)

    def reset(self):
        """ Reset Rotary Steps to 0. """
        self._value = 0

    def reset_button(self):
        """ Return and Reset Push Button State. """
        tempstate = self._button_pressed
        self._button_pressed = False
        return tempstate

    def close(self):
        """ Close Rotary Device, i.e. Disable IRQ Handlers. """
        self._pin_clk.irq(handler = None)
        self._pin_dt.irq(handler = None)
        self._pin_push.irq(handler = None)

    @micropython.native
    def _process_rotary_pins(self, pin):
        """ Process the Rotary Input and Calculate Encoder Value. """
        clk_dt_pins = (self._pin_clk.value() << 1) | self._pin_dt.value()
        # Determine next state
        self._state = Rotary._transition_table[self._state & Rotary.STATE_MASK][clk_dt_pins]
        direction = self._state & Rotary.DIR_MASK

        incr = 0
        if direction == Rotary.DIR_CW:
            incr = 1
        elif direction == Rotary.DIR_CCW:
            incr = -1

        if self._range_mode == Rotary.RANGE_WRAP:
            self._value = self._wrap(self._value, incr)
        elif self._range_mode == Rotary.RANGE_BOUNDED:
            self._value = self._bound(self._value, incr)
        else:
            self._value = self._value + incr

    def _process_push_button(self, pin):
        """ Process Rotary Encoder Push Button Presses. """
        # Debounce
        if pin.value() == 0:
            sleep_ms(5)
            if pin.value() == 0:
                self._button_pressed = True


class SwitchedDevice:
    """ Wrapper for the machine.Pin Class with __enter__ and __exit__
        Methods to Safely Disable Critical Devices Like A/C Heaters,
        Even in Case of Python Exceptions.

        This is for Output Pins that Are Switched On if in Logical High
        State.
    """

    def __init__(self, pin):
        """ Initialize Pin Object as Output, Activate Internal Pulldown
            Resistor.
        """
        self.pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)

    def __enter__(self):
        """ Return the Pin Object on 'with' Statement. """
        return self.pin

    def __exit__(self, exc_type, exc_value, traceback):
        """ Turn the Pin Off After Exiting the 'with' Statement Body.
        """
        self.pin.off()
        return exc_type is None
