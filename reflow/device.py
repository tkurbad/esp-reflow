from time import sleep

import config

from reflow.basedevice import PWMDevice, Rotary, SwitchedDevice


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

    def jingle(self):
        """ Play sequence (C#3 - C#8). """
        with self as buz:
            buz.duty(config.BUZZER_VOLUME)
            for octave in range(4, 9):
                buz.freq(config.BUZZER_NOTE_CSHARP[octave])
                sleep(0.2)


class Fan(PWMDevice):
    def __init__(self):
        super().__init__(config.FAN_PIN,
                         freq = config.FAN_PWM_FREQ,
                         timer = config.FAN_PWM_TIMER,
                         duty = 0)


class RotaryEncoder(Rotary):
    def __init__(self):
        super().__init__(config.ROTARY_CLK_PIN,
                         config.ROTARY_DT_PIN,
                         config.ROTARY_PUSH_PIN,
                         config.ROTARY_MIN_VAL,
                         config.ROTARY_MAX_VAL)

class Light(SwitchedDevice):
    def __init__(self):
        super().__init__(config.LIGHT_PIN)
