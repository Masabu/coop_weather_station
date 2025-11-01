
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
    def __init__(self, AUTH):
        # Initialize components via small helper methods to keep __init__ tidy
        # allow ds_pin to be an int or a Pin instance

        ds_pin = 5  # default to Pin 5 if not specified

        if isinstance(ds_pin, int):
            ds_pin = Pin(ds_pin)
        self._init_ds18(ds_pin)
        self._init_i2c_and_bme()
        self._init_blynk(AUTH)

    def _init_ds18(self, ds_pin):
        """Initialize DS18B20 sensor bus and LEDs."""
        self.ds_pin = ds_pin
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.roms = self.ds_sensor.scan()
        print(f'Found {len(self.roms)} sensor(s)')

        if len(self.roms) == 2:
            print("2 DS18B20 sensors found!")
            Led_Toggle(22, "ON")  # orange light at D22 Pin22

    def _init_i2c_and_bme(self):
        """Initialize I2C bus, detect devices and create a BME280 instance."""
        # Using SCL=Pin(26), SDA=Pin(25)
        i2c = I2C(0, scl=Pin(26), sda=Pin(25), freq=400000)

        # Scan for devices (should show 0x76 or 0x77)
        self.devices = i2c.scan()
        print("I2C devices found:", [hex(addr) for addr in self.devices])

        if len(self.devices) == 1:
            # indicate an I2C device was found
            Led_Toggle(27, "ON")

        # Initialize BME280 (may raise if device not present)
        try:
            self.bme = BME280_I2C(i2c, address=0x77)
            print("✓ BME280 initialized on I2C!")
        except Exception as e:
            print("BME280 init failed:", e)
            self.bme = None

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
            sleep(wait_time)


if __name__ == "__main__":
    try:
        from secret import BLYNK_AUTH_TOKEN
    except Exception:
        BLYNK_AUTH_TOKEN = ''

    monitor = Monitor(ds_pin=5, AUTH=BLYNK_AUTH_TOKEN)
    monitor.loop_section(wait_time=60)





