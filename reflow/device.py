from machine import Pin, PWM


class PWMDevice:
    _freq = None
    _freq_pin_devices = []

    def __init__(self, pin, freq = 0, duty = 0, freq_pin = True):
        if ((PWMDevice._freq is not None) and (freq != PWMDevice._freq)
            and (len(PWMDevice._freq_pin_devices) > 0)):
            raise RuntimeError('PWM device is pinned to frequency %d'
                               % PWMDevice._freq)
        self.duty = duty
        self.freq_pin = freq_pin
        self.pwm = PWM(Pin(pin, Pin.OUT), freq = PWMDevice.freq, duty = self.duty)
        if self.freq_pin:
            PWMDevice._freq_pin_devices.append(self.pwm)
            PWMDevice._freq = freq

    def __enter__(self):
        return self.pwm

    def __exit__(self, exc_type, exc_value, traceback):
        self.duty(0)
        if self.pwm in PWMDevice._freq_pin_devices:
            PWMDevice._freq_pin_devices.remove(self.pwm)
        if len(PWMDevice._freq_pin_devices) == 0:
            PWMDevice._freq = None
        self.deinit()
        return exc_type is None

    def deinit(self):
        self.pwm.deinit()

    def freq(self, freq, change_pinned = False):
        # TODO: Add checks
        #PWMDevice._freq = freq
        self.pwm.freq(freq)

    def duty(self, duty):
        self.pwm.duty = duty


class SwitchedDevice:
    def __init__(self, pin, inverse = False):
        self.inverse = inverse
        if self.inverse:
            self.pin = Pin(pin, Pin.OUT, Pin.PULL_UP)
        else:
            self.pin = Pin(pin, Pin.OUT, Pin.PULL_DOWN)

    def __enter__(self):
        return self.pin

    def __exit__(self, exc_type, exc_value, traceback):
        self.off()
        return exc_type is None

    def on(self):
        if self.inverse:
            self.pin.off()
        else:
            self.pin.on()

    def off(self):
        if self.inverse:
            self.pin.on()
        else:
            self.pin.off()
