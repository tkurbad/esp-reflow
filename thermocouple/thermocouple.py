# Temperature Reading Classes for ESP32 Micropython Driven
# SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

import _thread
from time import sleep

from max31855 import MAX31855

import config

class Thermocouple:
    """ Class to Manage and Read Several MAX31855 Thermocouple
        Amplifiers Connected to the Same Hardware SPI Bus, and their
        Values.
    """
    _busid = None       # Default Hardware SPI Bus Id
    _baudrate = None    # Default Baudrate
    _tcs = dict()       # Dictionary Holding All Configured Thermocouples
    _temps = dict()     # Dictionary Holding Last Temperature Readings

    def __init__(self, busid = None, baudrate = None):
        """ Initialize the Hardware SPI Bus for Use with MAX31855
            Thermocouple Amplifiers.
        """
        if busid is not None:
            if ((Thermocouple._busid is not None)
                and (Thermocouple._busid != busid)):
                raise RuntimeError('Thermocouple busid already initialized with %d'
                                    % Thermocouple._busid)
            Thermocouple._busid = busid
        if Thermocouple._busid is None:
            Thermocouple._busid = config.THERMOCOUPLE_BUSID
        if baudrate is not None:
            if ((Thermocouple._baudrate is not None)
                and (Thermocouple._baudrate != baudrate)):
                raise RuntimeError('Thermocouple baudrate already initialized with %d'
                                   % Thermocouple._baudrate)
            Thermocouple._baudrate = baudrate
        if Thermocouple._baudrate is None:
            Thermocouple._baudrate = config.THERMOCOUPLE_BAUDRATE

    def add_tc(self, name, cs):
        """ Add and Initialize a Thermocouple with Index Name 'name' and
            Chip Select Pin Number 'cs'.
        """
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
        """ Remove the Thermocouple with Index Name 'name' from the
            List of Active Thermocouples. """
        if name is None:
            raise RuntimeError('Thermocouple must have a name')
        if name not in self._tcs.keys():
            return
        del(Thermocouple._tcs[name])
        del(Thermocouple._temps[name])

    def read_temps(self):
        """ Read Temperatures from All Configured Thermocouples and
            Store them in the Class Variable _temps.
        """
        for (name, tc) in Thermocouple._tcs.items():
            Thermocouple._temps[name] = tc.read()

    @property
    def temp(self):
        """ Return the Last Temperature Readings of All Thermocouples.
        """
        return Thermocouple._temps
