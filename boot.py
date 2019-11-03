# Boot File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from esp import osdebug
from _thread import start_new_thread
import webrepl

from time import sleep
from wlan_sta import STA

osdebug(None)

webrepl.start()

ssids = [
    ('IWM', 'Be wary then; best safety lies in fear'),
    ('TORSTI-WLAN', 'To improve is to change;')
]

wifi = STA()

def connectWifi():
    while not wifi.isconnected():
        for (ssid, passphrase) in ssids:
            if wifi.connect(ssid, passphrase):
                return
        sleep(10)

start_new_thread(connectWifi, ())
