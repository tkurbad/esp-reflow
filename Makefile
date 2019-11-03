AMPY=ampy -p /dev/ttyUSB0
MPY_CROSS=../micropython/mpy-cross/mpy-cross -march=xtensawin -X heapsize=111168 -O4

all:
	$(MPY_CROSS) config.py
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
	$(AMPY) put webrepl_cfg.mpy webrepl_cfg.mpy
	$(AMPY) put wlan_sta.mpy wlan_sta.mpy
	$(AMPY) mkdir --exists-okay display
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

reset:
	$(AMPY) reset --hard

clean:
	rm -rf *.mpy
