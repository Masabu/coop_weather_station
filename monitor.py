import machine

import time
import random
import urequests
from time import sleep
import onewire
import ds18x20
from utilities import Led_Toggle
from machine import Pin, I2C
from bme280 import BME280_I2C

class Monitor:

    def __init__(self, AUTH, log=None):
        # Track last reboot time for scheduled reboot logic
        self._last_reboot_time = time.time()
        self.ds_sensor_init = False
        self.bme_init = False
        self.log = log if log is not None else {}

        ds_pin = 5  # default to Pin 5 if not specified

        if isinstance(ds_pin, int):
            ds_pin = Pin(ds_pin)
        self._init_ds18(ds_pin)
        self._init_i2c_and_bme()
        self._init_blynk(AUTH)

    def _init_ds18(self, ds_pin):
        """Initialize DS18B20 sensor bus and LEDs, with retries."""
        self.ds_pin = ds_pin
        self.roms = []
        for attempt in range(3):
            try:
                self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
                self.roms = self.ds_sensor.scan()
                print(f'DS18B20: Found {len(self.roms)} sensor(s) (attempt {attempt+1})')
                Led_Toggle(22, "ON")
                self.ds_sensor_init = True
                if len(self.roms) > 0:
                    break
            except Exception as e:
                print(f'DS18B20 init failed (attempt {attempt+1}):', e)
            if attempt < 2:
                print('Retrying DS18B20 initialization in 2 seconds...')
                sleep(2)

        if len(self.roms) == 2:
            print("2 DS18B20 sensors found!")
            Led_Toggle(22, "ON")  # orange light at D22 Pin22

        self.log['ds18b20'] = {
            'init': self.ds_sensor_init,
            'sensors': len(self.roms),
            'devices': self.roms.copy(),
            'attempts': attempt+1,
            'addresses': [rom.hex() for rom in self.roms]
        }

    def _init_i2c_and_bme(self):
        """Initialize I2C bus, detect devices and create a BME280 instance, with retries."""
        # Using SCL=Pin(26), SDA=Pin(25)
        i2c = I2C(0, scl=Pin(26), sda=Pin(25), freq=400000)

        # Scan for devices (should show 0x76 or 0x77)
        self.devices = i2c.scan()
        print("I2C devices found:", [hex(addr) for addr in self.devices])

        if len(self.devices) == 1:
            # indicate an I2C device was found
            Led_Toggle(27, "ON")
            self.bme_addr = hex(self.devices[0])

        # Try to initialize BME280 up to 3 times
        self.bme = None

        for attempt in range(3):
            try:
                self.bme = BME280_I2C(i2c, address=0x77)
                print(f"✓ BME280 initialized on I2C! (attempt {attempt+1})")
                self.bme_init = True
                break
            except Exception as e:
                print(f"BME280 init failed (attempt {attempt+1}):", e)
                self.bme = None
                if attempt < 2:
                    print("Retrying BME280 initialization in 2 seconds...")
                    sleep(2)
        self.log['bme280'] = {
            'init': self.bme_init,
            'devices': self.devices.copy(),
            'attempts': attempt+1
        }

    def maybe_reboot(self, reboot_interval_sec=86400):
        """
        Reboot the ESP32 if uptime exceeds reboot_interval_sec (default: 1 day).
        Call this periodically from your main loop.
        """
        now = time.time()
        if now - self._last_reboot_time > reboot_interval_sec:
            print("[Monitor] Rebooting system after scheduled interval...")
            machine.reset()

    def _init_blynk(self, AUTH):
        """Set Blynk configuration values."""
        self.BLYNK_AUTH = AUTH
        self.BLYNK_URL = "http://blynk.cloud/external/api/batch/update"


    def send_to_blynk(self, data):
        """Send a dict of virtual-pin -> value pairs to Blynk in one API call.

        `data` can be a dict like {'V0': 23.5, 'V1': 24.1} or {0: 23.5, '1': 24.1}.
        The method will normalise keys to the 'Vn' format.
        """
        try:
            parts = [f"token={self.BLYNK_AUTH}"]
            for k, v in data.items():
                # Normalise key: allow 0 or '0' or 'V0' formats
                if isinstance(k, int) or (isinstance(k, str) and k.isdigit()):
                    key = f"V{int(k)}"
                else:
                    key = str(k)
                    if not key.upper().startswith('V'):
                        key = 'V' + key
                parts.append(f"{key}={v}")

            query = '?' + '&'.join(parts)
            self.url = self.BLYNK_URL + query
            response = urequests.get(self.url)
            try:
                print('Blynk response:', response.status_code)
                print('URL sent:', self.url)
            finally:
                response.close()
            return True
        except Exception as e:
            print('Error sending to Blynk:', e)
            return False

    # --- modular sensor read methods ----------------------------------
    def read_ds(self):
        """Read DS18B20 sensors and return a list of temperatures.

        Returns a list like [temp1, temp2] (may have 0..N values).
        """
        try:
            self.ds_sensor.convert_temp()
            sleep(0.75)
            temps = []
            for rom in self.roms:
                try:
                    temps.append(self.ds_sensor.read_temp(rom))
                except Exception as e:
                    print('ds read error:', e)
                    temps.append(None)
            return temps
        except Exception as e:
            print('ds convert/read error:', e)
            return []

    def read_bme(self):
        """Read BME sensor and return (temp, pressure, humidity) or None if unavailable."""
        if getattr(self, 'bme', None) is None:
            return None
        try:
            return self.bme.values
        except Exception as e:
            print('bme read error:', e)
            return None

    def read_all(self):
        """Read all sensors and return a dict mapping virtual pins to values.

        DS sensors -> V0, V1 (in order)
        BME sensors -> V2 (temp), V3 (pressure), V4 (humidity)
        """
        payload = {}
        ds_vals = self.read_ds()
        if ds_vals:
            # map first two (if present) to V0 and V1
            if len(ds_vals) >= 1 and ds_vals[0] is not None:
                payload['V0'] = ds_vals[0]
            if len(ds_vals) >= 2 and ds_vals[1] is not None:
                payload['V1'] = ds_vals[1]

        bme_vals = self.read_bme()
        if bme_vals is not None:
            try:
                t, p, h = bme_vals
                payload['V2'] = t
                payload['V3'] = p
                payload['V4'] = h
            except Exception:
                pass

        return payload

    def send_combined(self):
        """Read all sensors and send a single Blynk payload if any data present."""
        data = self.read_all()
        if not data:
            print('No sensor data to send')
            return False
        ok = self.send_to_blynk(data)
        return ok

    def led_blink(self, pin_num=23, times=5, interval=0.2):
        led = Pin(pin_num, Pin.OUT)
        for _ in range(times):
            led.on()
            sleep(interval)
            led.off()
            sleep(interval)

    def loop_section(self, wait_time=30):
        while True:
            ok = self.send_combined()
            if ok:
                # short blink on success
                self.led_blink(pin_num=23, times=5, interval=0.15)

                # send blink time of update
                import time

                t = time.localtime()  # (year, month, mday, hour, min, sec, wday, yday)
                timestamp = "{:04d}-{:02d}-{:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4])
                print(timestamp)
                self.send_to_blynk({"V5": f"'{timestamp}'","V6": f"{timestamp}"})

            # Check if it's time to reboot (default: once per 24h)
            self.maybe_reboot(reboot_interval_sec=86400)
            sleep(wait_time)


if __name__ == "__main__":
    try:
        from secret import BLYNK_AUTH_TOKEN
    except Exception:
        BLYNK_AUTH_TOKEN = ''

    monitor = Monitor(AUTH=BLYNK_AUTH_TOKEN)
    monitor.loop_section(wait_time=60)





