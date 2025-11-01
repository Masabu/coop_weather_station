
# coop_weather_station
Chicken coop weather station

## Hardware
* Two DS18B20 temperature sensors, both attached at Pin 5.
* LED Pin 4   : WiFi status (green)
* LED Pin 22  : Sensor status (yellow)
* LED Pin 23  : Data transmission status (red)
* BME 280 Pin 25, 26: I2C port for barometer, temp, and humiditity

## Python Class: Monitor
The `Monitor` class in `monitor.py` manages temperature sensor readings and Blynk data transmission.

- **Initialization:**
	- `Monitor(ds_pin, AUTH)` sets up the DS18B20 sensors and Blynk configuration.
- **send_to_blynk:**
	- Sends both temperature readings to Blynk in a single API call.
- **read_humidity:**
	- Placeholder for future humidity sensor integration.
- **led_blink:**
	- Blinks an LED on a specified pin to indicate data transmission or status.
- **loop_section(wait_time):**
	- Main loop: reads temperatures, sends data, blinks LED, and waits for the next cycle.

## main.py Usage
`main.py` handles WiFi connection, LED status indication, and starts the monitoring loop:

1. Turns all status LEDs OFF at startup.
2. Connects to WiFi and turns the WiFi status LED ON if successful.
3. Creates a `Monitor` object and starts the main monitoring loop.

Example:
```python
from monitor import Monitor
from machine import Pin
from secret import BLYNK_AUTH_TOKEN

probe = Monitor(ds_pin=Pin(5), AUTH=BLYNK_AUTH_TOKEN)
probe.loop_section(wait_time=100)
```

## Useful commands

mpremote connect list  
mpremote connect [device name]
mpremote ls

### Copy files
mpremote cp main.py :main.py 

### Reboot
mpremote connect /dev/ttyUSB0 reset
mpremote connect /dev/ttyUSB0 repl

