# Main Execution File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect, mem_alloc, mem_free, threshold
from _thread import allocate_lock, start_new_thread

from machine import reset
from utime import sleep_ms

from config import THERMOCOUPLE_BUSID, THERMOCOUPLE_BAUDRATE
from config import THERMOCOUPLE_NAME1, THERMOCOUPLE_NAME2, THERMOCOUPLE_NAME3
from config import THERMOCOUPLE_CS1, THERMOCOUPLE_CS2, THERMOCOUPLE_CS3

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from reflow.device import ButtonDown, ButtonLeft, ButtonRight, ButtonUp
from reflow.device import Buzzer, Fan, HeaterBottom, HeaterTop, Light
from reflow.device import RotaryEncoder, SDCardHandler
from reflow.menu import Menu
from reflow.reflow import HeatControl
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
thermocouples = Thermocouple(busid = THERMOCOUPLE_BUSID,
                             baudrate = THERMOCOUPLE_BAUDRATE)

# Set up thermocouples
thermocouples.add_tc(name = THERMOCOUPLE_NAME1,
                     cs = THERMOCOUPLE_CS1)
thermocouples.add_tc(name = THERMOCOUPLE_NAME2,
                     cs = THERMOCOUPLE_CS2)
thermocouples.add_tc(name = THERMOCOUPLE_NAME3,
                     cs = THERMOCOUPLE_CS3)

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

sleep_ms(500)
threshold(mem_free() // 4 + mem_alloc())
collect()

# Initialize and Try to Mount SD Card
sdcard = SDCardHandler()
sleep_ms(500)

try:
    sdcard.mount()
except MemoryError as e:
    print (e)
    pass

collect()

# Allocate a lock
reflowLock = allocate_lock()

# Heat Control Object
heat_control = HeatControl(lock = reflowLock,
                           thermocouples = thermocouples,
                           heater_top = heater_top,
                           heater_bottom = heater_bottom,
                           fan = fan,
                           reflow_profile = None,
                           buzzer = buzzer,
                           light = light)
collect()


##
## Basic Threads
##
def statusDisplayThread(lock):
    """ Display Status, i.e. IP-Address and Temperatures on TFT. """
    global ipaddress, sdcard
    with lock as l:
        tft.show_ipaddress(ipaddress)

    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            tft.show_heaters(heat_control.heater_duty)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
            tft.show_fan(fan.duty())
            tft.show_light(light.pin.value())
            tft.show_sdcard(sdcard.is_mounted())
        sleep_ms(1000)

def buttonThread():
    # For now, just duplicate/emulate the rotary encoder
    while True:
        sleep_ms(50)
        if button_up.value():
            if rotary._value > rotary._min_val:
                rotary._value -= 1
            continue
        if button_down.value():
            if rotary._value < rotary._max_val:
                rotary._value += 1
            continue
        if button_left.value():
            print('Left')
            continue
        if button_right.value():
            rotary._button_pressed = True


# Start Reading Heat Values (with Locking - Lock Variable Given During Init)
start_new_thread(heat_control.heatReadResponse, ())

# Start Displaying Status (with Locking)
start_new_thread(statusDisplayThread, (reflowLock, ))

# Start Reading Button Presses (without Locking)
start_new_thread(buttonThread, ())

# Run Garbage Collector
collect()

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
    [heat_control.isReflowing, 'Start Reflow', heat_control.startReflow, None, 'Stop Reflow', heat_control.cancelReflow, None],
    [light.pin.value, 'Turn on Light', light.pin.on, None, 'Turn off Light', light.pin.off, None],
    [sdcard.is_mounted, 'Mount SD Card', sdcard.mount, None, 'Unmount SD Card', sdcard.umount, None],
    [False, 'Reboot', reset, None, None, None, None],
]

# Set Up Menu
menu = Menu(menuitems, tft, rotary, lock = reflowLock)


##
## Main Code
##

# Initial Menu Display
menu.draw_items()

# Play Jingle
#buzzer.jingle()

# Print Initial Amount of Free Memory
print ('Free Memory:', mem_free())
###
# IDEE:
# Callback-Funktionen / IRQ-Handler fuer Rotary konfigurierbar machen
# a la rotary.button_callback(callback)
###

##
# TODO:
# - SD-Karten Filebrowser
# - File-Headers ili9341 Modul

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
