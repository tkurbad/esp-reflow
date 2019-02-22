import _thread

from time import sleep

import config

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from wlan_sta import STA

##
## Setup
##

# Initialize Display
tft = Display()
tft.prepare()

# Initialize SPI bus for thermocouples
thermocouples = Thermocouple(busid = config.THERMOCOUPLE_BUSID,
                             baudrate = config.THERMOCOUPLE_BAUDRATE)

# Set up thermocouples
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME1, cs = THERMOCOUPLE_CS1)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME2, cs = THERMOCOUPLE_CS2)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME3, cs = THERMOCOUPLE_CS3)

# Allocate a lock for threads on the HSPI bus
hspiLock = _thread.allocate_lock()

# Get and Display IP Address
ipaddress = STA().ipaddress
tft.show_ipaddress(ipaddress)

def thermocoupleReadThread(lock):
    while True:
        with lock as l:
            thermocouples.read_temps()
        sleep(1)

def statusDisplayThread():
    while True:
        tft.show_temperatures()
        w1 = display.chars('%.2f ' % c1, x_tc1, y_upper)
        w2 = display.chars('%.2f ' % c2, x_tc2, y_upper)
        w3 = display.chars('%.2f ' % c3, x_tc3, y_lower)
        wint = display.chars('%.2f ' % max(int1, int2, int3), x_tc2, y_lower)
        if ipaddress != STA().ipaddress:
            ipaddress = STA().ipaddress
            tft.show_ipaddress(ipaddress)
        sleep(1)

_thread.start_new_thread(thermocoupleReadThread, (hspiLock, ))
_thread.start_new_thread(statusDisplayThread, ())

print (thermocouples.temp)
sleep(10)
print (thermocouples.temp)
sleep(10)
print (thermocouples.temp)
