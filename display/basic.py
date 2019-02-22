## ESP32 Reflow Oven
#
# Temperature Read and Display Thread

import _thread

from time import sleep

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

    def _prepare(self):
        """ Erase Display, Set Up Status Bars, etc. """
        # Erase
        self.erase()
        # Prepare top and bottom status bars
        self.fill_rectangle(0,
                            config.DISPLAY_TOP_BAR_Y,
                            config.DISPLAY_WIDTH,
                            config.DISPLAY_TOP_BAR_HEIGHT,
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
        self.x_ipaddress = self.chars('IP ',
                                      config.DISPLAY_TOP_BAR_TEXT_X,
                                      config.DISPLAY_TOP_BAR_TEXT_Y)
        self.set_font(tt24)


x_extra = display._font.get_width(' ')
x_tc1 = display.chars('TC1', 10, y_upper) + x_extra
x_tc2 = display.chars('TC2', 125, y_upper) + x_extra

x_tc3 = display.chars('TC3', 10, y_lower) + x_extra
x_internal = display.chars('INT', 135, y_lower) + x_extra

        self.prepared = True

    def show_ipaddress(self, ipaddress):
        if not self.prepared:
            return
        self.set_color(config.DISPLAY_STATUS_FG_COLOR,
                       config.DISPLAY_STATUS_BG_COLOR)
        self.set_font(tt14)
        self.chars('%s   ' % ipaddress,
                   self.x_ipaddress,
                   config.DISPLAY_TOP_BAR_TEXT_Y)
        self.set_font(tt24)

    def show_temperatures(self, temperatures):
        if not self.prepared:
            return
        if len(temperatures) != 3:
            return
        self.set_color(config.DISPLAY_STATUS_FG_COLOR,
                       config.DISPLAY_STATUS_BG_COLOR)

--- TODO ---
        w1 = display.chars('%.2f ' % c1, x_tc1, y_upper)
        w2 = display.chars('%.2f ' % c2, x_tc2, y_upper)
        w3 = display.chars('%.2f ' % c3, x_tc3, y_lower)
        wint = display.chars('%.2f ' % max(int1, int2, int3), x_tc2, y_lower)
