import _thread

from machine import Pin, PWM
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
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME1,
                     cs = config.THERMOCOUPLE_CS1)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME2,
                     cs = config.THERMOCOUPLE_CS2)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME3,
                     cs = config.THERMOCOUPLE_CS3)

# Allocate a lock for thermocouple related threads
tcLock = _thread.allocate_lock()

# Get and Display IP Address
ipaddress = STA().ipaddress
tft.show_ipaddress(ipaddress)

def thermocoupleReadThread(lock):
    while True:
        with lock as l:
            thermocouples.read_temps()
        sleep(0.5)

def statusDisplayThread(lock):
    global ipaddress
    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
        sleep(1)

_thread.start_new_thread(thermocoupleReadThread, (tcLock, ))
_thread.start_new_thread(statusDisplayThread, (tcLock, ))

# Play sequence (C#3 - C#8)
buzzer = PWM(Pin(0, Pin.OUT), freq = 0, duty = 0)
for note in [277, 554, 1109, 2217, 4435]:
    buzzer.freq(note)
    buzzer.duty(500)
    sleep(0.2)
    buzzer.duty(0)
buzzer.deinit()
