import gc
import _thread

from machine import Pin, PWM, reset
from os import mount, umount
from time import sleep

import config

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from reflow.device import Fan, HeaterBottom, HeaterTop, Light#, Rotary
from reflow.menu import Menu
#from sdcard import SDCard
from reflow.sdcard import SDCard
from wlan_sta import STA

##
## Setup - 1st Part
##

# SD Card Present?
SD_CARD_MOUNTED = False
sd = None

# Initialize Display
tft = Display()
tft.prepare()

# Set Up Light Switch
light = device.Light()

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

# Set Up Variable to Display Duty Cycles
heater_duty = {
    config.HEATER_NAME_TOP: 0.0,
    config.HEATER_NAME_BOTTOM: 0.0
}
##
## Basic Threads
##

# Allocate a lock for thermocouple related threads
tcLock = _thread.allocate_lock()

# Get and Display IP Address
ipaddress = STA().ipaddress
tft.show_ipaddress(ipaddress)

def thermocoupleReadThread(lock):
    """ Read Thermocouples Every 500 ms. """
    while True:
        with lock as l:
            thermocouples.read_temps()
        sleep(0.5)

def statusDisplayThread(lock):
    """ Display Status, i.e. IP-Address and Temperatures on TFT. """
    global ipaddress
    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
        sleep(1)

def heaterDisplayThread(lock):
    """ Display PWM Duty Setting of Both Heaters. """
    global heater_duty
    while True:
        heater_duty[config.HEATER_NAME_TOP] = heater_top.duty()
        heater_duty[config.HEATER_NAME_BOTTOM] = heater_bottom.duty()
        with lock as l:
            tft.show_heaters(heater_duty)
        sleep(1)

# Start Reading Thermocouples (with Locking)
_thread.start_new_thread(thermocoupleReadThread, (tcLock, ))
# Start Displaying Satus (with Locking)
_thread.start_new_thread(statusDisplayThread, (tcLock, ))

# Run Garbage Collector
gc.collect()

##
## Setup - 2nd Part
##

# Set Up Buzzer
buzzer = device.Buzzer()

# Set Up Top Heater
heater_top = device.HeaterTop()

# Set Up Bottom Heater
heater_bottom = device.HeaterBottom()

# Set Up Fan
fan = device.Fan()

# Try to Mount SD Card
try:
    with tcLock as l:
        sd = SDCard(cs = config.SDCARD_CS)
except OSError as e:
    if 'no sd card' in e.args[0].lower():
        print("Initialize regular watch for SD Card (via thread or timer)")

if sd is not None:
    try:
        mount(sd, '/sd')
        SD_CARD_MOUNTED = True
    except OSError:
        try:
            with tcLock as l:
                sd.init_card_v1()
            mount(sd, '/sd')
            SD_CARD_MOUNTED = True
        except OSError:
            pass

# Initialize Menu Display
menuitems = (,)
rotary = None
menu = Menu(menuitems, tft, None)

##
## Main Code
##

# Start Displaying Heater Settings (with Locking)
_thread.start_new_thread(heaterDisplayThread, (tcLock, ))

# Play Jingle
buzzer.jingle()

with heater_bottom as hb, heater_top as ht, fan as f, light as li:
    li.on()
    hb.duty(100)
    ht.duty(50)
    f.duty(20)
    sleep(20)
    hb.duty(30)
    ht.duty(100)
    sleep(10)
    hb.duty(10)
    ht.duty(10)
    sleep(10)

#try:
#    while True:
#        sleep(1)
#finally:
#    heater_bottom.deinit()
#    heater_top.deinit()
#    fan.deinit()
#    buzzer.deinit()

heater_bottom.deinit()
heater_top.deinit()
fan.deinit()
buzzer.deinit()
