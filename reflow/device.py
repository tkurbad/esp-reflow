import config

from reflow.basedevice import PWMDevice, SwitchedDevice


class Heater(PWMDevice):
    def __init__(self, pin):
        super().__init__(pin,
                         freq = config.HEATER_PWM_FREQ,
                         timer = config.HEATER_PWM_TIMER,
                         duty = 0)


class HeaterBottom(Heater):
    def __init__(self):
        super().__init__(config.HEATER_TOP_PIN)


class HeaterTop(Heater):
    def __init__(self):
        super().__init__(config.HEATER_TOP_PIN)


class Buzzer(PWMDevice):
    def __init__(self):
        super().__init__(config.BUZZER_PIN,
                         freq = config.BUZZER_NOTE_CSHARP[0],
                         timer = config.BUZZER_PWM_TIMER,
                         duty = 0)


class Fan(PWMDevice):
    def __init__(self):
        super().__init__(config.FAN_PIN,
                         freq = config.FAN_PWM_FREQ,
                         timer = config.FAN_PWM_TIMER,
                         duty = 0)


class Light(SwitchedDevice):
    def __init__(self):
        super().__init__(config.LIGHT_PIN)
