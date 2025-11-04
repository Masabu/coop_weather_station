
# coop_weather_station
Chicken coop weather station

## Hardware
* Two DS18B20 temperature sensors, both attached at Pin 5.
* LED Pin 2   : WiFi status (green)
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

`monitor.py` provides the `Monitor` class, which centralizes sensor reads, Blynk uploads, and system diagnostics. The class is modular, robust, and supports centralized logging.

### Monitor class methods

- `__init__(self, AUTH, log=None)`
	- Initializes DS18B20, BME280, and Blynk. Accepts a log dictionary for diagnostics.
- `_init_ds18(self, ds_pin)`
	- Sets up the DS18B20 one-wire bus and logs sensor status.
- `_init_i2c_and_bme(self)`
	- Scans I2C and initializes BME280 (if present), with retries and logging.
- `_init_blynk(self, AUTH)`
	- Stores Blynk endpoint and token.
- `maybe_reboot(self, reboot_interval_sec=86400)`
	- Reboots the ESP32 if uptime exceeds the interval (default: 1 day).
- `send_to_blynk(self, data)`
	- Sends a dict of virtual-pin → value pairs to Blynk in one API call.
- `read_ds(self)`
	- Reads DS18B20 sensors and returns a list of temperatures.
- `read_bme(self)`
	- Reads the BME280 and returns (temp, pressure, humidity) or None.
- `read_all(self)`
	- Reads all sensors and returns a dict mapping virtual pins to values.
- `send_combined(self)`
	- Reads all sensors and sends a single Blynk payload if any data present.
- `led_blink(self, pin_num=23, times=5, interval=0.2)`
	- Blinks the specified LED for status indication.
- `loop_section(self, wait_time=30)`
	- Main loop: sends combined sensor data, blinks LED, and checks for scheduled reboot.

#### Behavior notes

- Combined payload: When at least one sensor returns a value, the monitor sends a single, combined Blynk request containing all available values, reducing API calls and network overhead.
- Empty payloads: If no sensors return values, `send_combined()` will not send data to Blynk (prints "No sensor data to send").
- BME initialization: If initialization fails, BME reads are skipped and logged.


## main.py Usage
`main.py` handles WiFi connection, time sync, LED status, and starts the monitoring loop.

Typical flow:
1. Blink all status LEDs at startup
2. Connect to WiFi using `connect_wifi` (with logging)
3. Sync time to NTP and set Chicago time using `sync_time_chicago`
4. Create a `Monitor` and start `loop_section()`

Example:
```python
from monitor import Monitor
from secret import BLYNK_AUTH_TOKEN
from utilities import connect_wifi, sync_time_chicago

log = {}
connect_wifi([SSID1, SSID2], [PASSWORD, PASSWORD], log=log)
sync_time_chicago(log)
probe = Monitor(AUTH=BLYNK_AUTH_TOKEN, log=log)
probe.loop_section(wait_time=180)
```


## utilities.py functions/classes

- `sync_time_chicago(log)`
	- Syncs time from NTP and sets local time to Chicago (UTC-6), logging results and formatted local time string.
- `connect_wifi(ssid_list, password_list, max_attempts=10, log=None)`
	- Connects to WiFi, tries multiple SSIDs, logs status and IP.
- `Led_Toggle(pin_num, status)`
	- Turns an LED ON or OFF.
- `led_blink(pin_num=23, times=5, interval=0.2)`
	- Blinks an LED for status indication.
- `Weather(latitude, longitude, timezone="America/Chicago", forecast_days=3)`
	- Class for fetching and parsing weather forecasts from Open-Meteo.
		- `get_weather_forecast()`
		- `weather_code_to_condition(code)`
		- `send_weather_summary_to_blynk(monitor, weather_summary)`
		- `print_daily_forecast(weather_data)`

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

