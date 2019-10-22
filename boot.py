# Boot File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

import esp
import _thread
#import webrepl

from time import sleep
from wlan_sta import STA

esp.osdebug(None)

#webrepl.start()

ssids = [
    ('IWM', 'Be wary then; best safety lies in fear'),
    ('TORSTI-WLAN', 'To improve is to change;')
]

wifi = STA()

def connectWifi():
    while True:
        if wifi.isconnected():
            return
        for (ssid, passphrase) in ssids:
            if wifi.connect(ssid, passphrase):
                return
        sleep(10)

_thread.start_new_thread(connectWifi, ())

