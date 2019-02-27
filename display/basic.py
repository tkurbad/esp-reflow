## ESP32 Reflow Oven
#
# Display Class that Does All the Work on the TFT

from ili9341 import ILI9341, color565
from ili9341.fonts import tt14, tt24

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
        self.set_color(config.DISPLAY_STATUS_FG_COLOR,
                       config.DISPLAY_STATUS_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_TOP_BAR_Y,
                            config.DISPLAY_WIDTH,
                            config.DISPLAY_TOP_BAR_HEIGHT,
                            color = config.DISPLAY_STATUS_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_HEATER_DELIM_Y,
                            config.DISPLAY_WIDTH,
                            1,
                            color = config.DISPLAY_STATUS_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_LOW_BAR_Y1,
                            config.DISPLAY_WIDTH,
                            config.DISPLAY_LOW_BAR_HEIGHT,
                            color = config.DISPLAY_STATUS_BG_COLOR)
        self.fill_rectangle(0,
                            config.DISPLAY_LOW_BAR_Y2,
                            config.DISPLAY_WIDTH,
                            config.DISPLAY_LOW_BAR_HEIGHT,
                            color = config.DISPLAY_STATUS_BG_COLOR)
        self.set_font(tt14)
        self.ipaddress_x = self.chars('IP ',
                                      config.DISPLAY_TOP_BAR_TEXT_X,
                                      config.DISPLAY_TOP_BAR_TEXT_Y)
        self.set_font(tt24)
        self.tc_x = dict()
        for index in range(0:2):
            self.heater_x[index] = self.chars(
                                    config.HEATER_LABEL[index],
                                    config.DISPLAY_HEATER_TEXT_X[index],
                                    config.DISPLAY_HEATER_TEXT_Y
                                    )
        for tc_name in [config.THERMOCOUPLE_NAME1,
                        config.THERMOCOUPLE_NAME2,
                        config.THERMOCOUPLE_NAME3,
                        config.THERMOCOUPLE_NAME4]:
            self.tc_x[tc_name] = self.chars(
                                    config.THERMOCOUPLE_LABEL[tc_name],
                                    config.DISPLAY_LOW_BAR_TEXT_X[tc_name],
                                    config.DISPLAY_LOW_BAR_TEXT_Y[tc_name]
                                    )
        self.prepared = True

    def show_ipaddress(self, ipaddress):
        if not self.prepared:
            return
        self.set_color(config.DISPLAY_STATUS_FG_COLOR,
                       config.DISPLAY_STATUS_BG_COLOR)
        self.set_font(tt14)
        self.chars('%s   ' % ipaddress,
                   self.ipaddress_x,
                   config.DISPLAY_TOP_BAR_TEXT_Y)
        self.set_font(tt24)

    def show_temperatures(self, temperatures):
        if not self.prepared:
            return
        if len(temperatures) != 3:
            return
        self.set_color(config.DISPLAY_STATUS_FG_COLOR,
                       config.DISPLAY_STATUS_BG_COLOR)
        internal_temps = []
        for (name, (external, internal)) in temperatures.items():
            internal_temps.append(internal)
            self.chars('%.2f ' % external, self.tc_x[name],
                        config.DISPLAY_LOW_BAR_TEXT_Y[name])
        self.chars('%.2f ' % max(internal_temps),
                   self.tc_x[config.THERMOCOUPLE_NAME4],
                   config.DISPLAY_LOW_BAR_TEXT_Y[config.THERMOCOUPLE_NAME4])

    def show_heaters(self, heaters_pwm):
        if not self.prepared:
            return
        if len(heaters_pwm) != 2:
            return
        self.set_color(config.DISPLAY_HEATER_FG_COLOR,
                       config.DISPLAY_HEATER_BG_COLOR)
        self.chars('%.1f' % heaters_pwm[0], self.heater_x[0],
                   config.DISPLAY_HEATER_TEXT_Y)
        self.chars('%.1f' % heaters_pwm[1], self.heater_x[1],
                   config.DISPLAY_HEATER_TEXT_Y)
