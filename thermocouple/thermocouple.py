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
        if name in Thermocouple._tcs.keys():
            raise RuntimeError('Thermocouple %s already added' % name)
        if Thermocouple._tcs:
            for (tc_name, tc) in Thermocouple._tcs.items():
                if ('Pin(%d)' % cs) == str(tc.spi.cs):
                    raise RuntimeError('Thermocouple "%s" is already configured for cs pin %d'
                                % (tc_name, cs))
        Thermocouple._tcs[name] = MAX31855(busid = Thermocouple._busid,
                                           cs = cs,
                                           baudrate = Thermocouple._baudrate)
        Thermocouple._temps[name] = (0.0, 0.0)

    def remove_tc(self, name):
        if name is None:
            raise RuntimeError('Thermocouple must have a name')
        if name not in self._tcs.keys():
            return
        del(Thermocouple._tcs[name])
        del(Thermocouple._temps[name])

    def read_temps(self):
        for (name, tc) in Thermocouple._tcs.items():
            Thermocouple._temps[name] = tc.read()

    @property
    def temp(self):
        return Thermocouple._temps
