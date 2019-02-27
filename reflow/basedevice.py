import gc
from machine import Pin, PWM


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
        gc.collect()

    def duty(self, duty = None):
        try:
            return self.pwm.duty(duty)
        except:
            return 0.0


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
