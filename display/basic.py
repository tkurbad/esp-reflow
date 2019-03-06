# Basic Display Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from ili9341 import ILI9341
from display.icon import AnimatedFanIcon, FanIcon, LightbulbIcon, SDIcon

import config

class Display(ILI9341):
    """ Basic Reflow Oven Display Class. """

    def __init__(self):
        """ Initialize Display with Pre-Configured Parameters. """
        super().__init__(busid = config.DISPLAY_BUSID,
                         cs = config.DISPLAY_CS_PIN,
                         dc = config.DISPLAY_DC_PIN,
                         baudrate = config.DISPLAY_BAUDRATE)
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

    def prepare(self):
        """ Erase Display, Set Up Status Bars, etc. """
        # Erase
        self.erase()
        # Prepare Top and Bottom Status Bars
        self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                       config.DISPLAY_TOP_BAR_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_TOP_BAR_Y,
                            config.DISPLAY_WIDTH,
                            config.DISPLAY_TOP_BAR_HEIGHT,
                            color = config.DISPLAY_TOP_BAR_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_HEATER_DELIM_Y,
                            config.DISPLAY_WIDTH,
                            1,
                            color = config.DISPLAY_DELIM_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_LOW_BAR_DELIM_Y,
                            config.DISPLAY_WIDTH,
                            1,
                            color = config.DISPLAY_DELIM_COLOR)
        # Top Status Bar
        self.set_font(config.DISPLAY_TOP_BAR_FONT)
        self.ipaddress_x = self.chars('IP ',
                                      config.DISPLAY_TOP_BAR_TEXT_X,
                                      config.DISPLAY_TOP_BAR_TEXT_Y)
        # Heater Status Bar Label
        self.set_font(config.DISPLAY_LABEL_FONT)
        self.set_color(config.DISPLAY_LABEL_FG_COLOR,
                       config.DISPLAY_LABEL_BG_COLOR)
        self.chars(config.DISPLAY_HEATER_LABEL,
                   config.DISPLAY_LABEL_X,
                   config.DISPLAY_HEATER_LABEL_Y)
        # Thermocouple Status Bar Label
        self.chars(config.DISPLAY_LOW_BAR_LABEL,
                   config.DISPLAY_LABEL_X,
                   config.DISPLAY_LOW_BAR_LABEL_Y)
        # Thermocouple Names
        self.set_color(config.DISPLAY_THERMOCOUPLE_FG_COLOR,
                       config.DISPLAY_THERMOCOUPLE_BG_COLOR)
        self.set_font(config.DISPLAY_LOW_BAR_FONT)
        self.tc_x = dict()
        for tc_name in [config.THERMOCOUPLE_NAME1,
                        config.THERMOCOUPLE_NAME2,
                        config.THERMOCOUPLE_NAME3,
                        config.THERMOCOUPLE_NAME4]:
            self.tc_x[tc_name] = self.chars(
                                    config.THERMOCOUPLE_LABEL[tc_name],
                                    config.DISPLAY_LOW_BAR_TEXT_X[tc_name],
                                    config.DISPLAY_LOW_BAR_TEXT_Y[tc_name]
                                    )
        self.tc_x[config.THERMOCOUPLE_NAME1] = max(
                                                self.tc_x[config.THERMOCOUPLE_NAME1],
                                                self.tc_x[config.THERMOCOUPLE_NAME3]
                                                )
        self.tc_x[config.THERMOCOUPLE_NAME3] = self.tc_x[config.THERMOCOUPLE_NAME1]
        self.tc_x[config.THERMOCOUPLE_NAME2] = max(
                                                self.tc_x[config.THERMOCOUPLE_NAME2],
                                                self.tc_x[config.THERMOCOUPLE_NAME4]
                                                )
        self.tc_x[config.THERMOCOUPLE_NAME4] = self.tc_x[config.THERMOCOUPLE_NAME2]
        # Heater Names
        self.set_color(config.DISPLAY_HEATER_FG_COLOR,
                       config.DISPLAY_HEATER_BG_COLOR)
        self.heater_x = dict()
        for heater_name in [config.HEATER_NAME_TOP,
                            config.HEATER_NAME_BOTTOM]:
            self.heater_x[heater_name] = self.chars(
                                            config.HEATER_LABEL[heater_name],
                                            config.DISPLAY_HEATER_TEXT_X[heater_name],
                                            config.DISPLAY_HEATER_TEXT_Y)
        self.prepared = True

    def show_fan(self, fan_duty):
        if not self.prepared:
            return
        if self._fan_inactive and (fan_duty == self._last_fan_duty == 0):
            return

        self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                       config.DISPLAY_TOP_BAR_BG_COLOR)
        self.set_font(config.DISPLAY_TOP_BAR_FONT)
        fan_x = self.bitmap(self.fanicon.data if fan_duty == 0 else self.fanicon_anim.data,
                            config.DISPLAY_FAN_ICON_X,
                            config.DISPLAY_TOP_BAR_TEXT_Y,
                            self.fanicon.width,
                            self.fanicon.height)
        if self._last_fan_duty != fan_duty:
            self.chars(' %3d %% ' % round(fan_duty),
                       fan_x,
                       config.DISPLAY_TOP_BAR_TEXT_Y)
            self._last_fan_duty = fan_duty
            self._fan_inactive = (fan_duty == 0)

    def show_heaters(self, heater_duty):
        """ Display Currently Set Heater Duty Cycle Values in Heater
            Status Bar.
        """
        if not self.prepared:
            return
        if len(heater_duty) != config.NUM_HEATERS:
            return
        if self._last_heater_duty == heater_duty:
            return

        self.set_color(config.DISPLAY_HEATER_FG_COLOR,
                       config.DISPLAY_HEATER_BG_COLOR)
        self.set_font(config.DISPLAY_LOW_BAR_FONT)
        for (name, duty) in heater_duty.items():
            if name not in self._last_heater_duty.keys():
                self._last_heater_duty[name] = duty
                self.chars('%5.1f ' % duty, self.heater_x[name],
                           config.DISPLAY_HEATER_TEXT_Y)
                continue
            if self._last_heater_duty[name] != duty:
                self.chars('%5.1f ' % duty, self.heater_x[name],
                           config.DISPLAY_HEATER_TEXT_Y)

        self._last_heater_duty = heater_duty.copy()

    def show_ipaddress(self, ipaddress):
        """ Display Current IP Address in Top Status Bar. """
        if not self.prepared:
            return
        self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                       config.DISPLAY_TOP_BAR_BG_COLOR)
        self.set_font(config.DISPLAY_TOP_BAR_FONT)
        self.chars('%s   ' % ipaddress,
                   self.ipaddress_x,
                   config.DISPLAY_TOP_BAR_TEXT_Y)

    def show_light(self, light):
        if light is None:
            return
        if not self.prepared:
            return
        if self._last_light == light:
            return

        self._last_light = light
        if light:
            self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                           config.DISPLAY_TOP_BAR_BG_COLOR)
            self.bitmap(self.lighticon.data,
                        config.DISPLAY_LIGHT_ICON_X,
                        config.DISPLAY_TOP_BAR_TEXT_Y,
                        self.lighticon.width,
                        self.lighticon.height)
            return
        self.fill_rectangle(config.DISPLAY_LIGHT_ICON_X,
                            0,
                            self.lighticon.width,
                            config.DISPLAY_TOP_BAR_HEIGHT,
                            color = config.DISPLAY_TOP_BAR_BG_COLOR)

    def show_sdcard(self, mounted):
        if mounted is None:
            return
        if not self.prepared:
            return
        if self._last_mounted == mounted:
            return

        self._last_mounted = mounted
        if mounted:
            self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                           config.DISPLAY_TOP_BAR_BG_COLOR)
            self.bitmap(self.sdcardicon.data,
                        config.DISPLAY_SD_ICON_X,
                        config.DISPLAY_TOP_BAR_TEXT_Y,
                        self.sdcardicon.width,
                        self.sdcardicon.height)
            return
        self.fill_rectangle(config.DISPLAY_SD_ICON_X,
                            0,
                            self.sdcardicon.width,
                            config.DISPLAY_TOP_BAR_HEIGHT,
                            color = config.DISPLAY_TOP_BAR_BG_COLOR)

    def show_temperatures(self, temperatures):
        """ Display Current Thermocouple Temperature Readings in Bottom
            Status Bar.
        """
        if not self.prepared:
            return
        if len(temperatures) != config.NUM_THERMOCOUPLES:
            return
        if self._last_temperatures == temperatures:
            return

        self.set_color(config.DISPLAY_THERMOCOUPLE_FG_COLOR,
                       config.DISPLAY_THERMOCOUPLE_BG_COLOR)
        self.set_font(config.DISPLAY_LOW_BAR_FONT)
        internal_temps = []
        for (name, (external, internal)) in temperatures.items():
            internal_temps.append(internal)
            if name not in self._last_temperatures.keys():
                self._last_temperatures[name] = (external, internal)
                self.chars('%5.1f ' % external, self.tc_x[name],
                           config.DISPLAY_LOW_BAR_TEXT_Y[name])
                continue
            if self._last_temperatures[name][0] != external:
                self.chars('%5.1f ' % external, self.tc_x[name],
                           config.DISPLAY_LOW_BAR_TEXT_Y[name])

        if self._last_internal_temperature != max(internal_temps):
            self._last_internal_temperature = max(internal_temps)
            self.chars('%5.1f ' % self._last_internal_temperature,
                       self.tc_x[config.THERMOCOUPLE_NAME4],
                       config.DISPLAY_LOW_BAR_TEXT_Y[config.THERMOCOUPLE_NAME4])

        self._last_temperatures = temperatures.copy()
