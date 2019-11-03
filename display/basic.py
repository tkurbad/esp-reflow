# Basic Display Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from config import DISPLAY_BAUDRATE, DISPLAY_BUSID, DISPLAY_CS_PIN, DISPLAY_DC_PIN
from config import DISPLAY_WIDTH
from config import DISPLAY_DELIM_COLOR, DISPLAY_ERROR_FG_COLOR
from config import DISPLAY_LABEL_FONT, DISPLAY_LABEL_X
from config import DISPLAY_LABEL_FG_COLOR, DISPLAY_LABEL_BG_COLOR
from config import DISPLAY_TOP_BAR_HEIGHT, DISPLAY_TOP_BAR_Y
from config import DISPLAY_TOP_BAR_FG_COLOR, DISPLAY_TOP_BAR_BG_COLOR
from config import DISPLAY_TOP_BAR_HEIGHT, DISPLAY_TOP_BAR_FONT
from config import DISPLAY_TOP_BAR_TEXT_X, DISPLAY_TOP_BAR_TEXT_Y
from config import DISPLAY_PROFILE_FG_COLOR, DISPLAY_PROFILE_BG_COLOR
from config import DISPLAY_PROFILE_HEATING_FG_COLOR, DISPLAY_PROFILE_SOAKING_FG_COLOR
from config import DISPLAY_PROFILE_LABEL, DISPLAY_PROFILE_LABEL_Y
from config import DISPLAY_PROFILE_FONT, DISPLAY_PROFILE_DELIM_Y
from config import DISPLAY_PROFILE_NAME_X, DISPLAY_PROFILE_NAME_Y
from config import DISPLAY_PROFILE_SETPOINT_X, DISPLAY_PROFILE_SETPOINT_Y
from config import DISPLAY_HEATER_FG_COLOR, DISPLAY_HEATER_BG_COLOR
from config import DISPLAY_HEATER_LABEL, DISPLAY_HEATER_LABEL_Y
from config import DISPLAY_HEATER_TEXT_X, DISPLAY_HEATER_TEXT_Y
from config import DISPLAY_HEATER_DELIM_Y
from config import DISPLAY_LOW_BAR_FONT, DISPLAY_LOW_BAR_DELIM_Y
from config import DISPLAY_LOW_BAR_TEXT_X, DISPLAY_LOW_BAR_TEXT_Y
from config import DISPLAY_LOW_BAR_LABEL1, DISPLAY_LOW_BAR_LABEL2
from config import DISPLAY_LOW_BAR_LABEL_Y
from config import DISPLAY_THERMOCOUPLE_FG_COLOR, DISPLAY_THERMOCOUPLE_BG_COLOR
from config import DISPLAY_FAN_ICON_X, DISPLAY_LIGHT_ICON_X, DISPLAY_SD_ICON_X
from config import HEATER_LABEL, HEATER_NAME_BOTTOM, HEATER_NAME_TOP, NUM_HEATERS
from config import THERMOCOUPLE_NAME1, THERMOCOUPLE_NAME2, THERMOCOUPLE_NAME3, THERMOCOUPLE_NAME4
from config import THERMOCOUPLE_LABEL, NUM_THERMOCOUPLES

from ili9341 import ILI9341
from display.icon import AnimatedFanIcon, FanIcon, LightbulbIcon, SDIcon
from display.icon import DegreeSymbol

from reflow.reflow import HeatControl

# Initialize globals
HEATER_X                = dict()
TC_X                    = dict()


class Display(ILI9341):
    """ Basic Reflow Oven Display Class. """

    def __init__(self):
        """ Initialize Display with Pre-Configured Parameters. """
        super().__init__(busid = DISPLAY_BUSID,
                         cs = DISPLAY_CS_PIN,
                         dc = DISPLAY_DC_PIN,
                         baudrate = DISPLAY_BAUDRATE)
        self.prepared = False
        self.fanicon = FanIcon()
        self.fanicon_anim = AnimatedFanIcon()
        self.lighticon = LightbulbIcon()
        self.sdcardicon = SDIcon()
        self._fan_inactive = False
        self._last_fan_duty = -1.0
        self._last_heater_duty = dict()
        self._last_light = None
        self._last_mounted = None
        self._last_temperatures = dict()
        self._last_internal_temperature = 0.0
        self._last_ipaddress = None
        self._last_profile_name = None
        self._last_soaking_elapsed = - 1
        self._was_reflowing = False

    def prepare(self):
        """ Erase Display, Set Up Status Bars, etc. """
        # Erase
        self.erase()
        # Prepare Top and Bottom Status Bars
        self.set_color(DISPLAY_TOP_BAR_FG_COLOR,
                       DISPLAY_TOP_BAR_BG_COLOR)
        self.fill_rectangle(0,
                            DISPLAY_TOP_BAR_Y,
                            DISPLAY_WIDTH,
                            DISPLAY_TOP_BAR_HEIGHT,
                            color = DISPLAY_TOP_BAR_BG_COLOR)
        self.fill_rectangle(0,
                            DISPLAY_PROFILE_DELIM_Y,
                            DISPLAY_WIDTH,
                            1,
                            color = DISPLAY_DELIM_COLOR)
        self.fill_rectangle(0,
                            DISPLAY_HEATER_DELIM_Y,
                            DISPLAY_WIDTH,
                            1,
                            color = DISPLAY_DELIM_COLOR)
        self.fill_rectangle(0,
                            DISPLAY_LOW_BAR_DELIM_Y,
                            DISPLAY_WIDTH,
                            1,
                            color = DISPLAY_DELIM_COLOR)
        # Top Status Bar
        self.set_font(DISPLAY_TOP_BAR_FONT)
        self.ipaddress_x = self.chars('IP ',
                                      DISPLAY_TOP_BAR_TEXT_X,
                                      DISPLAY_TOP_BAR_TEXT_Y)
        # Reflow Profile Status Bar Label
        self.set_font(DISPLAY_LABEL_FONT)
        self.set_color(DISPLAY_LABEL_FG_COLOR,
                       DISPLAY_LABEL_BG_COLOR)
        self.chars(DISPLAY_PROFILE_LABEL,
                   DISPLAY_LABEL_X,
                   DISPLAY_PROFILE_LABEL_Y)
        # Heater Status Bar Label
        self.chars(DISPLAY_HEATER_LABEL,
                   DISPLAY_LABEL_X,
                   DISPLAY_HEATER_LABEL_Y)
        # Thermocouple Status Bar Label
        low_bar_label_x = self.chars(DISPLAY_LOW_BAR_LABEL1,
                                     DISPLAY_LABEL_X,
                                     DISPLAY_LOW_BAR_LABEL_Y)
        degree_symbol = DegreeSymbol()
        self.bitmap(degree_symbol.data,
                    low_bar_label_x,
                    DISPLAY_LOW_BAR_LABEL_Y,
                    degree_symbol.width,
                    degree_symbol.height)
        self.chars(DISPLAY_LOW_BAR_LABEL2,
                   low_bar_label_x + degree_symbol.width,
                   DISPLAY_LOW_BAR_LABEL_Y)
        # Thermocouple Names
        self.set_color(DISPLAY_THERMOCOUPLE_FG_COLOR,
                       DISPLAY_THERMOCOUPLE_BG_COLOR)
        self.set_font(DISPLAY_LOW_BAR_FONT)
        for tc_name in [THERMOCOUPLE_NAME1,
                        THERMOCOUPLE_NAME2,
                        THERMOCOUPLE_NAME3,
                        THERMOCOUPLE_NAME4]:
            TC_X[tc_name] = self.chars(
                                THERMOCOUPLE_LABEL[tc_name],
                                DISPLAY_LOW_BAR_TEXT_X[tc_name],
                                DISPLAY_LOW_BAR_TEXT_Y[tc_name]
                                )
        TC_X[THERMOCOUPLE_NAME1] = max(
                                    TC_X[THERMOCOUPLE_NAME1],
                                    TC_X[THERMOCOUPLE_NAME3]
                                    )
        TC_X[THERMOCOUPLE_NAME3] = TC_X[THERMOCOUPLE_NAME1]
        TC_X[THERMOCOUPLE_NAME2] = max(
                                    TC_X[THERMOCOUPLE_NAME2],
                                    TC_X[THERMOCOUPLE_NAME4]
                                    )
        TC_X[THERMOCOUPLE_NAME4] = TC_X[THERMOCOUPLE_NAME2]
        # Heater Names
        self.set_color(DISPLAY_HEATER_FG_COLOR,
                       DISPLAY_HEATER_BG_COLOR)
        for heater_name in [HEATER_NAME_TOP,
                            HEATER_NAME_BOTTOM]:
            HEATER_X[heater_name] = self.chars(
                                        HEATER_LABEL[heater_name],
                                        DISPLAY_HEATER_TEXT_X[heater_name],
                                        DISPLAY_HEATER_TEXT_Y)
        self.prepared = True

    def show_fan(self, fan_duty):
        if not self.prepared:
            return
        if self._fan_inactive and (fan_duty == self._last_fan_duty == 0):
            return

        self.set_color(DISPLAY_TOP_BAR_FG_COLOR,
                       DISPLAY_TOP_BAR_BG_COLOR)
        self.set_font(DISPLAY_TOP_BAR_FONT)
        fan_x = self.bitmap(self.fanicon.data if fan_duty == 0 else self.fanicon_anim.data,
                            DISPLAY_FAN_ICON_X,
                            DISPLAY_TOP_BAR_TEXT_Y,
                            self.fanicon.width,
                            self.fanicon.height)
        if self._last_fan_duty != fan_duty:
            self.chars(' %3d %% ' % round(fan_duty),
                       fan_x,
                       DISPLAY_TOP_BAR_TEXT_Y)
            self._last_fan_duty = fan_duty
            self._fan_inactive = (fan_duty == 0)

    def show_heaters(self, heater_duty):
        """ Display Currently Set Heater Duty Cycle Values in Heater
            Status Bar.
        """
        if not self.prepared:
            return
        if len(heater_duty) != NUM_HEATERS:
            return
        if self._last_heater_duty == heater_duty:
            return

        self.set_color(DISPLAY_HEATER_FG_COLOR,
                       DISPLAY_HEATER_BG_COLOR)
        self.set_font(DISPLAY_LOW_BAR_FONT)
        for (name, duty) in heater_duty.items():
            if name not in self._last_heater_duty.keys():
                self._last_heater_duty[name] = duty
                self.chars('%5.1f ' % duty, HEATER_X[name],
                           DISPLAY_HEATER_TEXT_Y)
                continue
            if self._last_heater_duty[name] != duty:
                self.chars('%5.1f ' % duty, HEATER_X[name],
                           DISPLAY_HEATER_TEXT_Y)

        self._last_heater_duty = heater_duty.copy()

    def show_ipaddress(self, ipaddress):
        """ Display Current IP Address in Top Status Bar. """
        if not self.prepared:
            return
        if ipaddress == self._last_ipaddress:
            return
        self.set_color(DISPLAY_TOP_BAR_FG_COLOR,
                       DISPLAY_TOP_BAR_BG_COLOR)
        self.set_font(DISPLAY_TOP_BAR_FONT)
        self.chars('%s   ' % ipaddress,
                   self.ipaddress_x,
                   DISPLAY_TOP_BAR_TEXT_Y)
        self.last_ipaddress = ipaddress

    def show_light(self, light):
        if light is None:
            return
        if not self.prepared:
            return
        if self._last_light == light:
            return

        self._last_light = light
        if light:
            self.set_color(DISPLAY_TOP_BAR_FG_COLOR,
                           DISPLAY_TOP_BAR_BG_COLOR)
            self.bitmap(self.lighticon.data,
                        DISPLAY_LIGHT_ICON_X,
                        DISPLAY_TOP_BAR_TEXT_Y,
                        self.lighticon.width,
                        self.lighticon.height)
            return
        self.fill_rectangle(DISPLAY_LIGHT_ICON_X,
                            0,
                            self.lighticon.width,
                            DISPLAY_TOP_BAR_HEIGHT,
                            color = DISPLAY_TOP_BAR_BG_COLOR)

    def show_sdcard(self, mounted):
        if mounted is None:
            return
        if not self.prepared:
            return
        if self._last_mounted == mounted:
            return

        self._last_mounted = mounted
        if mounted:
            self.set_color(DISPLAY_TOP_BAR_FG_COLOR,
                           DISPLAY_TOP_BAR_BG_COLOR)
            self.bitmap(self.sdcardicon.data,
                        DISPLAY_SD_ICON_X,
                        DISPLAY_TOP_BAR_TEXT_Y,
                        self.sdcardicon.width,
                        self.sdcardicon.height)
            return
        self.fill_rectangle(DISPLAY_SD_ICON_X,
                            0,
                            self.sdcardicon.width,
                            DISPLAY_TOP_BAR_HEIGHT,
                            color = DISPLAY_TOP_BAR_BG_COLOR)

    def show_temperatures(self, temperatures):
        """ Display Current Thermocouple Temperature Readings in Bottom
            Status Bar.
        """
        if not self.prepared:
            return
        if len(temperatures) != NUM_THERMOCOUPLES:
            return
        if self._last_temperatures == temperatures:
            return

        self.set_color(DISPLAY_THERMOCOUPLE_FG_COLOR,
                       DISPLAY_THERMOCOUPLE_BG_COLOR)
        self.set_font(DISPLAY_LOW_BAR_FONT)
        internal_temps = []
        for (name, (external, internal)) in temperatures.items():
            internal_temps.append(internal)
            if name not in self._last_temperatures.keys():
                self._last_temperatures[name] = (external, internal)
                self.chars('%5.1f ' % external, TC_X[name],
                           DISPLAY_LOW_BAR_TEXT_Y[name])
                continue
            if self._last_temperatures[name][0] != external:
                self.chars('%5.1f ' % external, TC_X[name],
                           DISPLAY_LOW_BAR_TEXT_Y[name])

        if self._last_internal_temperature != max(internal_temps):
            self._last_internal_temperature = max(internal_temps)
            self.chars('%5.1f ' % self._last_internal_temperature,
                       TC_X[THERMOCOUPLE_NAME4],
                       DISPLAY_LOW_BAR_TEXT_Y[THERMOCOUPLE_NAME4])

        self._last_temperatures = temperatures.copy()

    def show_error(self, message):
        """ Display an (Error) Message in the Second Line of the Profile
            Status.
        """
        if message is None:
            return
        self.set_color(DISPLAY_ERROR_FG_COLOR,
                       DISPLAY_PROFILE_BG_COLOR)
        self.fill_rectangle(0,
                            DISPLAY_PROFILE_SETPOINT_Y,
                            DISPLAY_WIDTH,
                            DISPLAY_LOW_BAR_FONT.height(),
                            color = DISPLAY_PROFILE_BG_COLOR
                            )
        self.chars('{:^25}'.format(message),
                   DISPLAY_PROFILE_SETPOINT_X,
                   DISPLAY_PROFILE_SETPOINT_Y)

    def show_profile(self, reflow_profile):
        """ Display Current Profile Name, Parameters and Progress. """
        if not self.prepared:
            return
        if reflow_profile is None:
            profile_name = '- - -'
        else:
            profile_name = reflow_profile.name

        self.set_color(DISPLAY_PROFILE_FG_COLOR,
                       DISPLAY_PROFILE_BG_COLOR)
        self.set_font(DISPLAY_LOW_BAR_FONT)

        if self._last_profile_name != profile_name:
            self._last_profile_name = profile_name
            self.chars('{:^25}'.format(profile_name),
                       DISPLAY_PROFILE_NAME_X,
                       DISPLAY_PROFILE_NAME_Y)

        if HeatControl.isReflowing():
            if not self._was_reflowing:
                self.fill_rectangle(0,
                    DISPLAY_PROFILE_SETPOINT_Y,
                    DISPLAY_WIDTH,
                    DISPLAY_LOW_BAR_FONT.height(),
                    color = DISPLAY_PROFILE_BG_COLOR
                    )
            self._was_reflowing = True
            soaking = HeatControl.soaking_started > 0
            setpoint_changed = HeatControl.last_setpoint != HeatControl.current_setpoint

            soaktime = ' /{:3d}s'.format(HeatControl.current_soaktime)
            soaktime_x = (DISPLAY_WIDTH
                          - DISPLAY_PROFILE_SETPOINT_X
                          - DISPLAY_LOW_BAR_FONT.get_width(soaktime))

            self.set_color(DISPLAY_PROFILE_HEATING_FG_COLOR,
                           DISPLAY_PROFILE_BG_COLOR)

            if soaking:
                self.set_color(DISPLAY_PROFILE_SOAKING_FG_COLOR,
                               DISPLAY_PROFILE_BG_COLOR)

            if (soaking or setpoint_changed):
                if setpoint_changed:
                    self._last_soaking_elapsed = - 1

                self.chars("{:4d}'C".format(HeatControl.current_setpoint),
                                            DISPLAY_PROFILE_SETPOINT_X,
                                            DISPLAY_PROFILE_SETPOINT_Y)

                self.chars(soaktime, soaktime_x, DISPLAY_PROFILE_SETPOINT_Y)

            if self._last_soaking_elapsed != HeatControl.soaking_elapsed:
                self._last_soaking_elapsed = HeatControl.soaking_elapsed
                elapsed = '{:4d}'.format(self._last_soaking_elapsed // 1000)
                elapsed_x = soaktime_x - DISPLAY_LOW_BAR_FONT.get_width(elapsed)
                self.chars(elapsed, elapsed_x, DISPLAY_PROFILE_SETPOINT_Y)

        elif self._was_reflowing:
            self._was_reflowing = False
            self.show_error('Open Door!')
