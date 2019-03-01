## ESP32 Reflow Oven
#
# Display Class that Does All the Work on the TFT

from ili9341 import ILI9341

import config

class Display(ILI9341):

    def __init__(self):
        super().__init__(busid = config.DISPLAY_BUSID,
                         cs = config.DISPLAY_CS_PIN,
                         dc = config.DISPLAY_DC_PIN,
                         baudrate = config.DISPLAY_BAUDRATE)
        self.prepared = False

    def prepare(self):
        """ Erase Display, Set Up Status Bars, etc. """
        # Erase
        self.erase()
        # Prepare top and bottom status bars
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
        self.set_font(config.DISPLAY_TOP_BAR_FONT)
        self.ipaddress_x = self.chars('IP ',
                                      config.DISPLAY_TOP_BAR_TEXT_X,
                                      config.DISPLAY_TOP_BAR_TEXT_Y)
        self.set_font(config.DISPLAY_LABEL_FONT)
        self.set_color(config.DISPLAY_LABEL_FG_COLOR,
                       config.DISPLAY_LABEL_BG_COLOR)
        self.chars(config.DISPLAY_HEATER_LABEL,
                   config.DISPLAY_LABEL_X,
                   config.DISPLAY_HEATER_LABEL_Y)
        self.chars(config.DISPLAY_LOW_BAR_LABEL,
                   config.DISPLAY_LABEL_X,
                   config.DISPLAY_LOW_BAR_LABEL_Y)
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

    def show_ipaddress(self, ipaddress):
        if not self.prepared:
            return
        self.set_color(config.DISPLAY_TOP_BAR_FG_COLOR,
                       config.DISPLAY_TOP_BAR_BG_COLOR)
        self.set_font(config.DISPLAY_TOP_BAR_FONT)
        self.chars('%s   ' % ipaddress,
                   self.ipaddress_x,
                   config.DISPLAY_TOP_BAR_TEXT_Y)

    def show_temperatures(self, temperatures):
        if not self.prepared:
            return
        if len(temperatures) != config.NUM_THERMOCOUPLES:
            return
        self.set_color(config.DISPLAY_THERMOCOUPLE_FG_COLOR,
                       config.DISPLAY_THERMOCOUPLE_BG_COLOR)
        self.set_font(config.DISPLAY_LOW_BAR_FONT)
        internal_temps = []
        for (name, (external, internal)) in temperatures.items():
            internal_temps.append(internal)
            self.chars('%5.1f ' % external, self.tc_x[name],
                        config.DISPLAY_LOW_BAR_TEXT_Y[name])
        self.chars('%5.1f ' % max(internal_temps),
                   self.tc_x[config.THERMOCOUPLE_NAME4],
                   config.DISPLAY_LOW_BAR_TEXT_Y[config.THERMOCOUPLE_NAME4])

    def show_heaters(self, heater_duty):
        if not self.prepared:
            return
        if len(heater_duty) != config.NUM_HEATERS:
            return
        self.set_color(config.DISPLAY_HEATER_FG_COLOR,
                       config.DISPLAY_HEATER_BG_COLOR)
        self.set_font(config.DISPLAY_LOW_BAR_FONT)
        for (name, duty) in heater_duty.items():
            self.chars('%5.1f ' % duty, self.heater_x[name],
                            config.DISPLAY_HEATER_TEXT_Y)
