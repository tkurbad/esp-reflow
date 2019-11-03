# WiFi Interface Class for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from time import sleep
from network import STA_IF, WLAN

class STA:
    """ WiFi Station. """
    _ipaddress = '0.0.0.0'
    _ssid = ''
    sta = None

    def __init__(self, *args, **kwargs):
        STA.sta = WLAN(STA_IF)

    def active(self, value = None):
        if STA.sta is None:
            return
        return STA.sta.active(value)

    def config(self, param):
        if STA.sta is None:
            return
        return STA.sta.config(param)

    def connect(self, essid, passphrase):
        if STA.sta is None:
            return
        STA.sta.active(True)
        if STA.sta.isconnected():
            STA.sta.disconnect()
        STA.sta.connect(essid, passphrase)
        timeout = 30
        while timeout >= 0 and not STA.sta.isconnected():
            timeout -= 1
            sleep(1)
        if STA.sta.isconnected():
            sleep(2)
            STA._ip_address = STA.sta.ifconfig()[0]
            STA._ssid = essid
            return True
        return False

    def disconnect(self):
        if STA.sta is None:
            return
        return STA.sta.disconnect()

    def ifconfig(self):
        if STA.sta is None:
            return
        return STA.sta.ifconfig()

    def isconnected(self):
        if STA.sta is None:
            return
        return STA.sta.isconnected()

    def scan(self):
        if STA.sta is None:
            return
        return STA.sta.scan()

    def status(self):
        if STA.sta is None:
            return
        return STA.sta.status()

    @property
    def ipaddress(self):
        STA._ipaddress = '0.0.0.0'
        if STA.sta.isconnected:
            STA._ipaddress = STA.sta.ifconfig()[0]
        return STA._ipaddress
