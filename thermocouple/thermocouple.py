## ESP32 Reflow Oven
#
# Temperature Read and Display Thread

import _thread

from time import sleep

from hwspi.hwspi import HSPI, VSPI

from ili9341 import ILI9341, color565
from ili9341.fonts import tt14, tt24

from max31855 import MAX31855

from wlan_sta import STA

# Setup
display = ILI9341(busid = VSPI, cs = 22, dc = 21, baudrate = 60000000)
tc1 = MAX31855(busid = HSPI, cs = 15)
tc2 = MAX31855(busid = HSPI, cs = 2)
tc3 = MAX31855(busid = HSPI, cs = 4)
bgcolor = color565(200, 200, 200)
fgcolor = color565(0, 0, 0)

y_ip = 2

y_upper = 262
y_lower = 293

# Init Display
display.erase()
display.fill_rectangle(0, 0, 240, 19, color = bgcolor)

display.fill_rectangle(0, 260, 240, 29, color = bgcolor)
display.fill_rectangle(0, 291, 240, 29, color = bgcolor)
display.set_color(fgcolor, bgcolor)

ip = STA().ipaddress

display.set_font(tt14)
tt14_extra = display._font.get_width(' ')
x_ip = display.chars('IP', 10, y_ip) + tt14_extra
display.chars(ip, x_ip, y_ip)

display.set_font(tt24)
x_extra = display._font.get_width(' ')
x_tc1 = display.chars('TC1', 10, y_upper) + x_extra
x_tc2 = display.chars('TC2', 125, y_upper) + x_extra

x_tc3 = display.chars('TC3', 10, y_lower) + x_extra
x_internal = display.chars('INT', 135, y_lower) + x_extra


def tempThread(ip):
    while True:
        c1, int1 = tc1.read()
        c2, int2 = tc2.read()
        c3, int3 = tc3.read()
        w1 = display.chars('%.2f ' % c1, x_tc1, y_upper)
        w2 = display.chars('%.2f ' % c2, x_tc2, y_upper)
        w3 = display.chars('%.2f ' % c3, x_tc3, y_lower)
        wint = display.chars('%.2f ' % max(int1, int2, int3), x_tc2, y_lower)
        if ip != STA().ipaddress:
            ip = STA().ipaddress
            display.set_font(tt14)
            display.chars(ip, x_ip, y_ip)
            display.set_font(tt24)
        sleep(1)

_thread.start_new_thread(tempThread, (ip, ))
