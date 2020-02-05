# Specialized Device Classes for ESP32 Micropython Driven
# SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect

from hwspi.hwspi import HSPI
from uos import ilistdir, mount, umount
from sdcard import SDCard
from utime import sleep_ms

from config import DOWN_PUSHBUTTON_PIN, UP_PUSHBUTTON_PIN
from config import LEFT_PUSHBUTTON_PIN, RIGHT_PUSHBUTTON_PIN
from config import BUZZER_PIN, BUZZER_NOTE_CSHARP, BUZZER_PWM_TIMER, BUZZER_VOLUME
from config import FAN_PIN, FAN_PWM_FREQ, FAN_PWM_TIMER
from config import HEATER_PWM_FREQ
from config import HEATER_BOTTOM_PIN, HEATER_BOTTOM_PWM_TIMER
from config import HEATER_TOP_PIN, HEATER_TOP_PWM_TIMER
from config import LIGHT_PIN, DEFAULT_SD_MOUNTPATH
from config import SDCARD_BAUDRATE, SDCARD_BUSID, SDCARD_CS
from config import ROTARY_CLK_PIN, ROTARY_DT_PIN, ROTARY_PUSH_PIN
from config import ROTARY_MIN_VAL, ROTARY_MAX_VAL

from reflow.basedevice import PushButton, PWMDevice, Rotary, SwitchedDevice


class ButtonDown(PushButton):
    """ Handle Lowermost of the 4 Push Buttons. """

    def __init__(self):
        """ Initialize Push Button Using Pre-Configured Values. """
        super().__init__(DOWN_PUSHBUTTON_PIN)


class ButtonLeft(PushButton):
    """ Handle Leftmost of the 4 Push Buttons. """

    def __init__(self):
        """ Initialize Push Button Using Pre-Configured Values. """
        super().__init__(LEFT_PUSHBUTTON_PIN)


class ButtonRight(PushButton):
    """ Handle Rightmost of the 4 Push Buttons. """

    def __init__(self):
        """ Initialize Push Button Using Pre-Configured Values. """
        super().__init__(RIGHT_PUSHBUTTON_PIN)


class ButtonUp(PushButton):
    """ Handle Topmost of the 4 Push Buttons. """

    def __init__(self):
        """ Initialize Push Button Using Pre-Configured Values. """
        super().__init__(UP_PUSHBUTTON_PIN)


class Buzzer(PWMDevice):
    """ Handle Buzzer. """

    def __init__(self):
        """ Initialize Buzzer Using Pre-Configured Values. """
        super().__init__(BUZZER_PIN,
                         freq = BUZZER_NOTE_CSHARP[0],
                         timer = BUZZER_PWM_TIMER,
                         duty = 0)

    def jingle(self):
        """ Play sequence (C#3 - C#8). """
        with self as buz:
            buz.duty(BUZZER_VOLUME)
            for octave in range(4, 9):
                buz.freq(BUZZER_NOTE_CSHARP[octave])
                sleep_ms(200)


class Fan(PWMDevice):
    """ Handle Fan. """

    def __init__(self):
        """ Initialize Fan Using Pre-Configured Values. """
        super().__init__(FAN_PIN,
                         freq = FAN_PWM_FREQ,
                         timer = FAN_PWM_TIMER,
                         duty = 0)


class Heater(PWMDevice):
    """ Handle a Heater. """

    def __init__(self, pin, timer):
        """ Initialize Heater on Given 'pin' Number Using Pre-Configured
            Values.
        """
        super().__init__(pin,
                         freq = HEATER_PWM_FREQ,
                         timer = timer,
                         duty = 0)


class HeaterBottom(Heater):
    """ Handle Bottom Heater. """

    def __init__(self):
        """ Initialize Bottom Heater Using Pre-Configured Pin Number.
        """
        super().__init__(HEATER_BOTTOM_PIN,
                         HEATER_BOTTOM_PWM_TIMER)


class HeaterTop(Heater):
    """ Handle Top Heater. """

    def __init__(self):
        """ Initialize Top Heater Using Pre-Configured Pin Number. """
        super().__init__(HEATER_TOP_PIN,
                         HEATER_TOP_PWM_TIMER)


class Light(SwitchedDevice):
    """ Handle Light Switch. """

    def __init__(self):
        """ Initialize Light Switch Using Pre-Configured Pin Number. """
        super().__init__(LIGHT_PIN)


class RotaryEncoder(Rotary):
    """ Handle Rotary Encoder. """

    def __init__(self):
        """ Initialize Rotary Encoder Using Pre-Configured Values. """
        super().__init__(ROTARY_CLK_PIN,
                         ROTARY_DT_PIN,
                         ROTARY_PUSH_PIN,
                         ROTARY_MIN_VAL,
                         ROTARY_MAX_VAL)

class SDCardHandler:
    """ Class to Handle Detection, Mounting, Unmounting, and Removal of
        SD Cards.
    """

    def __init__(self, busid = None, cs = None, lock = None):
        """ Initialize SDCardHandler Using Pre-Configured Values, if
            no Overrides Are Given as Parameters.
        """
        self.busid = busid
        if self.busid is None:
            self.busid = HSPI
        self.cs = cs
        if self.cs is None:
            self.cs = SDCARD_CS
        self.lock = lock
        self.sd = None
        self._mountpoint = None
        self._mounted = False

        if self.lock is not None:
            with lock as l:
                self.init_card()
        else:
            self.init_card()

    def init_card(self):
        """ Detect and Initialize SD Card. """
        try:
            self.sd = SDCard(busid = self.busid, cs = self.cs,
                             baudrate = SDCARD_BAUDRATE)
        except OSError as e:
            if 'no sd card' in e.args[0].lower():
                self.sd = None
            else:
                raise

    def mount(self, mountpoint = None, readonly = True):
        """ Mount SD Card on Given Mountpoint. """
        self._mountpoint = None
        if self.sd is None:
            return False
        else:
            if mountpoint is None:
                mountpoint = DEFAULT_SD_MOUNTPATH
            try:
                mount(self.sd, mountpoint, readonly = readonly)
                self._mounted = True
            except OSError as e:
                if e.args[0] == 5:
                    # Error #5 EIO
                    try:
                        # Card Probably Has Been Detected as SD Card
                        # Version 2, although Being Version 1.
                        sleep_ms (100)
                        if self.lock is not None:
                            with self.lock as l:
                                self.sd.init_card_v1()
                                mount(self.sd, mountpoint, readonly = readonly)
                                self._mounted = True
                        else:
                            self.sd.init_card_v1()
                            mount(self.sd, mountpoint, readonly = readonly)
                            self._mounted = True
                    except OSError:
                        # Card Could not Be Mounted
                        self._mounted = False
                else:
                    raise e
        if self._mounted:
            self._mountpoint = mountpoint
        return self._mounted

    def umount(self):
        """ Umount Mounted SD Card. """
        if self._mounted:
            try:
                umount(self._mountpoint)
                self._mounted = False
                return True
            except OSError as e:
                if e.args[0] == 22:
                    # OSError #22 EINVAL
                    # Card Was not/no Longer Mounted
                    self._mounted = False
                    return False
                raise
        return False

    def deinit(self):
        """ Umount and Deinitialize, i.e. Remove, SD Card. """
        self.umount()
        if self.sd is not None:
            self.sd._spi.deinit()
            self.sd = None
        collect()

    def is_mounted(self):
        """ Return the Mount Status of the SD Card. """
        return self._mounted

    def listFiles(self, extension = None):
        """ List Regular Files with Filename Extension 'extension'. """
        if not self._mounted:
            raise OSError('SD card not mounted.')

        if extension is None:
            extension = ''

        if self.lock is not None:
            with self.lock as l:
                files = [entry[0] for entry in ilistdir(self._mountpoint)
                         if entry[0].endswith(extension)
                         and entry[1] == 0x8000]    # only list regular files
        else:
            files = [entry[0] for entry in ilistdir(self._mountpoint)
                     if entry[0].endswith(extension)
                     and entry[1] == 0x8000]    # only list regular files
        return files

    @property
    def mountpoint(self):
        return self._mountpoint
