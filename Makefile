# Makefile for ESP32 Micropython Driven SMD Reflow Oven Project
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

# Install 'ampy' using
#
#  pip install adafruit-ampy
#
# Add 'ampy' to Path and Set Full Commandline Options Here.
AMPY=ampy -p /dev/ttyUSB0

# Put Full Commandline for 'mpy-cross' Here.
# Note: 'mpy-cross' is Part of the Official Micropython Distribution
#       [https://github.com/micropython/micropython]
#       For this Project, the Latest Forked Version of Micropython at
#       https://github.com/tkurbad/micropython/tree/esp32-reflow
#       is Mandatory.
MPY_CROSS=../micropython/mpy-cross/mpy-cross -march=xtensawin -X heapsize=111168 -O4

# If You Connect to the ESP32 via USB Serial, You Build and Deploy the
# Project to the Device by Issuing
#
#  make && make erase && make deploy
#
# If You Want to Erase the Currently Saved Reflow Profile from the
# Device, too, Type
#
#  make mrproper
#
# Instead of
#
#  make erase
#

all:
	$(MPY_CROSS) config.py
	-$(MPY_CROSS) private.py 2>/dev/null
	$(MPY_CROSS) webrepl_cfg.py
	$(MPY_CROSS) wlan_sta.py
	$(MPY_CROSS) display/basic.py
	$(MPY_CROSS) display/icon.py
	$(MPY_CROSS) reflow/basedevice.py
	$(MPY_CROSS) reflow/device.py
	$(MPY_CROSS) reflow/error.py
	$(MPY_CROSS) reflow/menu.py
	$(MPY_CROSS) reflow/profile.py
	$(MPY_CROSS) reflow/reflow.py
	$(MPY_CROSS) thermocouple/thermocouple.py

deploy:
	$(AMPY) put boot.py boot.py
	$(AMPY) put main.py main.py
	$(AMPY) put config.mpy config.mpy
	-$(AMPY) put private.mpy 2>/dev/null
	$(AMPY) put webrepl_cfg.mpy webrepl_cfg.mpy
	$(AMPY) put wlan_sta.mpy wlan_sta.mpy
	-$(AMPY) mkdir --exists-okay display 2>/dev/null
	-$(AMPY) mkdir --exists-okay display 2>/dev/null
	$(AMPY) put display/__init__.py display/__init__.py
	$(AMPY) put display/basic.mpy display/basic.mpy
	$(AMPY) put display/icon.mpy display/icon.mpy
	$(AMPY) mkdir --exists-okay reflow
	$(AMPY) put reflow/__init__.py reflow/__init__.py
	$(AMPY) put reflow/basedevice.mpy reflow/basedevice.mpy
	$(AMPY) put reflow/device.mpy reflow/device.mpy
	$(AMPY) put reflow/error.mpy reflow/error.mpy
	$(AMPY) put reflow/menu.mpy reflow/menu.mpy
	$(AMPY) put reflow/profile.mpy reflow/profile.mpy
	$(AMPY) put reflow/reflow.mpy reflow/reflow.mpy
	$(AMPY) mkdir --exists-okay thermocouple
	$(AMPY) put thermocouple/__init__.py thermocouple/__init__.py
	$(AMPY) put thermocouple/thermocouple.mpy thermocouple/thermocouple.mpy

erase:
	-$(AMPY) rm boot.py 2>/dev/null
	-$(AMPY) rm main.py 2>/dev/null
	-$(AMPY) rm config.py 2>/dev/null
	-$(AMPY) rm config.mpy 2>/dev/null
	-$(AMPY) rm private.py 2>/dev/null
	-$(AMPY) rm private.mpy 2>/dev/null
	-$(AMPY) rm webrepl_cfg.py 2>/dev/null
	-$(AMPY) rm webrepl_cfg.mpy 2>/dev/null
	-$(AMPY) rm wlan_sta.py 2>/dev/null
	-$(AMPY) rm wlan_sta.mpy 2>/dev/null
	-$(AMPY) rmdir display 2>/dev/null
	-$(AMPY) rmdir reflow 2>/dev/null
	-$(AMPY) rmdir thermocouple 2>/dev/null

mrproper: erase
	-$(AMPY) rm current.prf 2>/dev/null

reset:
	$(AMPY) reset --hard

clean:
	rm -rf *.mpy
