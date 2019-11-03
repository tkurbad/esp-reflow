# Boot File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from esp import osdebug
from _thread import start_new_thread
import webrepl

from time import sleep
from wlan_sta import STA

osdebug(None)

# Activate WebREPL.
webrepl.start()

try:
    # Import Configured SSIDs.
    from private import ssids
except ImportError:
    ssids = []

wifi = STA()


def connectWifi():
    """ WiFi Connection Method. """
    while not wifi.isconnected():
        for (ssid, passphrase) in ssids:
            if wifi.connect(ssid, passphrase):
                return
        sleep(10)

# Connect to the WiFi Network if One or More SSIDs Have Been Configured.
if ssids:
    start_new_thread(connectWifi, ())
