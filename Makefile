AMPY=ampy -p /dev/ttyUSB0
MPY_CROSS=../micropython/mpy-cross/mpy-cross -march=xtensa -X heapsize=111168 -O4

all:
	$(MPY_CROSS) boot.py
	$(MPY_CROSS) config.py
	$(MPY_CROSS) main.py
	$(MPY_CROSS) webrepl_cfg.py
	$(MPY_CROSS) wlan_sta.py
	$(MPY_CROSS) display/basic.py
	$(MPY_CROSS) display/icon.py
	$(MPY_CROSS) reflow/basedevice.py
	$(MPY_CROSS) reflow/device.py
	$(MPY_CROSS) reflow/menu.py
	$(MPY_CROSS) reflow/reflow.py
	$(MPY_CROSS) thermocouple/thermocouple.py

push:
	$(AMPY) put main.py main.py
	$(AMPY) put boot.mpy boot.mpy
	$(AMPY) put config.mpy config.mpy
	$(AMPY) put webrepl_cfg.mpy webrepl_cfg.mpy
	$(AMPY) put wlan_sta.mpy wlan_sta.mpy
	$(AMPY) put display/__init__.py display/__init__.py
	$(AMPY) put display/basic.mpy display/basic.mpy
	$(AMPY) put display/icon.mpy display/icon.mpy
	$(AMPY) put reflow/__init__.py reflow/__init__.py
	$(AMPY) put reflow/basedevice.mpy reflow/basedevice.mpy
	$(AMPY) put reflow/device.mpy reflow/device.mpy
	$(AMPY) put reflow/menu.mpy reflow/menu.mpy
	$(AMPY) put reflow/reflow.mpy reflow/reflow.mpy
	$(AMPY) put thermocouple/__init__.py thermocouple/__init__.py
	$(AMPY) put thermocouple/thermocouple.mpy thermocouple/thermocouple.mpy

push-main:
	$(AMPY) put main.mpy main.mpy

clean:
	rm -rf *.mpy
