## ESP32 Reflow Oven
#
# Temperature Read Thread Definition

import _thread
from time import sleep

from max31855 import MAX31855

import config

class Thermocouple:

    _busid = None
    _baudrate = None
    _tcs = dict()
    _temps = dict()

    def __init__(self, busid = config.THERMOCOUPLE_BUSID,
        baudrate = config.THERMOCOUPLE_BAUDRATE):
        if Thermocouple._busid is None:
            Thermocouple._busid = busid
        if Thermocouple._busid != busid:
            raise RuntimeError('Thermocouple busid already initialized with %d'
                                % Thermocouple._busid)
        if Thermocouple._baudrate is None:
            Thermocouple._baudrate = baudrate
        if Thermocouple._baudrate != baudrate:
            raise RuntimeError('Thermocouple baudrate already initialized with %d'
                                % Thermocouple._baudrate)

    def add_tc(self, name, cs):
        if name is None:
            raise RuntimeError('Thermocouple must have a name')
        Thermocouple._tcs[name] = MAX31855(busid = Thermocouple._busid, cs = cs))
        Thermocouple._temps[name] = (0.0, 0.0)

    def remove_tc(self, name):
        if name is None:
            raise RuntimeError('Thermocouple must have a name')
        del(Thermocouple._tcs[name])
        del(Thermocouple._temps[name])

    def read_temps(self):
        for tc in Thermocouple._tcs.keys():
            Thermocouple._temps[name] = tc.read()


--- MOVE!!! ---
# Setup
tc1 = MAX31855(busid = HSPI, cs = 15)
tc2 = MAX31855(busid = HSPI, cs = 2)
tc3 = MAX31855(busid = HSPI, cs = 4)


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
