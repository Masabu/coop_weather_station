
# coop_weather_station
Chicken coop weather station

## Hardware
* Two DS18B20 temperature sensors, both attached at Pin 5.
* LED Pin 4   : WiFi status (green)
* LED Pin 22  : Sensor status (yellow)
* LED Pin 23  : Data transmission status (red)
* LED Pin 27  : I2C/BME280 status (blue)
* BME 280 Pin 25, 26: I2C port for barometer, temp, and humiditity

### GPIO summary & devices

- DS18B20 temperature sensors: both on 1-wire bus at GPIO5 (use a single pull-up resistor on the data line -- see resistor notes below)
- BME280: I2C on GPIO25 (SDA) and GPIO26 (SCL). Typical I2C address 0x76 or 0x77 depending on module.
+- LEDs:
+  - GPIO4  — WiFi status (green)
+  - GPIO22 — Sensor status (yellow)
+  - GPIO23 — Data transmission status (red)
+  - GPIO27 — I2C/BME280 status (blue)

If you add extra LEDs, safe GPIO choices are e.g. 13, 16, 17, 27, 32, 33 on most ESP32 devboards. Avoid pins 6..11 (flash) and 34..39 (input only), and be careful with boot/strap pins (0, 2, 12, 15).

## Python Class: Monitor (overview)

`monitor.py` provides the `Monitor` class which centralizes sensor reads and Blynk uploads. Recent updates make the class modular and reduce API usage by sending combined payloads.

- Constructor: `Monitor(ds_pin, AUTH)`
  - `ds_pin` may be an integer GPIO number or a `machine.Pin` instance (default in examples: Pin 5)
  - `AUTH` is your Blynk auth token (from `secret.py` in the repo)
  - Initialization is split into small helpers:
	- `_init_ds18()` — sets up the DS18B20 one-wire bus and marks sensor LED
	- `_init_i2c_and_bme()` — scans I2C and initializes BME280 (if present)
	- `_init_blynk()` — stores Blynk endpoint and token

Key methods

- `read_ds()` — converts & reads DS18B20 sensors; returns a list of temperatures (may include `None` for failed reads).
- `read_bme()` — reads the BME280 and returns `(temp, pressure, humidity)` or `None` when unavailable.
- `read_all()` — combines available sensor readings into a single dict mapped to Blynk virtual pins:
  - DS18B20: V0 (sensor 1), V1 (sensor 2)
  - BME280: V2 (temp), V3 (pressure), V4 (humidity)
- `send_to_blynk(data)` — accepts a dict of virtual-pin → value (keys may be `V0`, `'0'`, or `0`) and sends them in a single HTTP GET to Blynk's batch/update endpoint.
- `send_combined()` — helper that calls `read_all()` and sends the combined payload if non-empty.
- `loop_section(wait_time)` — main loop: calls `send_combined()` every `wait_time` seconds and blinks the data LED on successful send.

Behavior notes

- Combined payload: When at least one sensor returns a value the monitor will send a single, combined Blynk request containing all available values. This reduces API calls and network overhead.
- Empty payloads: If no sensors return values, `send_combined()` will not send data to Blynk (it prints "No sensor data to send"). If you want a heartbeat or to resend last-known values, see the suggestions in the repo (or ask and I'll add them).
- BME initialization: `monitor` detects I2C devices and attempts to initialize the BME280. If initialization fails the code sets `self.bme = None` and continues; BME reads are skipped.

## main.py Usage
`main.py` handles WiFi connection, LED status indication, and starts the monitoring loop.

Typical flow

1. Turn status LEDs OFF at startup
2. Connect to WiFi and turn the WiFi LED ON if successful
3. Create a `Monitor` and start `loop_section()`

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
bash upload_to_esp32.sh 

### Reboot
mpremote connect /dev/ttyUSB0 reset
mpremote connect /dev/ttyUSB0 repl

---

### Notes about `bme280.py` in this repo

- The repository contains a BME280 driver (`bme280.py`) that supports both I2C (`BME280_I2C`) and SPI (`BME280_SPI`) interfaces and includes calibration/compensation routines. If you prefer a lighter stub for testing, the project also previously included a simple stub; replace or remove the stub if you want the full driver to run on the device.
- BME280 I2C addresses commonly used: `0x76` or `0x77`. If the sensor doesn't respond, try the alternate address.

### Resistors and wiring for LEDs and DS18B20

- LEDs: place a series resistor with each LED between the GPIO pin and the LED (or between LED and ground). Typical value: 220 Ω (safe default for 3.3 V GPIO). For example:

	GPIO --> 220Ω resistor --> LED anode
	LED cathode --> GND

	Use one resistor per LED; do not share resistors across multiple LEDs unless intentionally designing a multiplex.

- DS18B20 (1-wire): the 1-wire data line must be pulled up to 3.3 V with a resistor. Recommended value: 4.7 kΩ between DATA and 3.3 V. If you have multiple DS18B20 devices on one bus, one pull-up resistor shared by the bus is correct.

### Pressure ranges (BME280)

- Sensor operating/valid range (use for validation): 300–1100 hPa
- Typical ground-level weather: ~980–1030 hPa
- Recommended dashboard range (adjust to your site): 900–1100 hPa (broad) or 950–1050 hPa (tight)

If you'd like, I can update the README with a short wiring diagram (ASCII art) for the ESP32 -> sensors/LEDs, or add a short `try-it` section showing how to run the project with `mpremote`.

