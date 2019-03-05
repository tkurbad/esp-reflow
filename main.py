# Main Execution File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

import gc
import _thread

from machine import Pin, PWM, reset
from os import mount, umount
from time import sleep, sleep_ms

import config

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from reflow.device import Buzzer, Fan, HeaterBottom, HeaterTop, Light
from reflow.device import RotaryEncoder, SDCardHandler
from reflow.menu import Menu
from wlan_sta import STA

##
## Setup
##

# SD Card Present?
SD_CARD_MOUNTED = False

# Initialize Display
tft = Display()
tft.prepare()

# Set Up Light Switch
light = Light()

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
# Allocate a lock
reflowLock = _thread.allocate_lock()

# Get and Display IP Address
ipaddress = STA().ipaddress
tft.show_ipaddress(ipaddress)

# Set Up Buzzer
buzzer = Buzzer()

# Set Up Top Heater
heater_top = HeaterTop()

# Set Up Bottom Heater
heater_bottom = HeaterBottom()

# Set Up Fan
fan = Fan()

# Set Up Rotary Encoder
rotary = RotaryEncoder()

# Define Menu Items
menuitems = (
    ('hallo', None, None),
    ('ballo', None, None),
    ('popallo', None, None),
    ('fan', None, None),
)

# Set Up Menu
menu = Menu(menuitems, tft, rotary, lock = reflowLock)

##
## Basic Threads
##
def heatReadThread(lock):
    """ Read Heater PWM Duty Settings and Thermocouple Values Every
        500 ms.
    """
    global heater_duty
    while True:
        heater_duty[config.HEATER_NAME_TOP] = heater_top.duty()
        heater_duty[config.HEATER_NAME_BOTTOM] = heater_bottom.duty()
        with lock as l:
            thermocouples.read_temps()
        sleep_ms(500)

def statusDisplayThread(lock):
    """ Display Status, i.e. IP-Address and Temperatures on TFT. """
    global ipaddress
    while True:
        with lock as l:
            tft.show_heaters(heater_duty)
            tft.show_temperatures(thermocouples.temp)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
        sleep(1)

# Start Reading Heat Values (with Locking)
_thread.start_new_thread(heatReadThread, (reflowLock, ))
# Start Displaying Status (with Locking)
_thread.start_new_thread(statusDisplayThread, (reflowLock, ))

# Run Garbage Collector
gc.collect()

# Initialize and Try to Mount SD Card
sdcard = SDCardHandler()
SD_CARD_MOUNTED = sdcard.mount()

##
## Main Code
##

# Initial Menu Display
menu.draw_items()

# Play Jingle
buzzer.jingle()

# with heater_bottom as hb, heater_top as ht, fan as f, light as li:
    # li.on()
    # hb.duty(100)
    # ht.duty(50)
    # f.duty(20)
    # sleep(20)
    # hb.duty(30)
    # ht.duty(100)
    # sleep(10)
    # hb.duty(10)
    # ht.duty(10)
    # sleep(10)


###
# IDEE:
# Callback-Funktionen / IRQ-Handler fuer Rotary konfigurierbar machen
# a la rotary.button_callback(callback)
###

##
# TODO:
# - SD-Karten Filebrowser
# - Symbole Fan/Licht/SD

try:
    """ Handle Menu Input. """
    menu.loop()

finally:
    """ Deinitialize all PWM and SPI Devices.
        !!! Disable Heaters First to Prevent Fires !!!
    """
    heater_bottom.deinit()
    heater_top.deinit()
    fan.deinit()
    buzzer.deinit()
    sdcard.deinit()
