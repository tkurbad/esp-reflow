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
from reflow.device import ButtonDown, ButtonLeft, ButtonRight, ButtonUp
from reflow.device import Buzzer, Fan, HeaterBottom, HeaterTop, Light
from reflow.device import RotaryEncoder, SDCardHandler
from reflow.menu import Menu
from wlan_sta import STA

##
## Setup
##

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

# Set Up the Push Buttons
button_up = ButtonUp()
button_left = ButtonLeft()
button_right = ButtonRight()
button_down = ButtonDown()

# Let Device Settle
sleep(1)

# Initialize and Try to Mount SD Card
sdcard = SDCardHandler()
sdcard.mount()

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
    global ipaddress, sdcard
    with lock as l:
        tft.show_ipaddress(ipaddress)

    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            tft.show_heaters(heater_duty)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
            tft.show_fan(fan.duty())
            tft.show_light(light.pin.value())
            tft.show_sdcard(sdcard.is_mounted())
        sleep(1)

def buttonThread():
    while True:
        sleep_ms(50)
        if button_up.value():
            print('Up')
            continue
        if button_down.value():
            print('Down')
            continue
        if button_left.value():
            print('Left')
            continue
        if button_right.value():
            print('Right')


# Start Reading Heat Values (with Locking)
_thread.start_new_thread(heatReadThread, (reflowLock, ))
# Start Displaying Status (with Locking)
_thread.start_new_thread(statusDisplayThread, (reflowLock, ))

# Start Reading Button Presses (without Locking)
_thread.start_new_thread(buttonThread, ())

# Run Garbage Collector
gc.collect()

##
## Main Menu
##

## Menu Item Switching Callback Functionss (Have to Return True / False)

# Define Menu Items
#  Format:
#   OrderedDict with Menu Item Ids as Keys (Arbitrary Strings)
#    and
#   lists [trigger t, (label0, callback0, cb0 options if trigger == False), (label1, callback1, cb1 options if trigger == True)]
#
# Example Static Menu Item
#  calibrate = [False, ('Calibrate', calibrate, (test = 1)), (None, None, None)]
#
# Example Dynamic Menu Item
#  sdcard = [sd_card_mounted, ('Mount SD Card', mount_sd, None), ('Umount SD Card', umount_sd, None)]

menuitems = [
    [False, 'Hallo', None, None, None, None, None],
    [False, 'Ballo', None, None, None, None, None],
    [False, 'Popallo', None, None, None, None, None],
    [False, 'Fan', None, None, None, None, None],
    [sdcard.is_mounted, 'Mount SD Card', sdcard.mount, None, 'Unmount SD Card', sdcard.umount, None]
]

# Set Up Menu
menu = Menu(menuitems, tft, rotary, lock = reflowLock)


##
## Main Code
##

# Initial Menu Display
menu.draw_items()

# Play Jingle
buzzer.jingle()

###
# IDEE:
# Callback-Funktionen / IRQ-Handler fuer Rotary konfigurierbar machen
# a la rotary.button_callback(callback)
###

##
# TODO:
# - SD-Karten Filebrowser
# - File-Headers ili9341 Modul

# with heater_bottom as hb, heater_top as ht, fan as fa, light as li:
    # li.on()
    # fa.duty(20)
    # hb.duty(10)
    # ht.duty(100)
    # sleep(10)
    # fa.duty(50)
    # hb.duty(50)
    # ht.duty(50)
    # sleep(10)
    # fa.duty(10)
    # hb.duty(100)
    # ht.duty(100)
    # sleep(10)

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
